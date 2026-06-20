# 📘 Phase 2.7 — Evaluation Framework

---

# 🎯 Objective

Establish a repeatable and measurable framework to evaluate the quality of the Stock Recommendation Agent.

Move from:

```text
"It looks good."
```

to:

```text
"We can measure how good it is."
```

---

# 🧠 Why This Phase Matters

Current State:

```text
Query
 ↓
Recommendation
```

The system produces recommendations but there is no objective way to answer:

```text
Was retrieval correct?

Was grounding correct?

Were signals extracted correctly?

Was the recommendation reasonable?

Did the model hallucinate?
```

---

After this phase:

```text
Retrieval Recall      = 87%

Grounding Accuracy    = 95%

Signal Accuracy       = 81%

Recommendation Score  = 74%

Hallucination Rate    = 2%
```

---

# Evaluation Architecture

```text
Evaluation Dataset
 ↓

Evaluation Runner
 ↓

Pipeline Execution
 ↓

Metric Collection
 ↓

Evaluation Report
```

---

# 🧩 STEP 2.7.1 — Create Golden Evaluation Dataset

Create:

```text
evaluation/
    evaluation_dataset.json
```

---

Dataset Structure

```json
{
  "symbol": "INFY",
  "query": "Recent business developments for INFY",
  "expected_grounded": true,
  "expected_recommendation": "BUY",
  "expected_signal_types": [
    "POSITIVE"
  ]
}
```

---

Initial Dataset Size

```text
50–100 Cases
```

---

Dataset Categories

### Positive Cases

```text
Strong Earnings

Large Contract Wins

Positive Guidance

Expansion Plans
```

---

### Negative Cases

```text
Profit Decline

Layoffs

Fraud Investigation

Weak Guidance
```

---

### Risk Cases

```text
War

Tariffs

Interest Rate Hikes

Supply Chain Issues
```

---

### Refusal Cases

```text
Mars Colony Queries

Unrelated Questions

Insufficient Evidence
```

---

# 🧩 STEP 2.7.2 — Retrieval Evaluation

Goal:

```text
Did we retrieve relevant evidence?
```

---

Metrics

### Recall@K

```text
Expected evidence retrieved?
```

---

### Precision@K

```text
Retrieved evidence useful?
```

---

Store

```json
{
  "recall_at_5": 0.87,
  "precision_at_5": 0.79
}
```

---

Target

```text
Recall@5 > 80%
```

---

# 🧩 STEP 2.7.3 — Grounding Evaluation

Goal:

```text
Did GroundingService make the correct decision?
```

---

Measure

```text
True Positive

False Positive

True Negative

False Negative
```

---

Example

Query:

```text
Will INFY build a colony on Mars?
```

Expected:

```text
REFUSE
```

---

Metrics

```text
Grounding Accuracy

Precision

Recall

F1 Score
```

---

# 🧩 STEP 2.7.4 — Signal Evaluation

Goal:

```text
Were correct signals generated?
```

---

Example

News:

```text
Revenue increased by 20%.
```

Expected Signal:

```text
POSITIVE
```

---

Metrics

```text
Signal Precision

Signal Recall

Signal F1
```

---

# 🧩 STEP 2.7.5 — Recommendation Evaluation

Goal:

```text
Did recommendation match expected outcome?
```

---

Example

```json
{
  "expected": "BUY",
  "actual": "BUY"
}
```

---

Metrics

```text
Recommendation Accuracy

Confusion Matrix
```

---

Track

```text
BUY Accuracy

SELL Accuracy

HOLD Accuracy
```

---

# 🧩 STEP 2.7.6 — Citation Evaluation

Goal:

```text
Ensure recommendations reference real evidence.
```

---

Validate

```text
Citation Exists

Citation Belongs To Context

Citation Not Hallucinated
```

---

Metrics

```text
Citation Accuracy

Hallucinated Citation Rate
```

---

# 🧩 STEP 2.7.7 — Consistency Evaluation

Goal:

```text
Determine recommendation stability.
```

---

Execute same query:

```text
10 Times
```

---

Example

Good:

```text
BUY
BUY
BUY
BUY
BUY
```

---

Bad:

```text
BUY
SELL
BUY
HOLD
SELL
```

---

Metrics

```text
Recommendation Consistency %

Confidence Variance
```

---

# 🧩 STEP 2.7.8 — Hallucination Evaluation

Goal:

```text
Detect fabricated facts.
```

---

Validate

```text
Reasoning References Evidence

No Unsupported Claims

No Invented Citations
```

---

Metrics

```text
Hallucination Rate %
```

---

Target

```text
< 5%
```

---

# 🧩 STEP 2.7.9 — Performance Evaluation

Collect

```text
Retrieval Time

Reranker Time

Grounding Time

Prompt Build Time

LLM Time

Total Time
```

---

Generate

```text
Average

P95

Max
```

---

# 🧩 STEP 2.7.10 — Create Evaluation Runner

Create:

```text
evaluation/run_evaluation.py
```

---

Responsibilities

```text
Load Dataset

Execute Pipeline

Collect Metrics

Generate Report
```

---

Output

```json
{
  "retrieval_recall": 0.87,
  "grounding_accuracy": 0.95,
  "signal_accuracy": 0.81,
  "recommendation_accuracy": 0.74,
  "hallucination_rate": 0.02
}
```

---

# 🧩 STEP 2.7.11 — Generate Evaluation Report

Create:

```text
evaluation_report.md
```

---

Include

```text
Overall Scores

Category Scores

Failures

Recommendations
```

---

Example

```text
Retrieval Recall: 87%

Grounding Accuracy: 95%

Signal Accuracy: 81%

Recommendation Accuracy: 74%

Hallucination Rate: 2%
```

---

# 🧩 STEP 2.7.12 — Baseline Storage

Create:

```text
evaluation/baselines/
```

Store:

```text
Qwen 2.5 3B Results

Future Model Results
```

---

Purpose

```text
Track improvements over time.
```

---

# 🧪 Validation Checklist

Verify:

```text
✓ Evaluation Dataset Exists

✓ Evaluation Runner Exists

✓ Retrieval Metrics Computed

✓ Grounding Metrics Computed

✓ Signal Metrics Computed

✓ Recommendation Metrics Computed

✓ Hallucination Metrics Computed

✓ Performance Metrics Computed

✓ Evaluation Report Generated
```

---

# 🚀 Deliverables

```text
evaluation/
    evaluation_dataset.json

evaluation/
    run_evaluation.py

evaluation/
    evaluation_report.md

evaluation/
    baselines/
```

---

# 🎯 Definition of Done

Running:

```bash
python evaluation/run_evaluation.py
```

produces:

```text
Retrieval Recall

Grounding Accuracy

Signal Accuracy

Recommendation Accuracy

Hallucination Rate

Performance Metrics
```

for the complete Stock Agent pipeline.

---

# 🔜 Next Step

After Phase 2.7:

```text
Phase 2.8
Model Benchmarking Framework
```

Compare:

```text
Qwen 2.5 3B

Mistral

Llama

Phi

Gemma
```

using the same evaluation dataset and metrics.

This allows model selection based on measurable performance rather than subjective observations.
