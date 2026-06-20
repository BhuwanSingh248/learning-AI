# Stock Agent Model Benchmarking Report

This report summarizes the comparative evaluations of multiple local LLM models against the golden evaluation dataset (60 Cases), ranking their overall suitability for the autonomous recommendation agent.

---

## 🏆 Model Leaderboard Rankings

| Rank | Model Name | Overall Score | Rec Accuracy | Grounding Accuracy | Hallucination Rate | Consistency | Avg (P95) Latency |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | **qwen2.5:3b** | 85.6% | 75.3% | 96.3% | 3.4% | 95.5% | 3.91s (5.09s) |
| 2 | **gemma3** | 85.5% | 81.1% | 96.1% | 2.5% | 97.4% | 8.00s (10.40s) |
| 3 | **mistral:7b** | 85.3% | 79.3% | 95.3% | 2.9% | 96.9% | 6.76s (8.78s) |
| 4 | **phi4** | 85.0% | 80.6% | 95.6% | 2.2% | 97.1% | 8.37s (10.88s) |
| 5 | **llama3.1:8b** | 84.1% | 82.8% | 97.8% | 1.6% | 98.5% | 12.07s (15.70s) |
| 6 | **mock** | 77.3% | 50.0% | 89.2% | 0.0% | 100.0% | 0.07s (0.06s) |

---

## 📊 Optimal Deployment Decisions

* **🏆 Best Overall Model:** `qwen2.5:3b`
  * *Rationale:* Selected based on the weighted formula prioritizing high recommendation accuracy, low hallucination risk, and stable decision consistency.
* **⚡ Best Fast Model (< 5s):** `qwen2.5:3b`
  * *Rationale:* Offers the highest quality tradeoff while maintaining latency bounds for real-time customer interactive requests.
* **🎯 Best Accuracy Model:** `llama3.1:8b`
  * *Rationale:* Maximizes investment recommendation alignment with historical market event outcomes.

---

## 🔬 Benchmark Methodology & Weights

The overall score is calculated as a weighted average of normalized metric scores:
* **40% Recommendation Accuracy:** Agreement rate with historical market outcomes.
* **25% Grounding Gate Accuracy:** Correctly allowing grounded queries and refusing ungrounded queries.
* **15% Hallucination Rate:** Frequency of hallucinated citations or stock symbols.
* **10% Consistency Score:** Decision consistency when repeating identical queries 10 times.
* **10% Latency Score:** Speed penalty for execution latency (linearly penalized up to 15s).
