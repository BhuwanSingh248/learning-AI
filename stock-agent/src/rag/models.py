"""
RAG Metadata Models
===================

Defines the SQLAlchemy ORM models for storing RAG metadata.
"""

from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from src.config.database import Base


class RagNewsMetadata(Base):
    """
    SQLAlchemy model tracking metadata for news text indexed in FAISS.
    
    FAISS maps vector index -> this ID. We use this table to retrieve 
    the actual string content after FAISS returns the Top-K closest IDs.
    """
    __tablename__ = "rag_news_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_id = Column(Integer, index=True, nullable=False)
    source_id = Column(String, index=True, nullable=False)
    chunk_index = Column(Integer, index=True, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

@dataclass
class NewsChunk:
    chunk_id:int
    source_id:str
    chunk_index:int
    symbol:str
    timestamp:str
    text:str
    
