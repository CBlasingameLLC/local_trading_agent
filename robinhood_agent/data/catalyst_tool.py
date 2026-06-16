import yfinance as yf
from transformers import pipeline

# Load the FinBERT model into CPU memory
print("Loading FinBERT for Catalyst Screening...")
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert", device=-1)

def analyze_premarket_catalyst(ticker_symbol: str):
    """
    Pulls the latest news headlines for a given ticker and analyzes the sentiment 
    to determine if there is a fundamental catalyst driving pre-market volume.
    """
    print(f"Scanning news wires for {ticker_symbol} catalysts...\n")
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        
        if not news:
            return f"No recent news found for {ticker_symbol}. Volume may be technical noise."
            
        headlines = [item['title'] for item in news[:5]] # Grab top 5 recent headlines
        
        total_score = 0
        print("--- CATALYST HEADLINES ---")
        for headline in headlines:
            result = sentiment_analyzer(headline, truncation=True)[0]
            label = result['label']
            score = result['score']
            
            vector = score if label == "positive" else (-score if label == "negative" else 0.0)
            total_score += vector
            
            print(f"[{label.upper()}] {headline}")
            
        avg_sentiment = total_score / len(headlines)
        
        if avg_sentiment > 0.3:
            verdict = "Bullish Catalyst Confirmed. Volume is supported by positive fundamental news."
        elif avg_sentiment < -0.3:
            verdict = "Bearish Catalyst Confirmed. Volume is supported by negative fundamental news."
        else:
            verdict = "No Structural Catalyst. News is neutral/mixed; volume is likely retail or algorithmic noise."
            
        print(f"\nSystem Verdict: {verdict}")
        return f"{ticker_symbol} Catalyst Analysis: Sentiment Score {avg_sentiment:.2f}. {verdict}"
        
    except Exception as e:
        return f"Error analyzing catalysts for {ticker_symbol}: {e}"

if __name__ == "__main__":
    analyze_premarket_catalyst("NVDA")

def get_raw_sentiment_score(ticker_symbol: str) -> float:
    """Returns the raw FinBERT sentiment float for the automated loop."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        if not news:
            return 0.0
            
        headlines = []
        for item in news[:5]:
            # Robustly extract the headline due to changing yfinance API structures
            title = item.get('title')
            # If 'title' isn't at the top level, check if it's nested under 'content'
            if not title and 'content' in item:
                title = item['content'].get('title')
            
            if title and isinstance(title, str):
                headlines.append(title)
                
        if not headlines:
            print(f"Could not parse any headlines for {ticker_symbol}.")
            return 0.0

        total_score = 0.0
        for headline in headlines:
            result = sentiment_analyzer(headline, truncation=True)[0]
            label = result['label']
            score = result['score']
            vector = score if label == "positive" else (-score if label == "negative" else 0.0)
            total_score += vector
            
        return total_score / len(headlines)
    except Exception as e:
        print(f"Sentiment error for {ticker_symbol}: {e}")
        return 0.0