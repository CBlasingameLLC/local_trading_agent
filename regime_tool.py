import yfinance as yf

def get_market_regime():
    """Fetches the VIX and 10-Year Yield to classify the market state."""
    print("Agent is pulling macroeconomic indicators...\n")
    
    try:
        # Fetch VIX (Volatility Index)
        vix = yf.Ticker("^VIX")
        vix_price = vix.history(period="1d")['Close'].iloc[-1]
        
        # Fetch 10-Year Treasury Yield
        tnx = yf.Ticker("^TNX")
        tnx_yield = tnx.history(period="1d")['Close'].iloc[-1]
        
        print(f"Current VIX: {vix_price:.2f}")
        print(f"10-Year Yield: {tnx_yield:.2f}%\n")
        
        # Baseline Classification Logic
        if vix_price > 25:
            regime = "High Volatility / Crashing (Reduce sizing, favor defined risk)"
        elif vix_price < 15:
            regime = "Low Volatility / Complacent (Avoid premium selling)"
        else:
            regime = "Mean-Reverting (Optimal for Theta strategies and The Wheel)"
            
        print(f"[SYSTEM] Detected Market Regime: {regime}")
        
        # Return the data so the LLM can read it
        return f"VIX is {vix_price:.2f}, 10-Year Yield is {tnx_yield:.2f}%. Regime: {regime}"
        
    except Exception as e:
        return f"Error fetching regime data: {e}"

if __name__ == "__main__":
    get_market_regime()