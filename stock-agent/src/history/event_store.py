import os
import json
import numpy as np
import faiss
from typing import List, Tuple
from src.config.logger import setup_logger
from src.rag.embedder import EmbeddingModel
from src.history.models import HistoricalEvent

logger = setup_logger(__name__)

class EventStore:
    """
    In-memory database loading historical events from JSON and indexing them
    using FAISS semantic embeddings for fast retrieval.
    """
    def __init__(self, embedder: EmbeddingModel, filepath: str = None):
        self.embedder = embedder
        if filepath is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "historical_events.json"))
            
        self.filepath = filepath
        self.events: List[HistoricalEvent] = []
        self.index = None
        
        self.load_events()
        self.build_index()
        
    def load_events(self):
        logger.info("EventStore | Loading historical events from %s", self.filepath)
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.events = [HistoricalEvent(**item) for item in data]
            logger.info("EventStore | Successfully loaded %d historical events", len(self.events))
        except Exception as e:
            logger.error("EventStore | Failed to load historical events JSON: %s", e)
            self.events = []
            
    def build_index(self):
        if not self.events:
            logger.warning("EventStore | No events to index.")
            return
            
        logger.info("EventStore | Building FAISS semantic index for historical events")
        try:
            embeddings = []
            for ev in self.events:
                emb = self.embedder.embed_text(ev.description)
                embeddings.append(emb)
                
            emb_np = np.array(embeddings, dtype=np.float32)
            dimension = emb_np.shape[1]
            
            # IndexFlatIP for Cosine Similarity (using normalized L2 embeddings)
            self.index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(emb_np)
            self.index.add(emb_np)
            logger.info("EventStore | Successfully built FAISS event index of dimension %d", dimension)
        except Exception as e:
            logger.error("EventStore | Failed to build FAISS event index: %s", e)
            
    def search_similar_events(self, query: str, top_k: int = 1) -> List[Tuple[HistoricalEvent, float]]:
        """
        Finds similar events semantically matching the query.
        Returns a list of tuples containing (HistoricalEvent, similarity_score).
        """
        if self.index is None or not self.events:
            logger.warning("EventStore | FAISS index not built. Search returned empty list.")
            return []
            
        try:
            query_emb = self.embedder.embed_text(query)
            q_np = np.array([query_emb], dtype=np.float32)
            faiss.normalize_L2(q_np)
            
            scores, indices = self.index.search(q_np, top_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1:
                    # Clip similarity between 0.0 and 1.0
                    similarity = float(max(0.0, min(1.0, score)))
                    results.append((self.events[idx], similarity))
            return results
        except Exception as e:
            logger.error("EventStore | Error during similar events search: %s", e)
            return []
