import yfinance as yf
import pandas as pd
import numpy as np

def generate_strategy_recommendation(ticker_symbol: str):
    """
    Analyzes a specific ticker to recommend an options strategy.
    CRITICAL INSTRUCTION: The ticker_symbol parameter MUST be a valid, capitalized stock ticker symbol. 
    If the user asks about an index or company by name, convert it (e.g., 'S&P 500' -> 'SPY', 'Apple' -> 'AAPL').
    """
    print(f"Agent analyzing strategy viability for {ticker_symbol}...\n")
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # 1. Fetch recent price data (6 months) to calculate moving averages
        hist = ticker.history(period="6mo")
        if hist.empty:
            return f"Error: Could not retrieve price history for {ticker_symbol}."
            
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        # 2. Fetch nearest options chain to calculate Expected Move
        expirations = ticker.options
        if not expirations:
            return f"No options data available for {ticker_symbol}."
            
        nearest_expiry = expirations[0]
        chain = ticker.option_chain(nearest_expiry)
        
        # Find ATM (At-The-Money) straddle price to approximate the expected move
        atm_call = chain.calls.iloc[(chain.calls['strike'] - current_price).abs().argsort()[:1]]
        atm_put = chain.puts.iloc[(chain.puts['strike'] - current_price).abs().argsort()[:1]]
        
        straddle_price = atm_call['lastPrice'].values[0] + atm_put['lastPrice'].values[0]
        expected_move_pct = (straddle_price / current_price) * 100
        
        # 3. Strategy Logic / Decision Tree
        trend = "Bullish" if current_price > sma_50 else "Bearish"
        if expected_move_pct > 5.0:
            volatility_state = "High"
        elif expected_move_pct < 2.5:
            volatility_state = "Low"
        else:
            volatility_state = "Moderate"
            
        # Strict Delta-Neutral Recommendation Matrix
        if volatility_state == "High" and trend == "Bullish":
            recommendation = "Cash-Secured Put (The Wheel). IV is elevated and trend supports accumulation. Sell the 16-Delta strike."
        elif volatility_state == "High" and trend == "Bearish":
            recommendation = "Short Strangle or Iron Condor. IV Rank is sufficiently high to absorb directional risk. Structure for delta-neutrality."
        elif volatility_state == "Low":
            recommendation = "NO-GO. Implied Volatility is too low to safely harvest premium. Stay in cash and wait for IV expansion. DO NOT buy directional options."
        else:
            recommendation = "45-DTE Iron Condor. Volatility is moderate. Sell the 16-Delta wings and set an automatic GTC order for 50% max profit."
            
        print(f"--- {ticker_symbol.upper()} ANALYSIS ---")
        print(f"Price: ${current_price:.2f}")
        print(f"Trend (50 SMA): {trend}")
        print(f"Implied Expected Move: {expected_move_pct:.2f}%")
        print(f"Recommendation: {recommendation}\n")
        
        return f"{ticker_symbol} Analysis - Trend: {trend}, Expected Move: {expected_move_pct:.2f}%. Recommended Strategy: {recommendation}"

    except Exception as e:
        return f"Error analyzing {ticker_symbol}: {e}"

if __name__ == "__main__":
    # Test the logic on a high-volume stock
    generate_strategy_recommendation("TSLA")