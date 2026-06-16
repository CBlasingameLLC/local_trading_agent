import os
import asyncio
from dotenv import load_dotenv
from mcp.client.sse import sse_client
from mcp import ClientSession

# Load environment variables
load_dotenv()
ROBINHOOD_TOKEN = os.getenv("ROBINHOOD_API_TOKEN")
MCP_URL = "https://agent.robinhood.com/mcp/trading"

async def establish_connection():
    """
    Establishes an SSE connection to the Robinhood MCP server and verifies
    the ring-fenced account status.
    """
    print("Initiating handshake with Robinhood MCP...")
    
    # In a production environment, headers pass the auth token
    headers = {
        "Authorization": f"Bearer {ROBINHOOD_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        async with sse_client(url=MCP_URL, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ MCP Connection Established successfully.")
                
                # Verify the ring-fenced account balance
                try:
                    portfolio = await session.call_tool("robinhood_get_portfolio", arguments={})
                    cash = portfolio.get("cash_balance", 0.0)
                    print(f"📊 Ring-fenced Budget Confirmed: ${cash}")
                    
                    if cash < 500.00:
                        print("⚠️ WARNING: Account balance is below the $500 target.")
                        
                except Exception as e:
                    print(f"Connection active, but failed to fetch portfolio tools: {e}")
                
                return session

    except Exception as e:
        print(f"❌ Critical Error connecting to Robinhood: {e}")
        return None

async def execute_trade(session: ClientSession, ticker: str, limit_price: float, quantity: float = 1.0):
    """
    Pushes a validated trade payload to the Robinhood server.
    """
    print(f"Routing trade to Robinhood: Buy {quantity}x {ticker} at ${limit_price}")
    try:
        order = await session.call_tool(
            name="robinhood_place_stock_order",
            arguments={
                "symbol": ticker,
                "side": "buy",
                "type": "limit",
                "price": limit_price,
                "quantity": quantity
            }
        )
        print(f"✅ Order Accepted: {order}")
        return order
    except Exception as e:
        print(f"❌ Order Rejected by MCP: {e}")
        return None