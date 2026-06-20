# 📘 Phase 2.8 — Model Benchmarking Framework

---

# 🎯 Objective

Establish a repeatable benchmarking framework to compare multiple LLMs for the Stock Recommendation Agent.

Move from:

```text
"I think Qwen performs well."
```

to:

```text
"Qwen performs better than Mistral by 8% recommendation accuracy while being 40% faster."
```

---

# 🧠 Why This Phase Matters

Current State:

```text
Single Model
 ↓
Recommendation
```

You have no objective way to determine:

```text
Which model is best?

Which model is fastest?

Which model hallucinates less?

Which model provides better recommendations?
```

---

After this phase:

```text
Qwen 2.5 3B
Accuracy = 74%

Mistral 7B
Accuracy = 79%

Llama 3.1 8B
Accuracy = 82%
```

and decisions become data-driven.

---

# Benchmark Architecture

```text
Evaluation Dataset
 ↓

Model Registry
 ↓

Benchmark Runner
 ↓

Metric Collection
 ↓

Model Comparison
 ↓

Benchmark Report
```

---

# 🧩 STEP 2.8.1 — Create Model Registry

Create:

```text
src/llm/model_registry.py
```

---

Purpose:

```text
Centralized model definitions.
```

---

Example:

```python
SUPPORTED_MODELS = [
    "qwen2.5:3b",
    "qwen2.5:7b",
    "mistral:7b",
    "llama3.1:8b",
    "phi4",
    "gemma3"
]
```

---

# 🧩 STEP 2.8.2 — Create Provider Abstraction

Create:

```text
src/llm/providers/
```

---

Define:

```python
class LLMProvider:
    async def generate(...)
```

---

Initial implementation:

```text
OllamaProvider
```

---

Future providers:

```text
OpenAIProvider

AnthropicProvider

GeminiProvider
```

---

# 🧩 STEP 2.8.3 — Reuse Evaluation Dataset

Input:

```text
evaluation/evaluation_dataset.json
```

from Phase 2.7.

---

Do NOT create a separate benchmark dataset.

---

Reason:

```text
Benchmarking must use the same evaluation criteria.
```

---

# 🧩 STEP 2.8.4 — Create Benchmark Runner

Create:

```text
evaluation/run_benchmark.py
```

---

Responsibilities:

```text
Load Models

Load Evaluation Dataset

Execute Full Pipeline

Collect Metrics

Generate Results
```

---

Flow:

```text
For Each Model
 ↓
For Each Query
 ↓
Execute Pipeline
 ↓
Store Results
```

---

# 🧩 STEP 2.8.5 — Recommendation Quality Metrics

Collect:

```text
Recommendation Accuracy

Grounding Accuracy

Signal Accuracy

Citation Accuracy

Hallucination Rate
```

---

Example:

```json
{
  "model": "qwen2.5:3b",
  "recommendation_accuracy": 0.74,
  "grounding_accuracy": 0.95
}
```

---

# 🧩 STEP 2.8.6 — Performance Metrics

Collect:

```text
Average Latency

P95 Latency

LLM Duration

Time To First Token

Tokens Per Second
```

---

Example:

```json
{
  "avg_latency_ms": 4200,
  "p95_latency_ms": 6700
}
```

---

# 🧩 STEP 2.8.7 — Resource Utilization Metrics

Collect:

```text
RAM Usage

CPU Usage

GPU Usage (Future)

Model Size
```

---

Useful for deployment decisions.

---

# 🧩 STEP 2.8.8 — Consistency Testing

Run:

```text
Same Query
10 Times
```

---

Measure:

```text
Recommendation Stability

Confidence Variance
```

---

Good Example:

```text
BUY
BUY
BUY
BUY
BUY
```

---

Bad Example:

```text
BUY
SELL
HOLD
BUY
SELL
```

---

# 🧩 STEP 2.8.9 — Hallucination Comparison

Measure:

```text
Unsupported Claims

Invalid Citations

Invented Facts
```

---

Output:

```json
{
  "hallucination_rate": 0.03
}
```

---

Target:

```text
< 5%
```

---

# 🧩 STEP 2.8.10 — Generate Benchmark Report

Create:

```text
evaluation/model_benchmark_report.md
```

---

Example:

| Model      | Accuracy | Latency | Hallucination | Consistency |
| ---------- | -------- | ------- | ------------- | ----------- |
| Qwen 3B    | 74%      | 4.2s    | 4%            | 92%         |
| Mistral 7B | 79%      | 6.8s    | 3%            | 95%         |
| Llama 8B   | 82%      | 11.4s   | 2%            | 97%         |

---

# 🧩 STEP 2.8.11 — Create Model Ranking Engine

Create:

```text
evaluation/model_ranking.py
```

---

Weighted Ranking:

```text
40% Recommendation Accuracy

25% Grounding Accuracy

15% Hallucination Rate

10% Consistency

10% Latency
```

---

Output:

```json
{
  "best_overall": "llama3.1:8b",
  "best_fast_model": "qwen2.5:3b",
  "best_accuracy_model": "llama3.1:8b"
}
```

---

# 🧩 STEP 2.8.12 — Baseline Storage

Create:

```text
evaluation/baselines/
```

---

Store:

```text
qwen2.5_3b.json

qwen2.5_7b.json

mistral7b.json

llama3_8b.json

phi4.json
```

---

Purpose:

```text
Track improvements over time.
```

---

# 🧩 STEP 2.8.13 — Frontend Benchmark Dashboard (Optional)

Add page:

```text
/frontend/benchmarks
```

---

Display:

```text
Model Rankings

Accuracy

Latency

Hallucination Rate

Recommendation Accuracy
```

---

Useful once multiple models are benchmarked.

---

# 🧪 Validation Checklist

Verify:

```text
✓ Model Registry Exists

✓ Provider Abstraction Exists

✓ Benchmark Runner Exists

✓ Recommendation Metrics Computed

✓ Grounding Metrics Computed

✓ Hallucination Metrics Computed

✓ Consistency Metrics Computed

✓ Benchmark Report Generated

✓ Model Rankings Generated
```

---

# 🚀 Deliverables

```text
src/llm/model_registry.py

src/llm/providers/

evaluation/run_benchmark.py

evaluation/model_ranking.py

evaluation/model_benchmark_report.md

evaluation/baselines/
```

---

# 🎯 Definition of Done

Running:

```bash
python evaluation/run_benchmark.py
```

produces:

```text
Model Rankings

Recommendation Accuracy

Grounding Accuracy

Hallucination Rate

Consistency Score

Latency Metrics
```

for all configured models.

---

# 📊 Expected Outcome

You can confidently answer:

```text
Which model should power production?

Which model is best for local deployment?

Which model provides the highest recommendation quality?

Which model offers the best accuracy-to-latency tradeoff?
```

using measurable evidence.

---

# 🔜 Next Step

After Phase 2.8 completes:

```text
Phase 2 Complete
```

Move to:

```text
Phase 3.1
Event Detection Engine
```

where the system begins transitioning from:

```text
User-driven recommendation system
```

to:

```text
Autonomous Market Intelligence Agent
```

that continuously monitors news, detects events, generates signals, and produces recommendations without requiring user queries.
