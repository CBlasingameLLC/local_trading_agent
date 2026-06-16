class BullishStrategyEngine:
    def __init__(self, max_position_risk_pct: float = 0.10, total_budget: float = 500.00):
        """
        Initializes guardrails for small-account allocation.
        Default: No single trade can exceed 10% ($50) of the $500 total budget.
        """
        self.total_budget = total_budget
        self.max_trade_allocation = total_budget * max_position_risk_pct

    def evaluate_signals(self, ticker: str, market_data: dict, sentiment_score: float) -> dict:
        """
        Combines technical indicators and qualitative sentiment metrics to output
        an actionable trade signal.
        
        market_data expected format: {"rsi": float, "macd_bullish": bool, "current_price": float}
        sentiment_score: Scale of -1.0 (highly bearish) to +1.0 (highly bullish)
        """
        rsi = market_data.get("rsi", 50.0)
        macd_bullish = market_data.get("macd_bullish", False)
        current_price = market_data.get("current_price", 0.0)
        
        if current_price <= 0:
            return {"action": "HOLD", "reason": f"Invalid price data for {ticker}"}

        print(f"🕵️ Analyzing {ticker} | RSI: {rsi:.1f} | MACD Bullish: {macd_bullish} | Sentiment: {sentiment_score:.2f}")

        # Core Bullish Filter Criteria:
        # 1. RSI shows momentum but isn't deeply overbought (< 65)
        # 2. MACD signal line crossover is positive
        # 3. Local AI model confirms positive qualitative catalyst sentiment (> 0.3)
        is_technically_bullish = (30.0 < rsi < 65.0) and macd_bullish
        is_sentiment_bullish = sentiment_score >= 0.30

        if is_technically_bullish and is_sentiment_bullish:
            # Calculate position sizing safely bounded by the maximum allocation constraint
            target_cash_allocation = self.max_trade_allocation
            
            # Calculate share quantity (Robinhood MCP accepts fractional amounts)
            quantity = round(target_cash_allocation / current_price, 4)
            
            return {
                "action": "BUY",
                "ticker": ticker,
                "limit_price": round(current_price * 1.002, 2), # 0.2% slippage buffer for limit order
                "quantity": quantity,
                "reason": "Technical momentum alignment matched positive AI structural sentiment."
            }
        
        return {"action": "HOLD", "reason": "Filters not met. Conditions do not match bullish profile."}