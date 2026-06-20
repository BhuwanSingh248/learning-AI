# 📘 Phase 2.3 — Reasoning Engine

---

# 🎯 Objective

Convert grounded evidence into structured investment recommendations.

Current Flow:

```text
User Query
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
Grounding
 ↓
Prompt Builder
 ↓
LLM
 ↓
Raw Text
```

Target Flow:

```text
User Query
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
Grounding
 ↓
Prompt Builder
 ↓
LLM
 ↓
Reasoning Engine
 ↓
BUY / HOLD / SELL
 ↓
Structured Response
```

---

# 🧠 Why This Phase Matters

Currently the system can:

```text
Find Evidence
```

and

```text
Generate Text
```

But API consumers need:

```json
{
  "recommendation": "BUY",
  "confidence": 0.81,
  "reasoning": "...",
  "citations": [1,2]
}
```

instead of free-form LLM output.

---

# 🧩 STEP 2.3.1 — Create Recommendation Models

Create:

```text
src/reasoning/models.py
```

---

## RecommendationType Enum

Allowed values:

```python
BUY

HOLD

SELL

INSUFFICIENT_DATA
```

---

## RecommendationResponse

Fields:

```python
recommendation

confidence

reasoning

citations
```

---

## ReasoningResult

Fields:

```python
success

response

raw_llm_response
```

---

Purpose:

```text
Strong typing
```

throughout the reasoning layer.

---

# 🧩 STEP 2.3.2 — Create Reasoning Engine

Create:

```text
src/reasoning/reasoning_engine.py
```

---

Responsibilities:

```text
Prompt
 ↓
LLM
 ↓
Parse
 ↓
Validate
 ↓
RecommendationResponse
```

---

Not responsible for:

```text
Retrieval

Grounding

Prompt Construction
```

---

# 🧩 STEP 2.3.3 — Enforce JSON Output

Update prompt instructions.

The model must return:

```json
{
  "recommendation": "BUY",
  "confidence": 0.82,
  "reasoning": "Recent earnings exceeded expectations.",
  "citations": [1,2]
}
```

---

Avoid:

```text
Essay Responses
Markdown
Bullet Lists
```

---

Reason:

```text
API stability
```

---

# 🧩 STEP 2.3.4 — JSON Parsing Layer

Implement:

```text
LLM Output
 ↓
JSON Parse
 ↓
Pydantic Validation
```

---

Handle:

```text
Invalid JSON

Missing Fields

Unexpected Values
```

---

Fallback:

```json
{
  "recommendation": "INSUFFICIENT_DATA",
  "confidence": 0,
  "reasoning": "Unable to parse model response.",
  "citations": []
}
```

---

# 🧩 STEP 2.3.5 — Recommendation Validation

Allow ONLY:

```text
BUY

HOLD

SELL

INSUFFICIENT_DATA
```

---

Reject:

```text
STRONG_BUY

MAYBE

NEUTRAL
```

unless formally added later.

---

# 🧩 STEP 2.3.6 — Confidence Validation

Ensure:

```python
0 <= confidence <= 1
```

---

If:

```python
confidence < 0
```

set:

```python
0
```

---

If:

```python
confidence > 1
```

set:

```python
1
```

---

# 🧩 STEP 2.3.7 — Citation Validation

Ensure all citations returned by the model:

```python
[1,2,3]
```

exist in:

```python
CitationContext
```

---

Remove invalid citations.

---

Prevent:

```text
Hallucinated citation references
```

---

# 🧩 STEP 2.3.8 — Grounding Integration

If:

```python
grounded = False
```

Do NOT call the LLM.

---

Return:

```json
{
  "recommendation": "INSUFFICIENT_DATA",
  "confidence": 0,
  "reasoning": "Grounding failed.",
  "citations": []
}
```

---

Reason:

```text
Avoid hallucinations
```

---

# 🧩 STEP 2.3.9 — Metrics Integration

Measure:

```python
llm_duration_ms
```

around reasoning execution.

---

Capture:

```python
model_name

response_length
```

if available.

---

Store within:

```python
PipelineMetrics
```

---

# 🧩 STEP 2.3.10 — StockAgent Integration

Update orchestration:

```text
Grounding
 ↓
PromptBuilder
 ↓
ReasoningEngine
 ↓
RecommendationResponse
```

---

The API should no longer return:

```python
answer: str
```

---

Instead:

```python
recommendation

confidence

reasoning

citations
```

---

# 🧩 STEP 2.3.11 — API Response Cleanup

Current:

```json
{
  "answer": "{\"recommendation\":\"HOLD\"}"
}
```

Bad.

---

Target:

```json
{
  "recommendation": "HOLD",
  "confidence": 0.72,
  "reasoning": "...",
  "citations": [...]
}
```

---

Remove:

```text
Stringified JSON
```

responses.

---

# 🧩 STEP 2.3.12 — Unit Tests

Create:

```text
tests/reasoning/
```

---

Test Cases:

### Valid BUY

```json
{
  "recommendation": "BUY"
}
```

---

### Valid HOLD

```json
{
  "recommendation": "HOLD"
}
```

---

### Invalid Recommendation

```json
{
  "recommendation": "STRONG_BUY"
}
```

Expect:

```text
Validation Error
```

---

### Invalid JSON

Expect:

```text
Fallback Response
```

---

### Grounding Failure

Expect:

```json
{
  "recommendation": "INSUFFICIENT_DATA"
}
```

without LLM execution.

---

# 🧪 Validation Checklist

Verify:

```text
✓ Recommendation models created

✓ ReasoningEngine created

✓ JSON output enforced

✓ Parsing implemented

✓ Validation implemented

✓ Citation validation implemented

✓ Grounding integrated

✓ Metrics integrated

✓ API response cleaned

✓ Unit tests added
```

---

# 🚀 Deliverables

```text
src/reasoning/models.py

src/reasoning/reasoning_engine.py

RecommendationType Enum

RecommendationResponse

JSON Parser

Validation Layer

StockAgent Integration

Reasoning Tests
```

---

# 🎯 Definition of Done

Executing:

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys after recent earnings?"
}
```

returns:

```json
{
  "recommendation": "BUY",
  "confidence": 0.81,
  "reasoning": "Positive earnings growth and favorable outlook.",
  "citations": [1,2,3]
}
```

without exposing raw LLM output.

---

# 🔜 Next Step

After Phase 2.3 completes:

```text
End-to-End Validation
```

Validate:

```text
Retrieval
 ↓
Reranking
 ↓
Grounding
 ↓
Prompt Builder
 ↓
Reasoning Engine
 ↓
API Response
```

Only after successful validation should we proceed to:

```text
Phase 2.4
Advanced Recommendation Scoring
```

which introduces:

```text
Historical Signals

Technical Indicators

Risk Scoring

Portfolio Context
```
