import sqlite3

def calculate_kelly_criterion():
    """Reads closed trades from the database and calculates optimal position sizing."""
    
    print("Connecting to local trade database to calculate edge...\n")
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT result FROM trades WHERE status = 'Closed'")
    trades = cursor.fetchall()
    conn.close()
    
    if not trades or len(trades) < 5:
        verdict = "Not enough trade history to calculate edge. Defaulting to strict 1% risk per trade."
        print(f"[SYSTEM] {verdict}")
        return verdict
        
    # Extract results
    results = [t[0] for t in trades]
    wins = [r for r in results if r > 0]
    losses = [abs(r) for r in results if r < 0] # Use absolute value for loss math
    
    win_rate = len(wins) / len(results)
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    
    # Calculate Win/Loss Ratio
    wl_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')
    
    # Calculate Kelly Percentage
    if wl_ratio > 0 and wl_ratio != float('inf'):
        kelly_pct = win_rate - ((1 - win_rate) / wl_ratio)
    else:
        kelly_pct = 0.0
        
    # Apply Half-Kelly
    fractional_kelly = max(0, (kelly_pct / 2))
    
    # NEW: Capital Constraint Logic
    portfolio_balance = 22000.00
    hard_cap_pct = 0.05 # 5% maximum
    
    # The agent must take the lesser of the Kelly recommendation or the hard cap
    final_allocation_pct = min(fractional_kelly, hard_cap_pct)
    max_capital_risk = portfolio_balance * final_allocation_pct
    
    print("--- RISK METRICS ---")
    print(f"Historical Win Rate: {win_rate * 100:.1f}%")
    print(f"Calculated Half-Kelly: {fractional_kelly * 100:.2f}%")
    
    verdict = f"Maximum capital allocation capped at {final_allocation_pct * 100:.2f}% of portfolio. Do not exceed ${max_capital_risk:.2f} in required margin/collateral for this trade."
        
    print(f"System Verdict: {verdict}\n")
    return verdict

if __name__ == "__main__":
    calculate_kelly_criterion()