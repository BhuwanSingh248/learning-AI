from enum import Enum

class QueryIntent(str, Enum):
    """
    Intents supported or explicitly routed by the Stock Agent query routing engine.
    """
    NEWS = "NEWS"
    FUNDAMENTAL = "FUNDAMENTAL"
    HISTORICAL = "HISTORICAL"
    RECOMMENDATION = "RECOMMENDATION"
    UNKNOWN = "UNKNOWN"
