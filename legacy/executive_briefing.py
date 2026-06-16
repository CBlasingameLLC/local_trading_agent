import ollama
from regime_tool import get_market_regime
from sentiment_tool import get_fomc_sentiment_vector
from anomaly_tool import get_market_anomaly
from risk_tool import calculate_kelly_criterion

def run_morning_briefing():
    print("🚀 Initializing Autonomous Executive Loop...\n")
    
    # 1. Gather all data points autonomously
    regime = get_market_regime()
    sentiment = get_fomc_sentiment_vector()
    anomaly = get_market_anomaly()
    risk_sizing = calculate_kelly_criterion()
    
    # 2. Construct the "Master Context"
    # This is where we feed all the mathematical outputs into the LLM
    master_prompt = f"""
    You are the Chief Risk Officer for a delta-neutral options trader. 
    Analyze the following data and provide a concise, professional daily briefing.
    
    DATA INPUTS:
    - Market Regime: {regime}
    - Fed Sentiment: {sentiment}
    - Anomaly Detection: {anomaly}
    - Risk Allocation: {risk_sizing}
    
    TASK:
    1. Determine the 'Environmental Bias' (Bullish, Bearish, or Neutral).
    2. Suggest the best strategy for today (e.g., The Wheel, Iron Condors, or Cash).
    3. Highlight any critical risks or anomalies.
    """
    
    print("Synthesizing final briefing with Llama 3.1...\n")
    
    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': master_prompt}]
    )
    
    print("--- DAILY EXECUTIVE BRIEFING ---")
    print(response['message']['content'])

if __name__ == "__main__":
    run_morning_briefing()