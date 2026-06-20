# 📘 Phase 2.4 — Signal Engine & Recommendation Scoring

---

# 🎯 Objective

Move from:

```text
LLM Opinion
```

to:

```text
Evidence-Based Recommendation
```

by introducing explicit signals that contribute to BUY / HOLD / SELL decisions.

---

# 🧠 Why This Phase Matters

Current:

```text
News
 ↓
LLM
 ↓
BUY
```

Problem:

```text
Difficult to explain

Difficult to debug

Difficult to improve
```

---

Target:

```text
News
 ↓

Signal Generation
 ├─ Positive Signals
 ├─ Negative Signals
 ├─ Risk Signals
 └─ Market Signals

 ↓

Recommendation Score
 ↓

BUY / HOLD / SELL
```

---

# 🧩 STEP 2.4.1 — Create Signal Models

Create:

```text
src/signals/models.py
```

---

## SignalType

```python
POSITIVE

NEGATIVE

RISK

MARKET
```

---

## Signal

Fields:

```python
signal_type

title

description

score

citation_ids
```

---

Example:

```json
{
  "signal_type": "POSITIVE",
  "title": "Strong Earnings",
  "score": 0.25
}
```

---

# 🧩 STEP 2.4.2 — Create Signal Extraction Engine

Create:

```text
src/signals/signal_engine.py
```

---

Input:

```text
Grounded Context
```

Output:

```python
List[Signal]
```

---

Responsibilities:

```text
Identify positive events

Identify negative events

Identify risk events
```

---

Examples:

### Positive

```text
Revenue growth

Margin expansion

New contracts

Acquisitions
```

---

### Negative

```text
Profit decline

Regulatory issues

Executive exits

Weak guidance
```

---

### Risk

```text
War

Tariffs

Interest rates

Supply chain disruption
```

---

# 🧩 STEP 2.4.3 — Signal Scoring

Assign weights.

Example:

```python
Positive = +1

Negative = -1

Risk = -0.5
```

---

Store:

```python
signal.score
```

---

Initial implementation may be rule-based.

---

# 🧩 STEP 2.4.4 — Recommendation Score Calculator

Create:

```text
src/signals/scoring.py
```

---

Calculate:

```python
total_score = sum(signal.score)
```

---

Example:

```text
Strong Earnings      +1

New Contract         +1

War Risk             -0.5

Total = 1.5
```

---

# 🧩 STEP 2.4.5 — Recommendation Thresholds

Initial thresholds:

```python
score >= 2
→ BUY

-1 < score < 2
→ HOLD

score <= -1
→ SELL
```

---

Make configurable.

---

# 🧩 STEP 2.4.6 — Confidence Calculation

Confidence should NOT come directly from LLM.

---

Calculate from:

```text
Number of Signals

Signal Strength

Grounding Confidence

Evidence Quality
```

---

Example:

```python
confidence = 0.78
```

---

# 🧩 STEP 2.4.7 — LLM as Analyst, Not Judge

Change LLM role.

Current:

```text
LLM decides BUY
```

---

Future:

```text
LLM extracts signals

System calculates recommendation
```

---

Benefits:

```text
More deterministic

More explainable

More auditable
```

---

# 🧩 STEP 2.4.8 — Recommendation Explanation

Return:

```json
{
  "recommendation": "BUY",
  "confidence": 0.82,
  "signals": [
    {
      "title": "Strong Earnings",
      "score": 1.0
    },
    {
      "title": "New Government Contract",
      "score": 1.0
    }
  ]
}
```

---

# 🧩 STEP 2.4.9 — Metrics Integration

Capture:

```python
signal_count

positive_signal_count

negative_signal_count

risk_signal_count
```

---

Store in:

```python
PipelineMetrics.additional_data
```

---

# 🧩 STEP 2.4.10 — API Integration

Flow becomes:

```text
Grounding
 ↓
Prompt Builder
 ↓
Reasoning Engine
 ↓
Signal Engine
 ↓
Recommendation Score
 ↓
Response
```

---

# 🧪 Validation Checklist

Verify:

```text
✓ Signal Models

✓ Signal Engine

✓ Signal Scoring

✓ Recommendation Thresholds

✓ Confidence Calculation

✓ Metrics Integration

✓ API Integration
```

---

# 🚀 Deliverables

```text
src/signals/models.py

src/signals/signal_engine.py

src/signals/scoring.py

Signal Tests

Recommendation Thresholds

Signal Metrics
```

---

# 🎯 Definition of Done

Input:

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys?"
}
```

Output:

```json
{
  "recommendation": "BUY",
  "confidence": 0.81,
  "signals": [
    {
      "title": "Strong Earnings",
      "score": 1.0
    },
    {
      "title": "Positive Guidance",
      "score": 1.0
    }
  ],
  "citations": [1,2]
}
```

---

# 🔜 Next Step

After Phase 2.4:

```text
Phase 2.5
Historical Event Learning
```

Where the system starts answering:

```text
A similar event happened before.

What happened to the stock then?
```

which aligns directly with your earlier vision:

```text
News
 ↓
Impact Analysis
 ↓
Similar Historical Events
 ↓
Signal Generation
 ↓
Recommendation
```
