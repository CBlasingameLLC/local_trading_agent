import yfinance as yf
import pandas as pd

def get_directional_swing_setup(ticker_symbol: str):
    """
    Analyzes moving averages and price action to recommend directional swing trades
    (e.g., Debit Spreads, outright shares). 
    CRITICAL INSTRUCTION: ticker_symbol MUST be a capitalized stock ticker (e.g., 'AAPL').
    Use this ONLY when the user explicitly asks for a directional, swing, or tactical setup.
    DO NOT use this for delta-neutral or premium selling inquiries.
    """
    print(f"Activating Brain B (Tactical Allocator): Analyzing {ticker_symbol}...\n")
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1y")
        
        if hist.empty:
            return f"Error: Could not retrieve price history for {ticker_symbol}."
            
        current_price = hist['Close'].iloc[-1]
        
        # Calculate key technical moving averages
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        print(f"--- TECHNICAL ALIGNMENT FOR {ticker_symbol} ---")
        print(f"Current Price:  ${current_price:.2f}")
        print(f"20-Day SMA:     ${sma_20:.2f} (Short-term momentum)")
        print(f"50-Day SMA:     ${sma_50:.2f} (Mid-term trend)")
        print(f"200-Day SMA:    ${sma_200:.2f} (Macro trend)\n")
        
        # Directional Logic Tree
        if current_price > sma_20 and sma_20 > sma_50 and sma_50 > sma_200:
            trend = "Strong Bullish (Full Alignment)"
            recommendation = "Bull Call Debit Spreads or Long Equity. Momentum and macro trend are synchronized upward."
        elif current_price < sma_20 and sma_20 < sma_50 and sma_50 < sma_200:
            trend = "Strong Bearish (Full Alignment)"
            recommendation = "Bear Put Debit Spreads or Short Equity. Total trend breakdown detected."
        elif current_price > sma_200 and current_price < sma_50:
            trend = "Macro Bullish / Short-Term Pullback"
            recommendation = "Wait for price to reclaim the 50-day SMA before initiating long swing trades. Watch for support bounces."
        elif current_price < sma_200 and current_price > sma_50:
            trend = "Macro Bearish / Bear Market Rally"
            recommendation = "High risk of rejection at the 200-day SMA. Avoid heavy long exposure; look for short setups near resistance."
        else:
            trend = "Choppy / Range-Bound"
            recommendation = "No directional edge. Avoid Debit Spreads. Revert to Brain A (Delta-Neutral/Iron Condors) if IV is high."
            
        verdict = f"Trend: {trend}. Tactical Recommendation: {recommendation}"
        print(f"System Verdict: {verdict}\n")
        
        return f"{ticker_symbol} Directional Analysis - {verdict}"

    except Exception as e:
        return f"Error analyzing directional setup for {ticker_symbol}: {e}"

if __name__ == "__main__":
    # Test on a highly liquid stock
    get_directional_swing_setup("AAPL")

def get_quantitative_metrics(ticker_symbol: str) -> dict:
    """Returns raw numerical data for the automated trading loop."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1y")
        
        if hist.empty:
            return {"current_price": 0.0, "is_bullish_aligned": False}
            
        close = hist['Close']
        current_price = close.iloc[-1]
        sma_20 = close.rolling(window=20).mean().iloc[-1]
        sma_50 = close.rolling(window=50).mean().iloc[-1]
        sma_200 = close.rolling(window=200).mean().iloc[-1]
        
        # True if price is cascading upwards across all timeframes
        is_bullish_aligned = current_price > sma_20 and sma_20 > sma_50 and sma_50 > sma_200
        
        return {
            "current_price": current_price,
            "is_bullish_aligned": is_bullish_aligned
        }
    except Exception as e:
        print(f"Metrics error for {ticker_symbol}: {e}")
        return {"current_price": 0.0, "is_bullish_aligned": False}