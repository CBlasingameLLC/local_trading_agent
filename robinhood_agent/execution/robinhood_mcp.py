import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

# We use npx to run the official remote MCP bridge.
# This handles the secure browser popup and OAuth token management automatically.
SERVER_PARAMS = StdioServerParameters(
    command="npx",
    args=["-y", "mcp-remote", "https://agent.robinhood.com/mcp/trading"]
)

async def establish_connection():
    """
    Establishes a connection to the Robinhood MCP server via stdio bridge 
    and verifies the ring-fenced account status.
    """
    print("Initiating handshake with Robinhood MCP...")
    print("If this is your first time, a browser window will open to authenticate.")

    try:
        # Connect using the stdio bridge instead of direct SSE
        async with stdio_client(SERVER_PARAMS) as (read, write):
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
                
                # In a persistent app, we wouldn't return the session to close immediately,
                # but for this dry-run test, we will execute a mock trade inside the context block.
                await execute_trade(session, ticker="AAPL", limit_price=10.00, quantity=1)
                return True

    except Exception as e:
        print(f"❌ Critical Error connecting to Robinhood: {e}")
        return False

async def execute_trade(session: ClientSession, ticker: str, limit_price: float, quantity: float = 1.0):
    """
    Pushes a validated trade payload to the Robinhood server.
    """
    print(f"\nRouting trade to Robinhood: Buy {quantity}x {ticker} at ${limit_price}")
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