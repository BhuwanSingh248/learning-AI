from typing import List
from src.config.settings import settings
from src.rag.models import NewsChunk
import re


class NewsChunker:
    """
    Chunk news (title + summary) into overlapping segments for vector indexing.
    Maintains consistency by sliding a window of sentences with overlap.
    """

    @staticmethod
    def chunk(
        title: str,
        summary: str,
        *,
        symbol: str = None,
        source_id: str = None,
        timestamp: str = None,
        document_id: str = None,
        content_hash: str = None,
        chunking_version: str = "v1"
    ) -> List[NewsChunk]:
        if not title and not summary:
            return []
        
        import hashlib
        
        # 1. Compute stable document_id if not provided
        if not document_id:
            input_str = f"{symbol}_{source_id}_{timestamp}_{title}"
            document_id = hashlib.sha256(input_str.encode("utf-8")).hexdigest()
            
        # 2. Compute stable content_hash if not provided
        if not content_hash:
            content_str = f"{title}_{summary}"
            content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
        
        combined_text = NewsChunker._combine_text(title or "", summary or "")
        sentences = NewsChunker._split_sentence(combined_text)
        raw_chunks = NewsChunker._build_chunk(sentences)
        chunks = NewsChunker._attach_metadata(
            raw_chunks, symbol, source_id, timestamp, 
            document_id, content_hash, chunking_version
        )
        return chunks        
    
    @staticmethod
    def _combine_text(title:str,summary:str)->str:
        return f"Title: {title}\nSummary: {summary}"
    
    @staticmethod
    def _split_sentence(text:str)->List[str]:
        #use regex to split the text into sentences
        split_sentence = re.split(r'(?<=[.!?])\s+', text) 
        return [s.strip() for s in split_sentence if s.strip()]

    @staticmethod
    def _build_chunk(sentences: List[str]) -> List[str]:
        chunks = []
        current = []
        current_size = 0

        overlap_sentence_count = settings.CHUNK_OVERLAP  # now represents number of sentences

        for sentence in sentences:
            s_len = len(sentence) / settings.CHAR_PER_TOKEN

            # If adding this sentence exceeds chunk size → flush current chunk
            if current and (current_size + s_len > settings.CHUNK_SIZE):
                chunk_text = " ".join(current)
                chunks.append(chunk_text)

                # Keep last N sentences for overlap
                overlap_sentences = current[-overlap_sentence_count:] if overlap_sentence_count > 0 else []
                current = overlap_sentences.copy()

                # Recalculate size based on overlap sentences
                current_size = sum(len(s) for s in current) / settings.CHAR_PER_TOKEN

            # Always add current sentence
            current.append(sentence)
            current_size += s_len

        # Final flush
        if current:
            chunks.append(" ".join(current))

        return chunks

    
    @staticmethod
    def _attach_metadata(
        raw_chunk: List[str],
        symbol: str,
        source_id: str,
        timestamp: str,
        document_id: str,
        content_hash: str,
        chunking_version: str = "v1"
    ) -> List[NewsChunk]:
        import hashlib
        chunks = []
        for index, chunk in enumerate(raw_chunk):
            # stable chunk_id is a hash of (document_id + chunk_index + chunking_version)
            chunk_input = f"{document_id}_{index}_{chunking_version}"
            chunk_id = hashlib.sha256(chunk_input.encode("utf-8")).hexdigest()
            
            chunks.append(NewsChunk(
                chunk_id=chunk_id,
                source_id=source_id,
                chunk_index=index,
                symbol=symbol,
                timestamp=timestamp,
                text=chunk,
                document_id=document_id,
                content_hash=content_hash,
                chunking_version=chunking_version
            ))
        return chunks
    
    