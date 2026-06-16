import ollama
from options_tool import get_atm_options
from regime_tool import get_market_regime
from sentiment_tool import get_fomc_sentiment_vector
from anomaly_tool import get_market_anomaly
from risk_tool import calculate_kelly_criterion
from strategy_tool import generate_strategy_recommendation
from catalyst_tool import analyze_premarket_catalyst
from sniper_tool import get_precision_strikes
from directional_tool import get_directional_swing_setup

def agent_router(user_prompt):
    print("Agent is thinking...\n")
    
    # Providing Llama 3.1 with the full suite of current tools
    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': user_prompt}],
        tools=[get_atm_options, get_market_regime, get_fomc_sentiment_vector, get_market_anomaly, calculate_kelly_criterion, generate_strategy_recommendation, analyze_premarket_catalyst, get_precision_strikes, get_directional_swing_setup],
    )

    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            t_name = tool.function.name
            
            if t_name == 'get_atm_options':
                ticker = tool.function.arguments.get('ticker_symbol')
                print(f"[SYSTEM] Fetching options data for: {ticker}\n")
                get_atm_options(ticker)
                
            elif t_name == 'get_market_regime':
                print("[SYSTEM] Classifying market regime...\n")
                get_market_regime()
                
            elif t_name == 'get_fomc_sentiment_vector':
                print("[SYSTEM] Analyzing Fed sentiment...\n")
                result = get_fomc_sentiment_vector()
                # We feed the numerical result back to the LLM for a final summary
                print(f"\nFinal Analysis: {result}")

            elif t_name == 'get_market_anomaly':
                print("[SYSTEM] Running Isolation Forest on historical data...\n")
                result = get_market_anomaly()
                print(f"\nFinal Analysis: {result}")

            elif t_name == 'calculate_kelly_criterion':
             print("[SYSTEM] Calculating Kelly Criterion based on trade history...\n")
             result = calculate_kelly_criterion()
             print(f"\nFinal Analysis: {result}")

            elif t_name == 'generate_strategy_recommendation':
                ticker = tool.function.arguments.get('ticker_symbol')
                print(f"[SYSTEM] Generating options strategy for: {ticker}\n")
                result = generate_strategy_recommendation(ticker)
                print(f"\nFinal Analysis: {result}")

            elif t_name == 'analyze_premarket_catalyst':
                ticker = tool.function.arguments.get('ticker_symbol')
                print(f"[SYSTEM] Analyzing pre-market catalysts for: {ticker}\n")
                result = analyze_premarket_catalyst(ticker)
                print(f"\nFinal Analysis: {result}")
            
            elif t_name == 'get_precision_strikes':
                ticker = tool.function.arguments.get('ticker_symbol')
                print(f"[SYSTEM] Calculating precision strike targets for: {ticker}\n")
                result = get_precision_strikes(ticker)
                print(f"\nFinal Analysis: {result}")

            elif t_name == 'get_directional_swing_setup':
                ticker = tool.function.arguments.get('ticker_symbol')
                print(f"[SYSTEM] Analyzing directional swing setup for: {ticker}\n")
                result = get_directional_swing_setup(ticker)
                print(f"\nFinal Analysis: {result}")
    else:
        print(response.message.content)

if __name__ == "__main__":
    print("==================================================")
    print(" QUANTITATIVE AI AGENT INITIALIZED (Llama 3.1)    ")
    print(" Type 'exit' or 'quit' to close the terminal.     ")
    print("==================================================\n")
    
    while True:
        # This creates a persistent input prompt waiting for your command
        user_input = input("Commander: ")
        
        # Safe exit strategy
        if user_input.strip().lower() in ['exit', 'quit']:
            print("Shutting down agent...")
            break
            
        # Ignore empty presses of the Enter key
        if not user_input.strip():
            continue
            
        # Send your prompt into the routing logic
        agent_router(user_input)
        print("\n" + "-"*50 + "\n")