import sqlite3

def init_db():
    """Initializes the local database and creates the trades table."""
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    
    # Create a table for trade logging
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            strategy TEXT,
            entry_date TEXT,
            credit_received REAL,
            result REAL, -- Profit/Loss
            status TEXT -- 'Open' or 'Closed'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def log_trade(ticker, strategy, credit):
    """Adds a new trade entry to the database."""
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (ticker, strategy, entry_date, credit_received, status)
        VALUES (?, ?, date('now'), ?, 'Open')
    ''', (ticker, strategy, credit))
    conn.commit()
    conn.close()
    return f"Successfully logged {strategy} on {ticker}."

if __name__ == "__main__":
    init_db()