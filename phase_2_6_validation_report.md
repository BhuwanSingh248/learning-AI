# Phase 2.6: End-to-End Recommendation Pipeline Validation Report

This report documents the validation of the complete stock recommendation pipeline, verifying integration, reliability, and correctness across all components (Retrieval, Reranker, Grounding, Prompt Builder, Reasoning Engine, Signal Engine, and final API serialization).

---

## 🎯 Executive Summary

* **Validation Status:** **PASSED** (100% test success rate).
* **Test Dataset Size:** 20 parameterized end-to-end query scenarios + 1 debug endpoint integration test (total 21 test conditions).
* **Robustness & Safe Refusals:** No 500 crashes occurred. Queries violating grounding constraints were gracefully refused with HTTP `200` status codes and `INSUFFICIENT_DATA` recommendations.
* **Response Integrity:** Zero instances of stringified JSON in public `/analyze` responses; fields are correctly serialized according to the Pydantic schemas.

---

## ⚙️ Pipeline Components Validated

### 1. Hybrid Retrieval & Reranking
* **Functionality:** Combines semantic (FAISS) and keyword-based (BM25) search, neural reranking with a cross-encoder model, and deduplication.
* **Timings:** Successfully tracked on the `metrics` object as `retrieval_duration_ms` and `reranker_duration_ms`.

### 2. Grounding Gate
* **Rules Checked:** 
  * Minimum score thresholds (best score >= -5.0, average score >= -9.0)
  * Minimum candidate count >= 1 chunk
* **Grounded Path (ALLOW):** Relevant queries successfully bypass refusal, proceeding to LLM signal extraction.
* **Ungrounded Path (REFUSE):** Irrelevant queries (e.g., Space colonies, cookies) are refused immediately, bypassing LLM invocation to prevent hallucination.

### 3. Reasoning & Signal Engines
* **Structure:** The LLM's response is structured, parsed into individual signals, scored (POSITIVE = 1.0, NEGATIVE = -1.0, RISK = -0.5), blended with historical events, and aggregated.
* **Deterministic Calculations:** Recommendations (BUY/HOLD/SELL) and confidence scores are calculated deterministically on the system side.
* **Debug Support:** The `/debug/analyze` endpoint outputs raw prompts, recommendation summaries, and stage-by-stage latency metrics.

---

## 📊 Summary of Test Scenarios

| Category | Query Scenario Example | Expected Grounded | Expected Recommendation | Actual Recommendation | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Strong** | "Recent business developments and earnings reports for Infosys" | `True` | `BUY` | `BUY` | **Passed** |
| **Strong** | "Apple solid earnings growth and AI updates" | `True` | `BUY` | `BUY` | **Passed** |
| **Weak** | "Will Infosys build a city on Mars next year?" | `False` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | **Passed** |
| **Weak** | "How to make a chocolate chip cookie at home?" | `False` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | **Passed** |
| **Neutral**| "Should I buy Infosys stock right now?" | `True` | `BUY` | `BUY` | **Passed** |
| **Neutral**| "Is Apple stock a buy or sell after recent movements?" | `True` | `BUY` | `BUY` | **Passed** |
| **Failure**| `""` (Empty query) | `False` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | **Passed** |
| **Failure**| `"XYZ_INVALID"` (Invalid Symbol) | `False` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | **Passed** |

---

## 📈 Latency & Performance Breakdown

Under simulated load, stage-by-stage latency timings were recorded on the response object's `metrics` field:

* **Retrieval (`retrieval_duration_ms`):** ~2ms to 10ms (highly optimized vector-to-metadata queries).
* **Reranker (`reranker_duration_ms`):** ~10ms to 20ms (running lightweight cross-encoder local model).
* **Grounding (`grounding_duration_ms`):** < 1ms.
* **Prompt Builder (`prompt_build_duration_ms`):** < 1ms.
* **LLM Engine (`llm_duration_ms`):** Simulated via patches to run synchronously in ~1ms (production relies on local Ollama execution).

---

## 🛠️ Known Gaps & Next Steps (Phase 2.7)

* **Signal Calibration:** Currently, weights are fixed (+1.0, -1.0, -0.5). In Phase 2.7, we will configure an **Evaluation Framework** to assess whether these weights yield accurate recommendations against historical stock market data.
* **Embedding/Reranker Tuning:** Reranker scoring thresholds will be further calibrated using performance metric datasets to find the optimal trade-off between false-positives and false-negatives in grounding gates.
