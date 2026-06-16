import os
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import uvicorn
from fastapi import WebSocket, WebSocketDisconnect
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from execution.robinhood_mcp import establish_connection, execute_trade
from strategies.equity_bullish import BullishStrategyEngine
from data.directional_tool import get_quantitative_metrics
from data.catalyst_tool import get_raw_sentiment_score

# Import the FastAPI app and WebSocket manager
from api.websocket_server import app, manager

WATCHLIST = ["AAPL", "NVDA", "AMD", "TSLA", "MSFT"]
strategy = BullishStrategyEngine(max_position_risk_pct=0.10, total_budget=500.00)
scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))

async def log_and_broadcast(message: str, msg_type: str = "info", payload: dict = None):
    print(message)
    ws_msg = {"type": msg_type, "message": message}
    if payload:
        ws_msg.update(payload)
    await manager.broadcast(ws_msg)

async def fetch_live_market_metrics(ticker: str) -> tuple:
    market_data = get_quantitative_metrics(ticker)
    sentiment_score = get_raw_sentiment_score(ticker)
    return market_data, sentiment_score

async def market_execution_loop():
    await log_and_broadcast("\n⏰ Market interval triggered. Initializing scan...", "system")
    
    from mcp.client.stdio import stdio_client
    from mcp import ClientSession
    from execution.robinhood_mcp import SERVER_PARAMS

    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                for ticker in WATCHLIST:
                    market_data, sentiment_score = await fetch_live_market_metrics(ticker)
                    signal = strategy.evaluate_signals(ticker, market_data, sentiment_score)
                    
                    log_msg = f"🕵️ Analyzing {ticker} | SMA Aligned: {market_data.get('is_bullish_aligned')} | Sentiment: {sentiment_score:.2f}"
                    await log_and_broadcast(log_msg)

                    if signal["action"] == "BUY":
                        await log_and_broadcast(f"🎯 Execution Alert: {signal['reason']}", "alert", signal)
                        await log_and_broadcast(
                            f"⏸️ Awaiting manual approval for {ticker} via PWA...", 
                            "awaiting_approval", 
                            {"ticker": ticker, "limit_price": signal["limit_price"], "quantity": signal["quantity"]}
                        )
                    else:
                        await log_and_broadcast(f"横 {ticker}: {signal['reason']}")

    except Exception as e:
        await log_and_broadcast(f"❌ Execution loop failed to connect to MCP: {e}", "error")

# --- NEW: The API Listener ---
@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            cmd = payload.get("command")
            
            if cmd == "KILL_SWITCH":
                await log_and_broadcast("🚨 KILL SWITCH ACTIVATED: Halting background scheduler...", "error")
                scheduler.pause()
                
            elif cmd == "FORCE_SCAN":
                await log_and_broadcast("⚡ Manual scan triggered from PWA Dashboard...", "system")
                asyncio.create_task(market_execution_loop())
                
            elif cmd == "APPROVE_TRADE":
                await log_and_broadcast(f"✅ Trade manually approved for {payload.get('ticker')}. (Execution routing built next)", "system")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Use lifespan instead of the deprecated on_event
@app.on_event("startup")
async def startup_event():
    await log_and_broadcast("--- 🚀 STARTING AUTONOMOUS TRADING SYSTEM 🚀 ---", "system")
    scheduler.add_job(market_execution_loop, 'cron', day_of_week='mon-fri', hour='9-15', minute='*/15')
    scheduler.start()
    await log_and_broadcast("⏰ Core Scheduler Active. Monitoring market hours window (EST)...", "system")

# --- NEW: Serve the React PWA ---
build_dir = os.path.join(os.path.dirname(__file__), "pwa-dashboard", "build")
if os.path.exists(build_dir):
    # Mount the frontend. It must be placed after the WebSocket route so it doesn't block the API.
    app.mount("/", StaticFiles(directory=build_dir, html=True), name="frontend")
else:
    print("⚠️ Warning: React build folder not found. Run 'npm run build' in pwa-dashboard.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)