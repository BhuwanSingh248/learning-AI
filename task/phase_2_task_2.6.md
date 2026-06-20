# 📘 Phase 2.6 — End-to-End Recommendation Pipeline Validation

---

# 🎯 Objective

Validate the complete recommendation pipeline from query submission to final recommendation response.

This phase focuses on:

```text
Integration

Verification

Reliability

Observability
```

NOT new AI capabilities.

---

# 🧠 Why This Phase Matters

Individual components may work independently.

However:

```text
Working Components
≠
Working System
```

---

Need to verify:

```text
Retrieval
 ↓
Reranker
 ↓
Grounding
 ↓
Prompt Builder
 ↓
Reasoning Engine
 ↓
Signal Engine
 ↓
Recommendation Response
```

works end-to-end.

---

# Current Target Flow

```text
User Query
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
Grounding
 ↓

ALLOW?
 ├── YES
 │    ↓
 │ Prompt Builder
 │    ↓
 │ Reasoning Engine
 │    ↓
 │ Signal Engine
 │    ↓
 │ Recommendation
 │
 └── NO
      ↓
      INSUFFICIENT_DATA
```

---

# 🧩 STEP 2.6.1 — Create Test Dataset

Create:

```text
tests/e2e/test_queries.json
```

---

Include:

### Strong Queries

```json
{
  "symbol": "INFY",
  "query": "Recent business developments for INFY"
}
```

---

### Weak Queries

```json
{
  "symbol": "INFY",
  "query": "Will INFY build a colony on Mars?"
}
```

---

### Neutral Queries

```json
{
  "symbol": "INFY",
  "query": "Should I buy INFY?"
}
```

---

Target:

```text
20-50 queries
```

---

# 🧩 STEP 2.6.2 — Validate Retrieval

For each query verify:

```text
Chunks Retrieved > 0
```

for relevant questions.

---

Capture:

```text
retrieval_duration_ms
```

---

Failure Cases:

```text
No chunks found

Wrong symbol

Empty result set
```

---

# 🧩 STEP 2.6.3 — Validate Reranker

Verify:

```text
Scores generated
```

---

Check:

```text
Best score

Average score
```

---

Ensure:

```text
Relevant query
 >
 Irrelevant query
```

in score distribution.

---

# 🧩 STEP 2.6.4 — Validate Grounding

Test:

### Strong Context

Expect:

```text
ALLOW
```

---

### Weak Context

Expect:

```text
REFUSE
```

---

Verify:

```text
No hallucination path exists.
```

---

# 🧩 STEP 2.6.5 — Validate Prompt Builder

For grounded queries:

Verify:

```text
Prompt generated
```

---

Check:

```text
Context Included

Citations Included

Question Included
```

---

No empty prompts.

---

# 🧩 STEP 2.6.6 — Validate Reasoning Engine

Verify:

```json
{
  "recommendation": "...",
  "confidence": ...,
  "reasoning": "...",
  "citations": [...]
}
```

is always returned.

---

No:

```text
Raw LLM Output

Malformed JSON
```

---

# 🧩 STEP 2.6.7 — Validate Signal Engine

Verify:

```text
Signals Generated
```

for:

```text
Positive News

Negative News

Risk Events
```

---

Check:

```text
Signal Counts

Signal Scores
```

---

# 🧩 STEP 2.6.8 — Validate Final Recommendation

Only allow:

```text
BUY

HOLD

SELL

INSUFFICIENT_DATA
```

---

No unexpected values.

---

# 🧩 STEP 2.6.9 — API Response Audit

Review:

```http
POST /analyze
```

---

Verify:

Current bad pattern:

```json
{
  "answer": "{\"recommendation\":\"BUY\"}"
}
```

---

Target:

```json
{
  "recommendation": "BUY",
  "confidence": 0.81,
  "reasoning": "...",
  "citations": [...]
}
```

---

Eliminate:

```text
Stringified JSON
```

responses.

---

# 🧩 STEP 2.6.10 — Metrics Validation

Ensure:

```text
retrieval_duration_ms

reranker_duration_ms

grounding_duration_ms

prompt_build_duration_ms

llm_duration_ms
```

are populated.

---

Verify:

```text
No null values
```

for successful requests.

---

# 🧩 STEP 2.6.11 — Failure Scenario Testing

Test:

### No News

```text
Unknown Symbol
```

---

### Weak Evidence

```text
Mars Colony Query
```

---

### Empty Query

```text
""
```

---

### Invalid Symbol

```text
XYZ_INVALID
```

---

Expected:

```text
Graceful Failure
```

No crashes.

---

# 🧩 STEP 2.6.12 — Create Validation Report

Generate:

```text
phase_2_6_validation_report.md
```

---

Include:

```text
Passed Tests

Failed Tests

Recommendations

Known Gaps
```

---

# 🧪 Validation Checklist

Verify:

```text
✓ Retrieval Working

✓ Reranker Working

✓ Grounding Working

✓ Prompt Builder Working

✓ Reasoning Engine Working

✓ Signal Engine Working

✓ Recommendation Returned

✓ Metrics Returned

✓ Failure Cases Handled
```

---

# 🚀 Deliverables

```text
tests/e2e/test_queries.json

tests/e2e/

phase_2_6_validation_report.md
```

---

# 🎯 Definition of Done

Execute:

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys after recent earnings?"
}
```

and receive:

```json
{
  "recommendation": "BUY",
  "confidence": 0.81,
  "reasoning": "...",
  "signals": [...],
  "citations": [...]
}
```

with:

```text
Grounded Evidence

Valid JSON

No Hallucinations

Metrics Available
```

---

# 🔜 Next Step

After successful validation:

```text
Phase 2.7
Evaluation Framework
```

Where we begin measuring:

```text
Recommendation Accuracy

Grounding Accuracy

Signal Quality

Model Quality
```

instead of just verifying functionality.
