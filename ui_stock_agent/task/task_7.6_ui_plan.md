# Phase 7.6 - UI Planning Draft (RAG Visibility and Prediction Surfaces)

---

# Objective

Draft the UI layer for Phase 7 so users can see:

* what RAG is doing in background
* what signals are driving decisions
* what the "next prediction" candidates are

This is a draft only (no backend contract change implemented here yet).

---

# Scope Separation

This file is UI-only planning.

Backend contract details are tracked separately in:

* `stock-agent/task/task_7.6_backend_api_plan.md`

---

# Proposed UI Layer (Draft)

## 1. Prediction Board

Purpose:

* show ranked stocks for current run
* highlight top 3 "next prediction candidates"
* show confidence context (signals + RAG mode)

Cards include:

* symbol
* score
* decision
* short reason
* mode:
  * `signals-only`
  * `signals+context`

---

## 2. RAG Pipeline Panel

Purpose:

* show what retrieval is doing in background per symbol

Sections:

* query built for retrieval
* embedding model and vector dimension
* FAISS index type and Top-K
* retrieved context preview
* fallback used or not

---

## 3. Prediction Explainability Drawer

Purpose:

* deep drill-down for one symbol

Show:

* signal breakdown:
  * trend
  * momentum
  * volatility
  * sentiment
  * event score
* retrieved items (title, source, timestamp, relevance)
* final LLM reasoning
* conflict flag:
  * signals vs context disagreement

---

# UI Data Dependencies (from backend)

UI expects backend to eventually provide:

* recommendation core:
  * `symbol`
  * `score`
  * `decision`
  * `reason`
* explainability:
  * `signal_breakdown`
* RAG visibility:
  * `rag.enabled`
  * `rag.context_preview`
  * `rag.context_items`
* next prediction support:
  * `prediction.horizon`
  * `prediction.confidence`
  * `prediction.rank_bucket`

Detailed API contracts and sample payloads are in:

* `stock-agent/task/task_7.6_backend_api_plan.md`

---

# UI Development Sequence (After BE Work)

1. Finalize backend schema updates from Phase 7.6 backend plan.
2. Add mock fixtures matching final payload.
3. Build RAG Pipeline Panel in dashboard.
4. Add expanded prediction cards with `prediction` and `signal_breakdown`.
5. Build detail drawer/page for retrieved context and explainability.
6. Add status page subsystem cards from `/health`.
7. Validate loading, fallback, and missing-field behavior.

---

# Acceptance Criteria for UI Start

UI implementation should start once backend provides:

* stable `/suggest` extended payload OR temporary mock contract approved
* stable `/health` checks contract
* decision on `prediction` fields for "next prediction" display
