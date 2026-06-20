# Phase 3.3 — Outcome Tracking Engine

## Objective

Track actual market outcomes after detected events.

This transforms:

```text
Event
```

into:

```text
Event
+
Observed Market Behavior
```

---

### Example

Event:

```text
Russia Ukraine War
```

Observed:

```json
{
  "event_id": "ukraine_war",
  "nifty_return_1d": -2.1,
  "nifty_return_7d": -4.3,
  "oil_return_7d": 11.8,
  "it_sector_return_30d": -3.2
}
```

---

### Track

#### Market Indexes

```text
NIFTY 50

SENSEX

NASDAQ

S&P 500
```

---

#### Sectors

```text
Banking

IT

Pharma

Energy

Manufacturing

Defense
```

---

#### Stocks

```text
Affected Companies
```

---

### Time Horizons

Store:

```text
1 Day

7 Day

30 Day

90 Day

180 Day
```

returns.

---

### Storage

```text
event_outcomes
```

table.

---

# Phase 3.4 — Historical Memory Engine

## Objective

Create institutional memory.

---

Flow:

```text
New Event
 ↓
Similarity Search
 ↓
Historical Events
 ↓
Historical Outcomes
```

---

Example

Current Event:

```text
New US-China Tariffs
```

---

Retrieve:

```text
2018 Trade War

2020 Trade Restrictions

2022 Semiconductor Restrictions
```

---

Compute:

```text
Average Market Outcome

Average Sector Outcome

Average Stock Outcome
```

---

### Components

Create:

```text
src/history/
```

---

Potential modules:

```text
event_memory_store.py

event_similarity.py

event_retriever.py

outcome_analyzer.py
```

---

# Phase 3.5 — Historical Signal Generator

## Objective

Convert historical outcomes into recommendation signals.

---

Example:

Historical Result:

```text
Trade Wars

Manufacturing
Average -8%
```

---

Generate:

```json
{
  "signal_type": "HISTORICAL",
  "title": "Trade War Analogy",
  "score": -0.8,
  "confidence": 0.84
}
```

---

These signals become first-class citizens alongside:

```text
Positive Signals

Negative Signals

Risk Signals
```

from Phase 2.4.

---

# Phase 3.6 — Autonomous Recommendation Engine

## Objective

Generate recommendations without a user query.

---

Flow:

```text
News Arrives
 ↓
Event Detection
 ↓
Signal Generation
 ↓
Historical Comparison
 ↓
Recommendation Scoring
 ↓
BUY / HOLD / SELL
```

---

Output:

```json
{
  "symbol": "INFY",
  "recommendation": "BUY",
  "confidence": 0.82,
  "reason": "Positive AI spending trend combined with historical analog events."
}
```

---

# Phase 3.7 — Notification Engine

## Objective

Notify users only when confidence exceeds a threshold.

---

Example:

```text
Confidence > 0.80
```

Trigger:

```text
Email

Push Notification

Slack

Telegram
```

---

Avoid:

```text
Notification Spam
```

---

# Phase 3.8 — Knowledge Graph (Future)

## Objective

Model relationships between:

```text
Events

Countries

Commodities

Indexes

Sectors

Stocks
```

---

Example:

```text
War
 ↓

Oil ↑
 ↓

Transportation ↓

Airlines ↓

Defense ↑
```

---

Potential Technologies:

```text
Neo4j

Memgraph

NetworkX
```

---

# Phase 3.9 — Self-Learning Outcome Calibration

## Objective

Continuously improve recommendation quality.

---

Flow:

```text
Recommendation Generated
 ↓
Wait 30 Days
 ↓
Observe Actual Outcome
 ↓
Compare
 ↓
Adjust Weights
```

---

Example:

```text
System Predicted BUY

Stock Fell 12%

Confidence Calibration Updated
```

---

# Expected Architecture

```text
News
 ↓
Event Detection
 ↓
Event Clustering
 ↓
Historical Memory
 ↓
Outcome Tracking
 ↓
Historical Signals
 ↓
Signal Engine
 ↓
Recommendation Scoring
 ↓
BUY / HOLD / SELL
 ↓
Notification
```

---

# Success Criteria

The system can answer:

```text
What is happening now?
```

AND

```text
Has this happened before?
```

AND

```text
What happened then?
```

AND

```text
What should we do now?
```

without requiring a user query.

---

# Notes

This backlog item should NOT be started until:

```text
✓ Phase 2.3 Reasoning Engine complete

✓ Phase 2.4 Signal Engine complete

✓ End-to-End Recommendation Flow validated
```

Reason:

```text
Phase 3 enhances recommendations.

Phase 2 creates recommendations.
```

The foundation must exist before the intelligence layer is built.
