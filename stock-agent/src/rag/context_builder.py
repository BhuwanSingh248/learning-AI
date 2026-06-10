from typing import List
from src.rag.models import RagNewsMetadata
from src.data.models import Citation, CitationContext
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class CitationContextBuilder:
    """
    Responsible for transforming raw retrieved/reranked metadata chunks
    into evidence-backed context blocks and client citations.
    """

    @staticmethod
    def build_context(
        chunks: List[RagNewsMetadata],
        preview_char_limit: int = 150
    ) -> CitationContext:
        """
        Takes a ranked list of chunks, assigns sequential citation IDs,
        formats them into a structured prompt block, and maps them to Citation models.

        Args:
            chunks: Ranked list of RagNewsMetadata records (e.g. top 5 after reranking).
            preview_char_limit: Number of characters to keep for the citation preview.

        Returns:
            CitationContext: Contains the LLM context block and list of citations.
        """
        if not chunks:
            logger.debug("ContextBuilder | No chunks provided. Returning empty context.")
            return CitationContext(
                formatted_text="No significant recent news found.",
                citations=[]
            )

        formatted_parts = []
        citations_list = []

        logger.debug(f"ContextBuilder | Formatting {len(chunks)} chunks with citation identifiers")

        for idx, chunk in enumerate(chunks, 1):
            # 1. Clean the text and generate a preview
            clean_text = chunk.chunk_text.strip()
            preview = clean_text[:preview_char_limit]
            if len(clean_text) > preview_char_limit:
                preview = preview.rstrip() + "..."

            # 2. Format the timestamp
            time_str = chunk.timestamp.isoformat() if chunk.timestamp else "Unknown"

            # 3. Build the LLM bracketed reference line
            # Format: "[idx] Source: SourceName (Timestamp) | Context: chunk_text"
            formatted_parts.append(f"[{idx}] Source: {chunk.source_id} ({time_str}) | Context: {clean_text}")

            # 4. Instantiate a serializable Citation item
            citations_list.append(
                Citation(
                    citation_id=idx,
                    chunk_id=chunk.chunk_id,
                    source_id=chunk.source_id,
                    timestamp=time_str,
                    text_preview=preview
                )
            )

        # Join all bracketed lines into a single, clean text block for the LLM
        formatted_text = "Recent news context with reference citations:\n" + "\n\n".join(formatted_parts)

        logger.info(f"ContextBuilder | Context formatted successfully with {len(citations_list)} citations.")
        return CitationContext(
            formatted_text=formatted_text,
            citations=citations_list
        )
