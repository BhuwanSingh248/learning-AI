# Phase 7.6 - Backend API Plan for UI Integration

---

# Objective

Expose Phase 7 internals through stable API contracts so UI can show:

* RAG background activity
* signal-driven explainability
* next prediction candidates

This file is backend-only planning.

---

# Current Backend Status

Implemented internally:

* Embedding layer (`all-MiniLM-L6-v2`, 384 dim)
* FAISS vector store and retrieval
* Context-aware prompt flow (signals + retrieved context)

Current status from API review:

* `/suggest` now includes extended optional fields in code path.
* `/health` endpoint exists.
* `/debug/symbol/{symbol}` endpoint exists.

Remaining quality gaps before UI integration:

* `/health` is currently static and always healthy; it must reflect real subsystem state.
* `rag.fallback_used` logic is incorrect when retrieval returns "No significant recent news found."
* `prediction.expected_direction` should support `neutral` and align with decision logic.
* `rag.context_items` is currently empty even when context exists.
* `RagDebugInfo.context_items` uses mutable default `[]`; should use `Field(default_factory=list)`.

---

# Required API Changes

## 1. Extend `POST /suggest` response (backward-compatible)

Existing request remains:

```json
{
  "symbols": ["AAPL", "MSFT", "NVDA"],
  "lookback_days": 90
}
```

Extended response proposal:

```json
{
  "suggestions": [
    {
      "symbol": "NVDA",
      "score": 0.91,
      "decision": "Bullish",
      "reason": "Strong momentum supported by positive retrieved context.",
      "signal_breakdown": {
        "trend": "bullish",
        "momentum": 0.88,
        "volatility": 0.24,
        "sentiment_score": 0.74,
        "event_score": 0.52
      },
      "rag": {
        "enabled": true,
        "query": "Recent context and news updates for NVDA",
        "retrieval_strategy": "similarity_search",
        "top_k": 5,
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_dimension": 384,
        "index_type": "flat_l2",
        "fallback_used": false,
        "context_preview": "Recent News: ...",
        "context_items": [
          {
            "title": "NVIDIA beats expectations",
            "summary": "Revenue grew faster than expected.",
            "source": "Reuters",
            "timestamp": "2026-04-25T08:15:00Z",
            "relevance_score": 0.98
          }
        ]
      },
      "prediction": {
        "horizon": "short_term",
        "rank_bucket": "top_candidate",
        "confidence": 0.82,
        "expected_direction": "bullish"
      }
    }
  ]
}
```

Notes:

* Keep new fields optional to avoid breaking old clients.
* Preserve existing core fields exactly.

---

## 2. Add `GET /health` endpoint with subsystem checks

Response proposal:

```json
{
  "level": "healthy",
  "summary": "Core and RAG subsystems available.",
  "details": "All critical services are operational.",
  "probe_target": "/health",
  "checks": {
    "api": {
      "status": "healthy",
      "summary": "API responding."
    },
    "embedding_layer": {
      "status": "healthy",
      "summary": "Embedding model loaded.",
      "embedding_model": "all-MiniLM-L6-v2",
      "vector_dimension": 384
    },
    "vector_index": {
      "status": "healthy",
      "summary": "FAISS index ready.",
      "index_type": "flat_l2",
      "top_k": 5
    },
    "retrieval_pipeline": {
      "status": "healthy",
      "summary": "Retriever operational.",
      "retrieval_strategy": "similarity_search"
    },
    "reasoning": {
      "status": "healthy",
      "summary": "LLM reasoning with context enabled.",
      "prompt_mode": "signals+context"
    }
  }
}
```

---

## 3. Optional endpoint for focused debugging

`GET /debug/symbol/{symbol}?lookback_days=90`

Purpose:

* easier QA of one symbol without running full batch
* returns one fully-detailed prediction payload

---

# Schema Additions (Pydantic)

Suggested additions in API schemas:

* `SignalBreakdown`
* `RagContextItem`
* `RagDebugInfo`
* `PredictionMeta`
* `SuggestionItem` extended with optional:
  * `signal_breakdown`
  * `rag`
  * `prediction`

Health schemas:

* `HealthCheckItem`
* `HealthResponse`

---

# Implementation Checklist

1. Keep extended `/suggest` schema and ensure all new fields remain optional.
2. Fix `rag.fallback_used`:
   * true when retrieval returns no meaningful items
   * false when at least one context item is used
3. Return actual `rag.context_items` (title, summary, source, timestamp, relevance_score) from retriever pipeline.
4. Fix prediction semantics:
   * `expected_direction` supports `bullish | bearish | neutral`
   * mapping aligned with score thresholds and/or model decision
5. Replace static `/health` body with real checks:
   * api
   * embedding_layer
   * vector_index
   * retrieval_pipeline
   * reasoning
6. Update schema default:
   * `RagDebugInfo.context_items = Field(default_factory=list)`
7. Add tests for:
   * backward compatibility of minimal `/suggest` fields
   * enriched `/suggest` payload correctness
   * fallback correctness (`fallback_used`)
   * `/health` degraded and unavailable cases
8. Verify `/openapi.json` examples include the enriched contracts.

---

# Acceptance Criteria

Backend Phase 7.6 is done when:

* `/suggest` returns optional enriched fields for UI
* `/health` reports real subsystem readiness (not hardcoded)
* `rag.context_items` and `fallback_used` are accurate
* `prediction.expected_direction` supports neutral and matches scoring logic
* old clients still work without contract break
* OpenAPI clearly documents new structures
