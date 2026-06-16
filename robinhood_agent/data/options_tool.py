import yfinance as yf
import pandas as pd

def get_atm_options(ticker_symbol):
    print(f"Connecting to market data for {ticker_symbol}...\n")
    ticker = yf.Ticker(ticker_symbol)
    
    # Get current stock price
    current_price = ticker.info.get('regularMarketPrice', ticker.info.get('currentPrice'))
    if current_price is None:
         return "Could not retrieve current price."
        
    print(f"Current Price of {ticker_symbol}: ${current_price:.2f}")
    
    # Get expiration dates
    expirations = ticker.options
    if not expirations:
        return f"No options data found for {ticker_symbol}."
    
    nearest_expiry = expirations[0]
    print(f"Nearest Expiration: {nearest_expiry}\n")
    
    # Fetch the options chain for that date
    chain = ticker.option_chain(nearest_expiry)
    calls = chain.calls
    puts = chain.puts
    
    # Filter for options closest to the current price (At-The-Money)
    # We will grab 2 strikes below and 2 strikes above
    atm_calls = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:4]]
    atm_puts = puts.iloc[(puts['strike'] - current_price).abs().argsort()[:4]]
    
    print("--- ATM CALLS ---")
    print(atm_calls[['strike', 'lastPrice', 'impliedVolatility', 'openInterest']].to_string(index=False))
    
    print("\n--- ATM PUTS ---")
    print(atm_puts[['strike', 'lastPrice', 'impliedVolatility', 'openInterest']].to_string(index=False))

if __name__ == "__main__":
    # Testing the tool on the S&P 500 ETF
    get_atm_options("SPY")