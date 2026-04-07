# 🧱 PHASE 8 — API LAYER

---

## 🎯 Objective

Expose system via FastAPI.

---

## Endpoint

### POST /suggest

```json
{
  "symbols": ["AAPL"],
  "lookback_days": 90
}
```

---

## Response

```json
{
  "suggestions": [
    {
      "symbol": "AAPL",
      "score": 0.82,
      "reason": "Strong trend + positive sentiment"
    }
  ]
}
```
