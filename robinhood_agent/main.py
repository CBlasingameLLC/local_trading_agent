import asyncio
from execution.robinhood_mcp import establish_connection, execute_trade

async def run_system_check():
    print("--- BOOTING AI TRADING AGENT ---")
    
    # 1. Test the connection
    session = await establish_connection()
    
    if session:
        print("\n--- INITIATING DRY-FIRE TEST ---")
        # 2. Attempt to push a mock trade payload (e.g., buying 1 share of AAPL at a low limit price)
        # Assuming manual approvals are on, this should just pop up on your phone.
        await execute_trade(session=session, ticker="AAPL", limit_price=150.00, quantity=1)
    else:
        print("Halting execution: Could not secure Robinhood connection.")

if __name__ == "__main__":
    asyncio.run(run_system_check())