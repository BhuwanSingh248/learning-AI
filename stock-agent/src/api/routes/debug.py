from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db

from src.api.schemas.debug import (
    DebugRetrievalRequest,
    DebugRetrievalResponse,
    RetrievedChunkResponse,
    DebugRerankRequest,
    DebugRerankResponse,
    RerankedChunkResponse,
    DebugGroundingRequest,
    DebugGroundingResponse
)

router = APIRouter(
    prefix="/debug",
    tags=["Debug"]
)

@router.post("/retrieval", response_model=DebugRetrievalResponse)
async def debug_retrieval(request: DebugRetrievalRequest, db: AsyncSession = Depends(get_db)):
    """
    Exposes FAISS, BM25, and merged retrieval results separately for inspection.
    """
    from src.api.routes import hybrid_retriever
    try:
        faiss_raw, bm25_raw, merged_raw = await hybrid_retriever.search_detailed(
            query=request.query,
            symbol=request.symbol,
            db_session=db,
            top_k=request.top_k
        )
        
        def to_response_chunk(chunk):
            return RetrievedChunkResponse(
                chunk_id=chunk.chunk_id,
                symbol=chunk.symbol,
                source_id=chunk.source_id,
                timestamp=str(chunk.timestamp) if chunk.timestamp else None,
                chunk_text=chunk.chunk_text
            )

        return DebugRetrievalResponse(
            faiss_results=[to_response_chunk(c) for c in faiss_raw],
            bm25_results=[to_response_chunk(c) for c in bm25_raw],
            merged_results=[to_response_chunk(c) for c in merged_raw]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval debug failed: {e}")

@router.post("/rerank", response_model=DebugRerankResponse)
async def debug_rerank(request: DebugRerankRequest, db: AsyncSession = Depends(get_db)):
    """
    Retrieves candidates and applies Cross-Encoder neural reranking, returning scores.
    """
    from src.api.routes import hybrid_retriever, reranker
    try:
        # Fetch candidate pool (size top_k * 4)
        candidate_pool_size = request.top_k * 4
        _, _, candidates = await hybrid_retriever.search_detailed(
            query=request.query,
            symbol=request.symbol,
            db_session=db,
            top_k=candidate_pool_size
        )
        
        # Apply Cross-Encoder reranking
        ranked_pairs = reranker.rerank(
            query=request.query,
            candidates=candidates,
            top_k=request.top_k
        )
        
        return DebugRerankResponse(
            reranked_chunks=[
                RerankedChunkResponse(
                    chunk_id=chunk.chunk_id,
                    score=float(score),
                    chunk_text=chunk.chunk_text
                ) for chunk, score in ranked_pairs
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reranking debug failed: {e}")

@router.post("/grounding", response_model=DebugGroundingResponse)
async def debug_grounding(request: DebugGroundingRequest, db: AsyncSession = Depends(get_db)):
    """
    Performs retrieval, reranking, and runs grounding service thresholds rules on candidates.
    """
    from src.api.routes import hybrid_retriever, reranker, grounding_service
    try:
        # Fetch candidate pool (size top_k * 4)
        candidate_pool_size = request.top_k * 4
        _, _, candidates = await hybrid_retriever.search_detailed(
            query=request.query,
            symbol=request.symbol,
            db_session=db,
            top_k=candidate_pool_size
        )
        
        # Apply Cross-Encoder reranking
        ranked_pairs = reranker.rerank(
            query=request.query,
            candidates=candidates,
            top_k=request.top_k
        )
        
        # Evaluate grounding logic
        decision = grounding_service.evaluate(
            query=request.query,
            ranked_chunks_with_scores=ranked_pairs
        )
        
        # Extract metric summaries
        candidate_count = len(ranked_pairs)
        best_score = float(ranked_pairs[0][1]) if candidate_count > 0 else 0.0
        scores = [score for chunk, score in ranked_pairs]
        average_score = float(sum(scores) / candidate_count) if candidate_count > 0 else 0.0
        
        return DebugGroundingResponse(
            is_grounded=decision.is_grounded,
            confidence_score=decision.confidence_score,
            reason=decision.reason,
            candidate_count=candidate_count,
            best_score=best_score,
            average_score=average_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grounding debug failed: {e}")
