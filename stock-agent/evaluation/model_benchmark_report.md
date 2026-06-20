# Stock Agent Model Benchmarking Report

This report summarizes the comparative evaluations of multiple local LLM models against the golden evaluation dataset (60 Cases), ranking their overall suitability for the autonomous recommendation agent.

---

## 🏆 Model Leaderboard Rankings

| Rank | Model Name | Overall Score | Rec Accuracy | Grounding Accuracy | Hallucination Rate | Consistency | Avg (P95) Latency |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | **gemma3** | 85.8% | 81.4% | 96.4% | 2.3% | 97.6% | 7.88s (10.25s) |
| 2 | **mistral:7b** | 85.3% | 79.5% | 95.5% | 2.8% | 97.0% | 7.03s (9.14s) |
| 3 | **qwen2.5:3b** | 84.2% | 73.7% | 94.7% | 4.1% | 94.5% | 4.14s (5.38s) |
| 4 | **phi4** | 83.8% | 80.4% | 95.4% | 2.3% | 97.0% | 9.89s (12.86s) |
| 5 | **llama3.1:8b** | 83.6% | 82.3% | 97.3% | 1.9% | 98.2% | 12.21s (15.87s) |
| 6 | **mock** | 79.3% | 48.3% | 100.0% | 0.0% | 100.0% | 0.10s (0.06s) |

---

## 📊 Optimal Deployment Decisions

* **🏆 Best Overall Model:** `gemma3`
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
