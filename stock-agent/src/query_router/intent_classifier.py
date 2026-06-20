import re
from src.query_router.query_types import QueryIntent

# Financial keyword definitions for classification
FUNDAMENTAL_KEYWORDS = [
    r"\bpe\b", r"\bp/e\b", r"\bprice to earnings\b", r"\bmarket cap\b", r"\bshareholding\b",
    r"\bbalance sheet\b", r"\bincome statement\b", r"\bdebt to equity\b", r"\bcash flow\b",
    r"\bfinancial statements\b", r"\bdividend", r"\bbook value\b", r"\broce\b", r"\broe\b",
    r"\beps\b", r"\bearnings per share\b"
]

HISTORICAL_KEYWORDS = [
    r"\bhistory\b", r"\bsimilar\b", r"\bpast\b", r"\boccurred\b", r"\bhappened\b",
    r"\bpreviously\b", r"\breaction\b", r"\breact\b", r"\banalogy\b", r"\bhistorical\b"
]

RECOMMENDATION_KEYWORDS = [
    r"\bshould i buy\b", r"\bshould i sell\b", r"\bshould i hold\b", r"\brecommendation\b",
    r"\bbuy\b", r"\bsell\b", r"\bhold\b", r"\binvestment advice\b", r"\badvisory\b"
]

NEWS_KEYWORDS = [
    r"\bnews\b", r"\brecent updates\b", r"\bdevelopments\b", r"\bearnings report\b",
    r"\blatest news\b", r"\bannouncements\b", r"\bpress release\b"
]

class IntentClassifier:
    """
    Keyword-based query intent classifier mapping stock queries to execution paths.
    """
    @staticmethod
    def classify(query: str) -> QueryIntent:
        if not query or not query.strip():
            return QueryIntent.UNKNOWN

        q_lower = query.lower()

        # Check FUNDAMENTAL first to prevent ungrounded RAG runs
        for pattern in FUNDAMENTAL_KEYWORDS:
            if re.search(pattern, q_lower):
                return QueryIntent.FUNDAMENTAL

        # Check HISTORICAL comparison queries
        for pattern in HISTORICAL_KEYWORDS:
            if re.search(pattern, q_lower):
                return QueryIntent.HISTORICAL

        # Check RECOMMENDATION queries
        for pattern in RECOMMENDATION_KEYWORDS:
            if re.search(pattern, q_lower):
                return QueryIntent.RECOMMENDATION

        # Check NEWS indicators
        for pattern in NEWS_KEYWORDS:
            if re.search(pattern, q_lower):
                return QueryIntent.NEWS

        # Fallback to NEWS to allow general news-driven searches
        return QueryIntent.NEWS
