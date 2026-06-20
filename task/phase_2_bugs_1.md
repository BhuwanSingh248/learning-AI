# 📘 Phase 2 Closure — Missing Items & Bug Fix Backlog

Status: Post Phase-2 Audit

Purpose:

Before starting Phase 3, ensure the Stock Agent behaves as a complete, production-quality recommendation system.

---

# Priority 1 — Critical Functional Gaps

## Bug 2.9.1 — Query Intent Routing Missing

Current:

```text
/analyze
 ↓
RAG Retrieval
 ↓
Grounding
```

Problem:

Queries like:

```text
What is PE Ratio?
What is Shareholding Pattern?
What is Market Cap?
```

always fail because the system only understands news-backed questions.

Required:

Create:

```text
src/query_router/
```

Components:

```text
intent_classifier.py

query_types.py
```

Supported intents:

```text
NEWS
FUNDAMENTAL
HISTORICAL
RECOMMENDATION
UNKNOWN
```

Temporary behavior:

```text
FUNDAMENTAL
↓
Return structured "not yet supported"
```

instead of attempting RAG retrieval.

---

## Bug 2.9.2 — Analyze Endpoint Returns Refusal Too Often

Current:

```text
Grounding Threshold
↓
REFUSE
```

Problem:

Calibration report shows many legitimate queries still fail.

Required:

Review:

```text
GroundingService
calibrate_grounding.py
```

Tasks:

```text
Validate thresholds

Validate reranker distributions

Review top_k values

Review average-score calculations
```

Do NOT automate calibration yet.

Goal:

```text
Legitimate news queries should pass.
```

---

## Bug 2.9.3 — Empty Symbol Diagnostics

Problem:

No clear explanation whether:

```text
No News Exists

No Chunks Indexed

Retrieval Failed

Symbol Unknown
```

Required:

Enhance diagnostics.

Example:

```json
{
  "failure_type": "NO_NEWS_INDEXED"
}
```

---

# Priority 2 — API Improvements

## Bug 2.9.4 — Add Supported Capability Metadata

Current:

```text
/analyze
```

accepts every query.

Required:

Add:

```http
GET /capabilities
```

Response:

```json
{
  "supports": [
    "news_analysis",
    "recommendations",
    "historical_events"
  ],
  "not_supported": [
    "shareholding",
    "financial_statements",
    "technical_analysis"
  ]
}
```

---

## Bug 2.9.5 — Model Metadata Endpoint

Create:

```http
GET /models
```

Return:

```json
{
  "active_model": "qwen2.5:3b"
}
```

Required for future benchmarking.

---

## Bug 2.9.6 — Pipeline Status Endpoint

Create:

```http
GET /pipeline/status
```

Return:

```json
{
  "faiss": true,
  "reranker": true,
  "ollama": true,
  "database": true
}
```

---

# Priority 3 — Evaluation Gaps

## Bug 2.9.7 — Evaluation Dataset Coverage

Current:

```text
evaluation_dataset.json
```

needs verification.

Add coverage for:

```text
Positive News

Negative News

Risk News

Refusal Queries

Historical Queries
```

Target:

```text
100+ cases
```

---

## Bug 2.9.8 — Benchmark Runner Validation

Verify:

```text
evaluation/run_benchmark.py
```

actually executes:

```text
Real model
```

and not mocked outputs.

Validate:

```text
Qwen

Mistral

Llama
```

execution paths.

---

# Priority 4 — Historical Engine Gaps

## Bug 2.9.9 — Historical Events Validation

Current:

```text
historical_events.json
```

contains synthetic outcome data.

Required:

Mark dataset as:

```text
Seed Dataset
```

not:

```text
Ground Truth
```

Add documentation.

---

## Bug 2.9.10 — Historical Similarity Evaluation

Create tests validating:

```text
Current Tariff News
 ↓
Trade War Events Retrieved

War News
 ↓
Ukraine Event Retrieved
```

---

# Priority 5 — Frontend Integration Readiness

## Bug 2.9.11 — Missing Visualization Endpoints

Frontend currently cannot display:

```text
Signals

Historical Matches

Benchmark Results

Evaluation Results
```

Required APIs:

```http
GET /evaluation/results

GET /benchmark/results

POST /historical-events/search

POST /signals
```

---

## Bug 2.9.12 — Recommendation Explainability

Expose:

```json
{
  "recommendation": "BUY",
  "signals": [...],
  "historical_matches": [...],
  "citations": [...]
}
```

for UI rendering.

---

# Priority 6 — Operational Gaps

## Bug 2.9.13 — News Freshness Monitoring

Create health check:

```text
Latest Indexed News Timestamp
```

Alert if:

```text
No news indexed in last 24h
```

---

## Bug 2.9.14 — Duplicate Indexing Protection

Verify:

```text
NewsIndexer
```

does not repeatedly insert identical articles.

---

## Bug 2.9.15 — RAG Observability

Track:

```text
Retrieved Chunks

Reranked Chunks

Grounded %

Refused %

Average Score
```

Persist metrics.

---

# Exit Criteria Before Phase 3

Must be true:

```text
✓ Analyze endpoint stable

✓ Grounding calibrated

✓ Evaluation suite working

✓ Benchmark suite working

✓ Historical retrieval validated

✓ Frontend can consume outputs

✓ Diagnostics improved

✓ Capability routing implemented
```

Only after these are complete should development move to:

```text
Phase 3.1
Event Detection Engine
```
