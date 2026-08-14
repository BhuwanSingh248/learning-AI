from typing import List, Tuple
from src.history.event_store import EventStore
from src.history.models import HistoricalEvent
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class EventRetriever:
    """
    Retrieves semantically relevant historical events for a given query or context.
    """
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        
    def retrieve(self, query: str, top_k: int = 1) -> List[Tuple[HistoricalEvent, float]]:
        logger.info("EventRetriever | Retrieving top %d similar events for query: '%s'", top_k, query)
        return self.event_store.search_similar_events(query, top_k)
