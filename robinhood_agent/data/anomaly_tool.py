import yfinance as yf
import pandas as pd
from sklearn.ensemble import IsolationForest
import warnings

# Suppress standard sklearn warnings to keep the terminal output clean for the LLM
warnings.filterwarnings('ignore')

def get_market_anomaly(ticker_symbol="^GSPC"):
    print(f"Pulling historical data for {ticker_symbol}...")
    
    try:
        data = yf.download(ticker_symbol, start="2000-01-01", progress=False)
        
        # FIX: Flatten MultiIndex columns if they exist
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if data.empty:
            return "Failed to download historical data."

        # Engineering features
        data['Return'] = data['Close'].pct_change()
        data['Volatility'] = data['Return'].rolling(window=5).std()
        data['Volume_Spike'] = data['Volume'].pct_change()
        
        # Now dropna will find the keys correctly
        df_clean = data.dropna(subset=['Return', 'Volatility', 'Volume_Spike']).copy()
        
        # ... [Rest of your Isolation Forest logic remains the same] ...
        
        features = df_clean[['Return', 'Volatility', 'Volume_Spike']]
        model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        df_clean['Anomaly_Score'] = model.fit_predict(features)
        
        latest_data = df_clean.iloc[-1]
        is_anomaly = latest_data['Anomaly_Score'] == -1
        
        verdict = "🚨 BLACK SWAN PROFILE" if is_anomaly else "✅ Normal Market Action"
        return f"Market Anomaly Status: {verdict}"

    except Exception as e:
        return f"Error running anomaly detection: {e}"

if __name__ == "__main__":
    # Test the model on the S&P 500
    get_market_anomaly("^GSPC")