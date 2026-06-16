import sqlite3
import datetime

def log_new_trade():
    """Interactive command-line tool to log trades into the SQLite database."""
    print("--- 📝 TRADE LOGGING INTERFACE ---\n")
    
    ticker = input("Ticker Symbol (e.g., AAPL): ").upper()
    strategy = input("Strategy (e.g., Iron Condor, Strangle, The Wheel): ")
    credit = float(input("Total Credit Received ($): "))
    
    # Check if the trade is open or closed
    status = input("Is this trade Closed? (Y/N): ").upper()
    
    if status == 'Y':
        result = float(input("Final P/L (Use negative for loss, e.g., -150 or 200): "))
        trade_status = 'Closed'
    else:
        result = 0.0
        trade_status = 'Open'
        
    date = datetime.date.today().strftime('%Y-%m-%d')
    
    # Connect and insert
    try:
        conn = sqlite3.connect('trading_journal.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (ticker, strategy, entry_date, credit_received, result, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, strategy, date, credit, result, trade_status))
        
        conn.commit()
        conn.close()
        print(f"\n✅ Successfully logged {strategy} on {ticker}.")
    except Exception as e:
        print(f"\n❌ Database Error: {e}")

if __name__ == "__main__":
    log_new_trade()