# 🧱 PHASE 3 — DATA LAYER (OpenBB)

---

## 🎯 Objective

Fetch and standardize all required data.

---

## Data Types

### Price Data

* OHLCV
* Lookback-based

### News

* Title
* Summary
* Timestamp

### Corporate Actions

* Dividends
* Earnings
* Splits

---

## DataService Responsibilities

* Fetch data from OpenBB
* Convert to pandas
* Normalize schema
* Handle missing values

---

## Cleaning Rules

* Remove nulls
* Standardize timestamps (UTC)
* Deduplicate news
* Align time-series

---

## Output Format

### Price

```json
{
  "date": "...",
  "open": 0,
  "close": 0
}
```

---

### News

```json
{
  "title": "...",
  "summary": "...",
  "timestamp": "..."
}
```

---

## Output

* Clean structured data pipeline
