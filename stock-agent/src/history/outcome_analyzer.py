from typing import Optional
from src.history.models import HistoricalEvent
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class OutcomeAnalyzer:
    """
    Analyzes historical event results, matching specific stock tickers or mapping to sector behaviors.
    """
    @staticmethod
    def get_stock_sector(symbol: str) -> str:
        """Helper mapping common stock tickers to their primary sectors."""
        sym = symbol.upper()
        if sym in ["INFY", "AAPL", "MSFT", "TSLA", "NVDA"]:
            return "IT"
        elif sym in ["JPM", "BAC", "WFC", "SVB"]:
            return "Financials"
        else:
            return "Manufacturing"

    def analyze_outcome(self, event: HistoricalEvent, symbol: str) -> str:
        """
        Analyzes historical event outcomes for a stock symbol or its sector,
        returning a human-readable observed outcome description string.
        """
        symbol_upper = symbol.upper()
        sector = self.get_stock_sector(symbol_upper)
        
        # 1. Check stock-specific outcome
        for so in event.stock_outcomes:
            if so.get("stock_symbol") == symbol_upper:
                ret = so.get("return_30d", 0.0)
                direction = "fell" if ret < 0 else "rose"
                return f"{symbol_upper} stock {direction} {abs(ret) * 100:.0f}%"
                
        # 2. Check sector-specific outcome
        for se in event.sector_outcomes:
            if se.get("sector") == sector or se.get("sector") == event.sector:
                ret = se.get("return_30d", 0.0)
                direction = "fell" if ret < 0 else "rose"
                sec_name = se.get("sector", "Sector")
                return f"{sec_name} stocks {direction} {abs(ret) * 100:.0f}%"
                
        # 3. Fallback to event impact score
        direction = "negative" if event.impact_score < 0 else "positive"
        return f"Sector average trend was {direction} with impact score of {event.impact_score}"
