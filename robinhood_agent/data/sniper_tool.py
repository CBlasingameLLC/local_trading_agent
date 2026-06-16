import yfinance as yf
import math
from datetime import datetime

def get_precision_strikes(ticker_symbol: str):
    """
    Pulls the options chain for a given ticker, targets an expiration ~45 days out, 
    and calculates the optimal 16-Delta (1 Standard Deviation) strikes for premium selling.
    CRITICAL INSTRUCTION: ticker_symbol MUST be a capitalized stock ticker (e.g., 'AAPL').
    """
    print(f"Targeting precision strikes for {ticker_symbol}...\n")
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        expirations = ticker.options
        
        if not expirations:
            return f"No options chain available for {ticker_symbol}."
        
        # Target an expiration closest to the 45-DTE quantitative standard
        today = datetime.today()
        target_dte = 45
        best_exp = expirations[0]
        min_diff = float('inf')
        actual_dte = 0
        
        for exp in expirations:
            exp_date = datetime.strptime(exp, '%Y-%m-%d')
            dte = (exp_date - today).days
            if abs(dte - target_dte) < min_diff and dte > 0:
                min_diff = abs(dte - target_dte)
                best_exp = exp
                actual_dte = dte
                
        print(f"Target Expiration Selected: {best_exp} ({actual_dte} DTE)")
        
        # Fetch the options chain
        chain = ticker.option_chain(best_exp)
        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        
        # Find ATM strikes to establish baseline Implied Volatility
        atm_call = chain.calls.iloc[(chain.calls['strike'] - current_price).abs().argsort()[:1]]
        atm_put = chain.puts.iloc[(chain.puts['strike'] - current_price).abs().argsort()[:1]]
        
        avg_iv = (atm_call['impliedVolatility'].values[0] + atm_put['impliedVolatility'].values[0]) / 2
        
        # Calculate the 1 Standard Deviation Expected Move
        expected_move = current_price * avg_iv * math.sqrt(actual_dte / 365.25)
        
        short_call_target = current_price + expected_move
        short_put_target = current_price - expected_move
        
        # Locate the actual tradable strikes closest to our mathematical targets
        short_call = chain.calls.iloc[(chain.calls['strike'] - short_call_target).abs().argsort()[:1]]
        short_put = chain.puts.iloc[(chain.puts['strike'] - short_put_target).abs().argsort()[:1]]
        
        call_strike = short_call['strike'].values[0]
        call_premium = short_call['lastPrice'].values[0]
        
        put_strike = short_put['strike'].values[0]
        put_premium = short_put['lastPrice'].values[0]
        
        total_credit = call_premium + put_premium
        
        print("\n--- PRECISION STRIKE TARGETS ---")
        print(f"Current Price: ${current_price:.2f}")
        print(f"Mathematical 1-SD Move: ±${expected_move:.2f}")
        print(f"Short Call Leg: {call_strike} Strike (Premium: ${call_premium:.2f})")
        print(f"Short Put Leg: {put_strike} Strike (Premium: ${put_premium:.2f})")
        print(f"Total Expected Credit: ${total_credit:.2f} per contract\n")
        
        return (f"Recommended 45-DTE Strikes for {ticker_symbol} ({best_exp}): "
                f"Sell {call_strike} Call, Sell {put_strike} Put. Total Expected Credit: ${total_credit:.2f}.")

    except Exception as e:
        return f"Error calculating strikes for {ticker_symbol}: {e}"

if __name__ == "__main__":
    # Test on a highly liquid ETF
    get_precision_strikes("SPY")