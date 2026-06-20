# Stock Agent Evaluation & Calibration Report

* **Evaluation Date:** 2026-06-20 23:15:34
* **Evaluation Mode:** MOCK/SIMULATION (mock)
* **Validation Standard:** Golden Evaluation Dataset (60 Cases)

---

## 📈 Quality Metrics Scorecard

| Metric | Score | Target / Acceptable Range | Status |
| :--- | :---: | :---: | :---: |
| **Retrieval Recall** | 98.4% | > 80% | ✅ Met |
| **Retrieval Precision** | 100.0% | - | Info |
| **Grounding Gate Accuracy** | 100.0% | > 90% | ✅ Met |
| **Grounding Precision** | 100.0% | - | Info |
| **Grounding Recall (Gate)** | 100.0% | - | Info |
| **Grounding F1 Score** | 100.0% | - | Info |
| **Signal Extraction Precision** | 60.0% | > 80% | ⚠️ Low |
| **Signal Extraction Recall** | 80.0% | - | Info |
| **Recommendation Accuracy** | 48.3% | > 70% | ⚠️ Low |
| **Citation Hallucination Rate** | 0.0% | < 5% | ✅ Safe |
| **Fact/Symbol Hallucination Rate** | 0.0% | < 5% | ✅ Safe |

---

## 🔀 Recommendation Confusion Matrix

| Expected \ Predicted | BUY | HOLD | SELL | INSUFFICIENT_DATA | Matches / Total | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **BUY** | 0 | 15 | 0 | 0 | 0 / 15 | 0.0% |
| **HOLD** | 0 | 0 | 0 | 0 | 0 / 0 | 0.0% |
| **SELL** | 0 | 16 | 14 | 0 | 14 / 30 | 46.7% |
| **INSUFFICIENT_DATA** | 0 | 0 | 0 | 15 | 15 / 15 | 100.0% |

---

## 🔁 Consistency Metrics Profile (Stability Check)

Each consistency query was run **10 times** to verify decision boundary stability:

1. **Grounded INFY Positive Query:**
   * Query: `Recent business developments and Q4 earnings reports for Infosys`
   * Consistency: **100.0%** (Most frequent decision: `HOLD`)
   * Confidence Variance: `0.000000`
2. **Grounded AAPL Positive Query:**
   * Query: `Apple solid earnings growth and AI updates`
   * Consistency: **100.0%** (Most frequent decision: `HOLD`)
   * Confidence Variance: `0.000000`
3. **Refusal Mars Query:**
   * Query: `Will Infosys build a city on Mars next year?`
   * Consistency: **100.0%** (Most frequent decision: `INSUFFICIENT_DATA`)
   * Confidence Variance: `0.000000`

---

## ⏱️ Latency & Performance Analysis

All latency metrics are expressed in milliseconds (ms) over the full 60-query run:

* **Overall Execution Time:**
  * Average: **96.2ms**
  * 95th Percentile: **61.9ms**
  * Max: **3467.3ms**
* **Sub-Stage Durations (Average / P95):**
  * Retrieval Stage: `10.8ms` / `16.5ms`
  * Reranker Stage: `72.2ms` / `24.5ms`
  * Grounding Gate Stage: `0.1ms` / `<1ms`
  * LLM Query Stage: `0.0ms` / `0.1ms`

---

## 💡 Recommendations for Calibration (Phase 2.7 Outcome)

1. **Threshold Settings:** The Grounding Gate successfully filtered 100% of the Mars/cookie/capital questions without querying the LLM, showing the thresholds of `-5.0` (best) and `-9.0` (average) are properly set for this embedding/reranker combination.
2. **Signal Blending Balance:** Blending historical risk markers (e.g. SVB collapse) into current stock evaluations adds high-quality perspective but requires careful weighting to prevent holding decisions during predominantly positive growth trends.
