# 📘 Phase 2.5 — Historical Event Learning & Analog Analysis

---

# 🎯 Objective

Enhance recommendation quality by allowing the system to learn from similar historical events.

Move from:

```text id="7zvqnk"
Current News
 ↓
Signal Engine
 ↓
Recommendation
```

to:

```text id="y0xq44"
Current News
 ↓
Signal Engine
 ↓
Historical Similar Events
 ↓
Historical Outcomes
 ↓
Recommendation
```

---

# 🧠 Why This Phase Matters

Today the system can answer:

```text id="1j7aop"
What is happening now?
```

---

After this phase the system can answer:

```text id="6t85r3"
Has something similar happened before?

What happened afterward?

How did the stock react?

How did the sector react?
```

---

# Example

Current News:

```text id="z1dr8k"
US increases tariffs on Chinese imports
```

---

System should discover:

```text id="g67phg"
Similar Event:
US-China Trade War (2018)

Outcome:
IT sector neutral

Manufacturing sector negative

Export companies impacted
```

---

Recommendation becomes:

```text id="d3az5u"
Evidence + Historical Analogy
```

rather than evidence alone.

---

# 🧩 STEP 2.5.1 — Create Historical Event Models

Create:

```text id="4ntzbt"
src/history/models.py
```

---

## HistoricalEvent

Fields:

```python id="ix6on5"
event_id

title

description

event_date

sector

impact_score
```

---

## HistoricalOutcome

Fields:

```python id="plu5z0"
event_id

stock_symbol

return_1d

return_7d

return_30d

return_90d
```

---

# 🧩 STEP 2.5.2 — Create Event Store

Create:

```text id="0x9w3f"
src/history/event_store.py
```

---

Purpose:

```text id="szhmql"
Store historical market events
```

Examples:

```text id="kzxg77"
COVID Crash

Russia-Ukraine War

US-China Trade War

Banking Crisis

Major Elections

Interest Rate Hikes
```

---

Initially:

```text id="uz8sph"
Manual Dataset
```

---

No automatic ingestion yet.

---

# 🧩 STEP 2.5.3 — Event Embeddings

Create embeddings for:

```text id="b30yxe"
Event Description
```

---

Store:

```text id="3z9hsm"
FAISS
```

or

```text id="1tjlwm"
Historical Event Index
```

---

Purpose:

```text id="bqwt1o"
Semantic Event Similarity
```

---

# 🧩 STEP 2.5.4 — Similar Event Retriever

Create:

```text id="4t3pxj"
src/history/event_retriever.py
```

---

Input:

```text id="zkchpd"
Current Signals

Current News
```

---

Output:

```python id="zjlwmf"
List[HistoricalEvent]
```

---

Example:

```text id="2xjlwm"
War
 ↓
Retrieve:
Russia-Ukraine War
```

---

# 🧩 STEP 2.5.5 — Outcome Analyzer

Create:

```text id="jlwm4f"
src/history/outcome_analyzer.py
```

---

Calculate:

```text id="7vkl8h"
Average Stock Movement

Sector Movement

Index Movement
```

---

Across:

```text id="84j9r8"
1 Day

7 Day

30 Day

90 Day
```

---

# 🧩 STEP 2.5.6 — Sector-Level Learning

Create:

```text id="d6m2ap"
SectorImpact
```

---

Examples:

### War

```text id="k0bqk4"
Defense
Positive

Airlines
Negative

Oil
Positive
```

---

### Rate Hike

```text id="4mjlwm"
Banks
Positive

Growth Stocks
Negative
```

---

# 🧩 STEP 2.5.7 — Historical Signal Generation

Generate:

```python id="ibx9ks"
HistoricalSignal
```

---

Example:

```json id="z8v1z0"
{
  "title": "Similar Trade War Event",
  "score": -0.7,
  "historical_confidence": 0.82
}
```

---

These signals should join:

```text id="9jw5ec"
Positive Signals

Negative Signals

Risk Signals
```

---

# 🧩 STEP 2.5.8 — Recommendation Integration

Flow becomes:

```text id="jex5vt"
News
 ↓

Signal Engine
 ↓

Historical Event Retriever
 ↓

Historical Signals
 ↓

Recommendation Score
 ↓

BUY/HOLD/SELL
```

---

# 🧩 STEP 2.5.9 — Explainability

Return:

```json id="0gv8m5"
{
  "historical_matches": [
    {
      "event": "US-China Trade War",
      "similarity": 0.84,
      "observed_outcome": "Manufacturing stocks fell 8%"
    }
  ]
}
```

---

Users should understand:

```text id="5cjlwm"
Why recommendation was generated.
```

---

# 🧩 STEP 2.5.10 — Metrics

Capture:

```python id="jlwm8r"
historical_matches_found

average_similarity

historical_signal_count
```

---

Store:

```python id="cjlwm9"
PipelineMetrics.additional_data
```

---

# 🧩 STEP 2.5.11 — Initial Dataset

Create:

```text id="mjlwm0"
data/historical_events.json
```

---

Include:

```text id="cjlwm1"
COVID Crash

Russia-Ukraine War

US-China Trade War

Silicon Valley Bank Collapse

Major Rate Hikes

Major Elections
```

---

Small dataset first.

---

# 🧪 Validation Checklist

Verify:

```text id="wjlwm2"
✓ HistoricalEvent models

✓ Event Store

✓ Event Embeddings

✓ Similar Event Retrieval

✓ Outcome Analysis

✓ Historical Signals

✓ Recommendation Integration

✓ Explainability
```

---

# 🚀 Deliverables

```text id="zjlwm3"
src/history/models.py

src/history/event_store.py

src/history/event_retriever.py

src/history/outcome_analyzer.py

historical_events.json

Historical Signal Tests
```

---

# 🎯 Definition of Done

Input:

```text id="mjlwm4"
New tariff announcement
```

---

System Response:

```json id="njlwm5"
{
  "recommendation": "SELL",
  "confidence": 0.76,
  "signals": [...],
  "historical_matches": [
    {
      "event": "US-China Trade War",
      "similarity": 0.88
    }
  ],
  "reasoning": "A similar event occurred previously and negatively impacted export-focused companies."
}
```

---

# 🔜 Next Step

After Phase 2.5:

```text id="pjlwm6"
Phase 2.6
Autonomous Market Monitoring
```

This is where the system starts doing what you originally envisioned:

```text id="qjlwm7"
News arrives
 ↓
No user query required
 ↓
Impact Analysis
 ↓
Historical Comparison
 ↓
Signal Generation
 ↓
Recommendation
 ↓
Notification
```

and begins acting like a market analyst instead of a question-answering system.
