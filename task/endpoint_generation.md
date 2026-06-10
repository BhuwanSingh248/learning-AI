# 📘 Phase 2 (Pre-Observability) - Debug API Implementation Plan

## Objective

Expose internal RAG pipeline components through FastAPI endpoints so they can be independently tested and validated.

These endpoints are development/debugging endpoints and are not intended for production UI consumption.

---

# Target Endpoints

Implement in the following order:

```text
1. POST /debug/retrieval
2. POST /debug/rerank
3. POST /debug/grounding
```

Do not implement:

```text
/debug/chunking
/debug/embedding
/debug/faiss
/debug/bm25
```

These are either low-value or already covered.

---

# Architecture

Current:

```text
User
 ↓
/suggest
 ↓
StockAgent
 ↓
Everything
```

Problem:

Cannot inspect intermediate stages.

---

Future:

```text
/debug/retrieval
/debug/rerank
/debug/grounding

↓

Inspect each stage independently
```

---

# STEP 1 — Create Request Models

File:

```text
src/api/schemas/debug.py
```

Create:

```python
DebugRetrievalRequest
DebugRerankRequest
DebugGroundingRequest
```

---

## DebugRetrievalRequest

Fields:

```python
symbol: str
query: str
top_k: int = 10
```

---

## DebugRerankRequest

Fields:

```python
symbol: str
query: str
top_k: int = 10
```

---

## DebugGroundingRequest

Fields:

```python
symbol: str
query: str
top_k: int = 10
```

---

# STEP 2 — Create Response Models

File:

```text
src/api/schemas/debug.py
```

---

## RetrievedChunkResponse

Fields:

```python
chunk_id: str
symbol: str
source_id: str
timestamp: str | None
chunk_text: str
```

---

## DebugRetrievalResponse

Fields:

```python
faiss_results: list[RetrievedChunkResponse]
bm25_results: list[RetrievedChunkResponse]
merged_results: list[RetrievedChunkResponse]
```

---

## RerankedChunkResponse

Fields:

```python
chunk_id: str
score: float
chunk_text: str
```

---

## DebugRerankResponse

Fields:

```python
reranked_chunks: list[RerankedChunkResponse]
```

---

## DebugGroundingResponse

Fields:

```python
is_grounded: bool
confidence_score: float
reason: str
candidate_count: int
best_score: float
average_score: float
```

---

# STEP 3 — Create Router

File:

```text
src/api/routes/debug.py
```

Create:

```python
router = APIRouter(
    prefix="/debug",
    tags=["Debug"]
)
```

---

# STEP 4 — Implement Retrieval Endpoint

Endpoint:

```text
POST /debug/retrieval
```

---

## Purpose

Inspect retrieval quality.

---

## Service Flow

```text
Request
 ↓
HybridRetriever
 ↓
Return:
FAISS
BM25
Merged
```

---

## Implementation Notes

Expose:

```python
faiss_results
bm25_results
merged_results
```

Separately.

Do NOT return only merged results.

We need visibility.

---

## Example Request

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys?",
  "top_k": 10
}
```

---

# STEP 5 — Implement Rerank Endpoint

Endpoint:

```text
POST /debug/rerank
```

---

## Purpose

Inspect neural ranking.

---

## Service Flow

```text
Request
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
Return Scores
```

---

## Response

```json
{
  "reranked_chunks": [
    {
      "chunk_id": "abc",
      "score": 0.91,
      "chunk_text": "..."
    }
  ]
}
```

---

## Validation

Verify:

```text
Highest score appears first
```

---

# STEP 6 — Implement Grounding Endpoint

Endpoint:

```text
POST /debug/grounding
```

---

## Purpose

Inspect grounding decisions.

---

## Service Flow

```text
Request
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
GroundingService
 ↓
Return Decision
```

---

## Response

```json
{
  "is_grounded": true,
  "confidence_score": 0.74,
  "reason": "...",
  "candidate_count": 5,
  "best_score": 0.91,
  "average_score": 0.74
}
```

---

## Validation Cases

### Case 1

Good query

Expected:

```text
is_grounded = true
```

---

### Case 2

Weak query

Expected:

```text
is_grounded = false
```

---

# STEP 7 — Register Router

File:

```text
src/api/routes/__init__.py
```

or

```text
src/main.py
```

depending on project structure.

---

Add:

```python
app.include_router(debug_router)
```

---

# STEP 8 — Swagger Validation

Start FastAPI.

Verify:

```text
/debug/retrieval
/debug/rerank
/debug/grounding
```

appear inside:

```text
/docs
```

---

# STEP 9 — Manual Testing

Test:

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys?"
}
```

---

Verify:

## Retrieval

```text
Chunks returned
```

---

## Rerank

```text
Scores returned
```

---

## Grounding

```text
Decision returned
```

---

# STEP 10 — Success Criteria

All endpoints should support:

```text
POST /debug/retrieval
POST /debug/rerank
POST /debug/grounding
```

through Swagger.

---

Developers should be able to answer:

```text
Why was this chunk retrieved?
Why was this chunk ranked first?
Why did grounding pass?
Why did grounding fail?
```

without reading logs.

---

# Deliverables

```text
src/api/routes/debug.py

src/api/schemas/debug.py

/debug/retrieval
/debug/rerank
/debug/grounding
```

implemented and available through Swagger.

---

# After Completion

Proceed to:

```text
Phase 2
 ↓
Metrics Framework
 ↓
Langfuse
 ↓
RAGAS
```

Only after these endpoints are working correctly.
