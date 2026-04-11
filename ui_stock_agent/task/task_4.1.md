# Phase 4 - API Contract Planning

---

# Objective

Define the frontend-facing API contract that the UI depends on.

---

# STEP 4.1.1 - Define analysis request

```json
{
  "symbols": ["AAPL", "MSFT", "TSLA"],
  "lookback_days": 90
}
```

---

# STEP 4.1.2 - Define analysis response

```json
{
  "suggestions": [
    {
      "symbol": "AAPL",
      "score": 0.82,
      "decision": "Bullish",
      "reason": "Strong trend and positive sentiment"
    }
  ]
}
```

---

# STEP 4.1.3 - Define recommended additional endpoints

* `GET /health`
* `GET /stocks/:symbol/details`
* `GET /stocks/:symbol/news`
* `GET /stocks/:symbol/price-history`

---

# STEP 4.1.4 - Identify current backend gaps

The current stock agent already returns:

* symbol
* score
* decision
* reason

For richer UI, later backend work should expose:

* signal breakdown
* price history
* recent news
* corporate actions

---

# Completion Checklist

* [ ] core request shape defined
* [ ] core response shape defined
* [ ] optional endpoints listed
* [ ] backend gaps identified
