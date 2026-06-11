# 📘 Epic: Autonomous Market Intelligence Agent (Future Phase)

## Status

```text
BACKLOG
Priority: HIGH
Target Phase: After Observability & Evaluation
```

---

# 🎯 Vision

Transform the current AI Stock Assistant from a reactive system into a proactive market research agent.

Current System:

```text
User
 ↓
Ask Question
 ↓
RAG + LLM
 ↓
Answer
```

Future System:

```text
News Arrives
 ↓
Event Analysis
 ↓
Impact Detection
 ↓
Signal Generation
 ↓
Recommendation
 ↓
Notification
```

The system should identify opportunities and risks before a user explicitly asks.

---

# 🧠 Business Goal

Replicate the workflow of a professional market researcher:

1. Read business news continuously
2. Detect significant events
3. Determine affected sectors
4. Determine affected stocks
5. Validate using technical indicators
6. Compare against historical events
7. Generate recommendations
8. Notify users only when confidence is high

---

# 🏗 High-Level Architecture

```text
News Feed
 ↓
Event Detection Engine
 ↓
Impact Analysis Engine
 ↓
Sector Mapping Engine
 ↓
Stock Mapping Engine
 ↓
Historical Event Retrieval
 ↓
Technical Validation Engine
 ↓
Recommendation Engine
 ↓
Confidence Engine
 ↓
Notification Engine
```

---

# Phase A — Event Detection Engine

## Objective

Convert raw news into structured events.

Example:

```text
Russia escalates conflict
```

↓

```json
{
  "event_type": "WAR",
  "severity": "HIGH",
  "region": "EUROPE"
}
```

---

## Event Categories

* War / Geopolitical Conflict
* Interest Rate Changes
* Inflation Events
* Tariff Announcements
* Government Regulation
* Earnings Surprises
* Commodity Price Shocks
* Supply Chain Disruptions
* Currency Movements
* Natural Disasters

---

# Phase B — Impact Analysis Engine

## Objective

Determine how an event affects the market.

Example:

```text
War
```

↓

```text
Oil ↑
Gold ↑
Defense ↑
Airlines ↓
Logistics ↓
```

---

## Techniques

* LLM Reasoning
* Rule-Based Logic
* Knowledge Graph Relationships

---

# Phase C — Sector Mapping Engine

## Objective

Map impacts to market sectors.

Example:

```text
Oil Price Increase
```

↓

```text
Positive:
Oil & Gas

Negative:
Airlines
Paint
Chemicals
```

---

# Phase D — Stock Mapping Engine

## Objective

Convert sector impacts into stock candidates.

Example:

```text
Oil & Gas
```

↓

```text
ONGC
Oil India
Reliance
```

---

## Scope

Initially:

```text
Global Event
 ↓
Indian Market Impact
```

Future:

```text
Global Event
 ↓
Global Market Impact
```

---

# Phase E — Historical Event Retrieval

## Objective

Find similar events from the past.

Example:

```text
Current Event:
Oil Supply Disruption
```

↓

Search:

```text
Historical Oil Supply Disruptions
```

---

## Questions

* What happened previously?
* Which sectors benefited?
* Which sectors suffered?
* How long did impact last?

---

## Data Sources

* News Archive
* Existing RAG System
* Historical Market Data

---

# Phase F — Technical Validation Engine

## Objective

Confirm news-based signals using market data.

---

## Validation Inputs

* Trend Direction
* Volume
* RSI
* MACD
* Moving Averages
* Volatility

---

Example:

```text
Positive News
+
Volume Breakout
+
Trend Confirmation
```

↓

Higher Confidence

---

# Phase G — Recommendation Engine

## Objective

Generate actionable recommendations.

Output:

```json
{
  "stock": "ONGC",
  "action": "BUY",
  "confidence": 0.84,
  "reason": "Oil supply disruption historically benefits upstream producers."
}
```

---

## Recommendation Types

* BUY
* HOLD
* SELL
* WATCHLIST

---

# Phase H — Confidence Engine

## Objective

Estimate reliability.

---

## Inputs

* LLM Impact Analysis
* Historical Similarity
* Technical Validation
* Retrieval Quality
* News Severity

---

## Output

```json
{
  "confidence": 0.82
}
```

---

## Notification Rule

Only notify when:

```text
confidence > threshold
```

Example:

```text
0.80+
```

---

# Phase I — Notification Engine

## Objective

Push recommendations proactively.

---

## Delivery Methods

Future Options:

* In-App Notifications
* Email
* Telegram
* WhatsApp
* Mobile Push

---

## Example Notification

```text
BUY SIGNAL

Stock: ONGC

Confidence: 84%

Reason:
Geopolitical conflict is expected to increase oil prices.
Historical analysis and technical validation support a positive outlook.
```

---

# Relationship To Existing System

The current RAG platform becomes a subsystem.

```text
Autonomous Market Intelligence Agent
 ├── Event Detection
 ├── Impact Analysis
 ├── Historical Retrieval
 ├── Technical Validation
 ├── Recommendation Engine
 └── Notification Engine

Existing Advanced RAG
 └── Evidence Retrieval Layer
```

---

# Dependencies

Must be completed first:

1. Langfuse Integration
2. RAGAS Evaluation
3. Retrieval Metrics
4. Latency Monitoring
5. Grounding Validation
6. End-to-End Testing

---

# Risks

## False Positives

News does not always create market impact.

---

## Confidence Calibration

Most difficult problem in the system.

---

## Event Generalization

Not all historical events are comparable.

---

## LLM Overconfidence

Must remain grounded in evidence.

---

# Success Criteria

The system can:

1. Detect impactful events automatically
2. Map events to sectors
3. Map sectors to stocks
4. Retrieve similar historical events
5. Validate using technical indicators
6. Generate recommendations
7. Calculate confidence scores
8. Notify only when confidence exceeds threshold

---

# Long-Term Vision

```text
Reactive AI Assistant
 ↓
Research Assistant
 ↓
Market Analyst
 ↓
Autonomous Market Intelligence Platform
```
