import requests
from bs4 import BeautifulSoup
import re
from transformers import pipeline

# Initialize FinBERT pipeline. 
# device=-1 forces it to run on your CPU, saving your GPU VRAM for Llama 3.1.
print("Loading FinBERT into CPU memory...")
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert", device=-1)

def scrape_fed_minutes(url):
    """Scrapes and cleans the text from a Federal Reserve FOMC minutes page."""
    print(f"Scraping FOMC data from: {url}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Failed to retrieve data. Status Code: {response.status_code}"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        raw_text = ' '.join([p.get_text() for p in paragraphs])
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        return clean_text
    except Exception as e:
        return f"Error scraping URL: {e}"

def get_fomc_sentiment_vector():
    """Scrapes the most recent FOMC minutes and returns a numerical sentiment score."""
    url = "https://www.federalreserve.gov/monetarypolicy/fomcminutes20260318.htm"
    text = scrape_fed_minutes(url)
    
    if text.startswith("Error") or text.startswith("Failed"):
        return text

    print("Slicing text and running FinBERT sentiment analysis...\n")
    
    # Reduced to 250 words to stay well under the 512-token limit
    words = text.split()
    chunks = [' '.join(words[i:i + 250]) for i in range(0, len(words), 250)]
    
    total_score = 0.0
    valid_chunks = 0
    
    for chunk in chunks:
        if len(chunk.strip()) < 20:
            continue
            
        # Added truncation=True to prevent tensor size mismatch errors
        result = sentiment_analyzer(chunk, truncation=True)[0]
        label = result['label']
        score = result['score']
        
        vector = score if label == "positive" else (-score if label == "negative" else 0.0)
            
        total_score += vector
        valid_chunks += 1
        
    final_sentiment = total_score / valid_chunks if valid_chunks > 0 else 0
    
    print("--- SENTIMENT VECTOR ANALYSIS ---")
    print(f"Total Chunks Analyzed: {valid_chunks}")
    print(f"Raw Vector Score: {final_sentiment:.3f} (-1.0 to +1.0)")
    
    verdict = "Neutral"
    if final_sentiment > 0.15: verdict = "Dovish / Accommodative"
    elif final_sentiment < -0.15: verdict = "Hawkish / Restrictive"
        
    print(f"Agent Verdict: {verdict}")
    return f"FOMC Sentiment Score: {final_sentiment:.3f}. Verdict: {verdict}"

if __name__ == "__main__":
    get_fomc_sentiment_vector()