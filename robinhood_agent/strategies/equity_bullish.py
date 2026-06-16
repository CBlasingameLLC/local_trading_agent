class BullishStrategyEngine:
    def __init__(self, max_position_risk_pct: float = 0.10, total_budget: float = 500.00):
        """
        Initializes guardrails for small-account allocation.
        Default: No single trade can exceed 10% ($50) of the $500 total budget.
        """
        self.total_budget = total_budget
        self.max_trade_allocation = total_budget * max_position_risk_pct

    def evaluate_signals(self, ticker: str, market_data: dict, sentiment_score: float) -> dict:
        current_price = market_data.get("current_price", 0.0)
        is_technically_bullish = market_data.get("is_bullish_aligned", False)
        
        if current_price <= 0:
            return {"action": "HOLD", "reason": f"Invalid price data for {ticker}"}

        print(f"🕵️ Analyzing {ticker} | SMA Aligned: {is_technically_bullish} | Sentiment: {sentiment_score:.2f}")

        # Core Bullish Filter Criteria
        is_sentiment_bullish = sentiment_score >= 0.30

        if is_technically_bullish and is_sentiment_bullish:
            target_cash_allocation = self.max_trade_allocation
            quantity = round(target_cash_allocation / current_price, 4)
            
            return {
                "action": "BUY",
                "ticker": ticker,
                "limit_price": round(current_price * 1.002, 2), 
                "quantity": quantity,
                "reason": "Technical SMA alignment matched positive AI structural sentiment."
            }
        
        return {"action": "HOLD", "reason": "Filters not met. Conditions do not match bullish profile."}