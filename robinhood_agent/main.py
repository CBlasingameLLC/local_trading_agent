import asyncio
import os
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncioScheduler
from execution.robinhood_mcp import establish_connection, execute_trade
from strategies.equity_bullish import BullishStrategyEngine

# Define a tight watchlist focused on high-liquidity momentum equities
WATCHLIST = ["AAPL", "NVDA", "AMD", "TSLA", "MSFT"]

# Initialize components
strategy = BullishStrategyEngine(max_position_risk_pct=0.10, total_budget=500.00)
scheduler = AsyncioScheduler(timezone=timezone('US/Eastern'))

async def fetch_live_market_metrics(ticker: str) -> tuple:
    """
    Mock pipeline interface. 
    Replace these values with calls to your root scripts:
    e.g., directional_tool.get_rsi(ticker) & sentiment_tool.get_score(ticker)
    """
    # Placeholder mapping to emulate a live scan match for demonstration
    if ticker == "NVDA":
        mock_market_data = {"rsi": 45.5, "macd_bullish": True, "current_price": 125.00}
        mock_sentiment = 0.65
    else:
        mock_market_data = {"rsi": 72.0, "macd_bullish": False, "current_price": 180.00}
        mock_sentiment = 0.10
        
    return mock_market_data, mock_sentiment

async def market_execution_loop():
    """
    The core routine that executes on every scheduler interval.
    Sweeps the watchlist, evaluates metrics, and routes executions to the MCP server.
    """
    print("\n⏰ Market interval triggered. Initializing scan...")
    
    # 1. Spin up the secure connection to Robinhood
    # The stdio bridge context closes out upon block exit, keeping sessions highly secure
    async def run_scan(session):
        for ticker in WATCHLIST:
            # Pull metrics from your analytical tools
            market_data, sentiment_score = await fetch_live_market_metrics(ticker)
            
            # Pass data through the $500 risk boundaries
            signal = strategy.evaluate_signals(ticker, market_data, sentiment_score)
            
            if signal["action"] == "BUY":
                print(f"🎯 Execution Alert: {signal['reason']}")
                await execute_trade(
                    session=session,
                    ticker=signal["ticker"],
                    limit_price=signal["limit_price"],
                    quantity=signal["quantity"]
                )
            else:
                print(f"横 {ticker}: {signal['reason']}")

    # Import the connection engine parameters from your execution file
    from mcp.client.stdio import stdio_client
    from mcp import ClientSession
    from execution.robinhood_mcp import SERVER_PARAMS

    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await run_scan(session)
    except Exception as e:
        print(f"❌ Execution loop failed to connect to MCP: {e}")

async def main():
    print("--- 🚀 STARTING Persistant TRADING SYSTEM 🚀 ---")
    
    # Schedule the loop to execute every 15 minutes, Monday-Friday, during standard market hours (9 AM - 4 PM)
    scheduler.add_job(
        market_execution_loop,
        'cron',
        day_of_week='mon-fri',
        hour='9-15',
        minute='*/15'
    )
    
    # Start the background execution clock
    scheduler.start()
    print("⏰ Core Scheduler Active. Monitoring market hours window (EST)...")
    
    # For a quick manual test inside your terminal immediately upon booting, 
    # we force a one-off execution run right now without waiting for the next 15-minute mark:
    await market_execution_loop()

    # Keep the main script alive so the background scheduler can continue running indefinitely
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 System safely shut down.")