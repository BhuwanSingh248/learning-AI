# 🧱 PHASE 5 — PROCESSING & FEATURE ENGINEERING

---

## 🎯 Objective

Convert raw data into signals.

---

## Price Features

* [ ] Moving averages
* [ ] RSI
* [ ] Momentum

---

## News Features

* [ ] Sentiment (basic → FinBERT later)

---

## Corporate Actions

* [ ] Event scoring rules

---

## Scoring Formula (MVP)

```text
score =
  0.4 * trend +
  0.4 * sentiment +
  0.2 * corporate_action
```

---

## Output

* Feature-rich dataset
