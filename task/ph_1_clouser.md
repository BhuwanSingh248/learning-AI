# 📘 Phase 1 — Closure & Missing Link Resolution

## Objective

The architecture review identified that the core RAG pipeline is implemented and connected.

Implemented:

```text
✓ Chunking
✓ Embedding
✓ FAISS
✓ BM25
✓ Hybrid Retrieval
✓ Cross Encoder Reranker
✓ Grounding
✓ Citation Builder
✓ Context Builder
✓ Prompt Builder
✓ LLM Integration
✓ StockAgent Orchestration
✓ Debug Endpoints
```

The remaining work focuses on exposing capabilities, validating production flow, and closing Phase 1.

---

# 🎯 Success Criteria

A user can:

```text
Ask a stock question
↓
Retrieve evidence
↓
Pass Grounding
↓
Generate answer
↓
Receive citations
```

and

```text
Ask an unsupported question
↓
Grounding fails
↓
Refusal returned
```

through public APIs.

---

# 🧩 STEP 6.5 — User Query Driven Analysis Endpoint

## Problem

Current flow:

```text
Symbol
↓
Fixed Query
("Recent context and news updates")
↓
RAG
↓
LLM
```

The user cannot provide a custom query.

---

## Goal

Expose the complete RAG system.

---

## STEP 6.5.1 — Create Request Model

Create:

```python
AnalyzeRequest
```

Fields:

```python
symbol: str
query: str
top_k: int = 10
```

Example:

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys after recent earnings?",
  "top_k": 10
}
```

---

## STEP 6.5.2 — Create Response Model

Create:

```python
AnalyzeResponse
```

Fields:

```python
answer: str

grounded: bool

confidence_score: float

citations: List[Citation]

diagnostics: Optional[dict]
```

---

## STEP 6.5.3 — Add Endpoint

Create:

```http
POST /analyze
```

Purpose:

```text
User-driven stock research
```

---

## STEP 6.5.4 — Wire User Query

Current:

```python
retrieve(symbol)
```

Future:

```python
retrieve(
    symbol=symbol,
    query=query
)
```

The user query must flow through:

```text
Hybrid Retrieval
↓
Reranker
↓
Grounding
```

---

# 🧩 STEP 6.6 — Grounding Configuration

## Goal

Remove hardcoded thresholds.

---

Move into:

```python
settings.py
```

Add:

```python
GROUNDING_MIN_SCORE

GROUNDING_MIN_AVERAGE_SCORE

GROUNDING_MIN_CHUNKS
```

---

GroundingService must consume configuration.

---

# 🧩 STEP 6.7 — End-to-End Validation

## Objective

Verify production behavior.

---

## Test 1

Request:

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys after recent earnings?"
}
```

Expected:

```text
Retrieval
↓
Rerank
↓
Grounding PASS
↓
Prompt Builder
↓
LLM
↓
Answer
```

---

## Test 2

Request:

```json
{
  "symbol": "INFY",
  "query": "Will Infosys build a city on Mars?"
}
```

Expected:

```text
Retrieval
↓
Rerank
↓
Grounding FAIL
↓
Refusal
```

---

# 🧩 STEP 6.8 — Retrieval Quality Audit

## Objective

Investigate score inconsistencies.

---

Use:

```http
POST /debug/retrieval
```

for:

```text
INFY
HDFCBANK
ICICIBANK
RELIANCE
```

---

Verify:

```text
Retrieved chunks are relevant

Retrieved chunks match query intent

Retrieved chunks belong to requested company
```

---

Document findings.

---

# 🧩 STEP 6.9 — Reranker Quality Audit

Use:

```http
POST /debug/rerank
```

Verify:

```text
Best chunk ranked first
```

---

Inspect:

```text
Strong Query Scores

Weak Query Scores
```

---

# 🧩 STEP 6.10 — Grounding Calibration (Reduced Scope)

## Goal

Do NOT spend significant time tuning.

---

Current action:

```text
Move calibration report to project artifacts
```

---

Only adjust thresholds if:

```text
Valid queries frequently fail.
```

---

Otherwise:

```text
Accept current calibration
```

and continue.

---

# 🧩 STEP 6.11 — Regression Tests

Minimum coverage:

```python
test_hybrid_retrieval()

test_reranker()

test_grounding_allow()

test_grounding_refuse()

test_analyze_endpoint()

test_refusal_path()
```

---

Goal:

Prevent Phase 1 regressions.

---

# 🧩 STEP 6.12 — Final Phase 1 Audit

Verify:

```text
Chunking
Embedding
FAISS
BM25
Hybrid Retrieval
Reranker
Grounding
Citation Builder
Prompt Builder
LLM
Analyze Endpoint
```

are all reachable.

---

Identify:

```text
Dead code

Unused services

Orphan components
```

---

# 🧩 STEP 6.13 — Phase 1 Closure

Generate final report.

---

Sections:

```text
Retrieval
PASS / FAIL

Reranker
PASS / FAIL

Grounding
PASS / FAIL

Analyze Endpoint
PASS / FAIL

Refusal Path
PASS / FAIL

Regression Tests
PASS / FAIL
```

---

# 🚀 Deliverables

1. User Query Driven Analysis Endpoint
2. Grounding Config Settings
3. End-to-End Validation
4. Retrieval Audit
5. Reranker Audit
6. Regression Tests
7. Final Phase 1 Audit Report

---

# Definition of Done

The system supports:

```text
User Question
↓
Evidence Retrieval
↓
Grounding
↓
Citation-backed Answer
```

and

```text
Unsupported Question
↓
Grounding Refusal
```

through public APIs.

At that point:

```text
PHASE 1 COMPLETE
```