# PHASE 7 - API INTEGRATION & DATA CONTRACTS

---

## Objective

Translate backend capabilities into frontend-ready request and response contracts.

---

## Minimum Required Endpoint

### POST `/suggest`

```json
{
  "symbols": ["AAPL", "MSFT"],
  "lookback_days": 90
}
```

---

## Minimum Expected Response

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

## Recommended Additional Endpoint

### GET `/health`

Use this for:

* backend availability
* database status
* LLM status
* data provider status

---

## Recommended Detail Payload Additions

For richer UI later, the backend should expose:

* momentum
* volatility
* sentiment score
* event score
* recent news items
* recent corporate actions

---

## Phase 7 Checklist

* [ ] base request payload defined
* [ ] base response model defined
* [ ] health endpoint requirement noted
* [ ] detail data gaps identified
* [ ] frontend type model list prepared
