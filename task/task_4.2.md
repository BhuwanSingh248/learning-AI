# 📘 Phase 4 — LLM Integration (STEP 2: Prompt Design for Financial Reasoning)

---

# 🎯 Objective (This Step Only)

Design a **structured prompt system** that:

* Takes signals as input
* Guides the LLM to reason correctly
* Produces consistent, explainable output

👉 No agent yet
👉 No automation yet

---

# 🧠 Why This Step Matters

LLMs are powerful, but:

❌ Without guidance → random answers
✅ With structure → reliable reasoning

---

# 🧩 STEP 4.2.1 — Define Inputs to LLM

---

Your prompt should include:

---

## 1. Stock Symbol

Example:

* AAPL
* RELIANCE.NS

---

## 2. Signals (From Phase 3)

---

### Price Signals

* trend (bullish / bearish / neutral)
* momentum (numeric)

---

### News Sentiment

* sentiment_score

---

### Corporate Actions

* event_score

---

---

## Final Input Structure (Conceptual)

```text id="i7z7hj"
Stock: AAPL

Trend: Bullish
Momentum: 0.7
Sentiment: 0.6
Event Score: 0.5
```

---

# 🧩 STEP 4.2.2 — Define Expected Output

---

You must force LLM to return:

---

```text id="ksrjyf"
Decision: (Bullish / Bearish / Neutral)

Reason:
- Point 1
- Point 2
- Point 3
```

---

👉 This ensures consistency

---

# 🧩 STEP 4.2.3 — Add Instructions (Very Important)

---

Tell LLM:

* You are a financial analyst
* Use ONLY provided data
* Do NOT hallucinate
* Keep reasoning concise

---

---

## Example Instruction Style:

```text id="d8o8yw"
You are a financial analyst.
Based on the provided signals, determine whether the stock is bullish, bearish, or neutral.
Do not assume any external information.
```

---

# 🧩 STEP 4.2.4 — Combine Everything

---

Your prompt should include:

1. Role definition
2. Input signals
3. Output format instructions

---

👉 This is called **structured prompting**

---

# 🧩 STEP 4.2.5 — Test Prompt

---

## What to do:

* Send sample signals
* Observe response

---

## What to verify:

* Output follows format
* Reasoning is logical
* No hallucinations

---

# 🧠 Common Issues

---

## ❌ Problem: Random answers

👉 Fix:

* Make instructions stricter

---

## ❌ Problem: Wrong format

👉 Fix:

* Clearly define output structure

---

## ❌ Problem: Too verbose

👉 Fix:

* Add “be concise” instruction

---

# 🧠 SOLID Thinking Applied

---

## SRP

Prompt module:
👉 ONLY handles prompt creation

---

## OCP

You can:

* improve prompt later
* add variations

---

## DIP

LLM wrapper does NOT know:
👉 how prompts are structured

---

# 🧠 System Now Looks Like

---

```text id="5nprlh"
Signals
 ↓
Prompt Builder (YOU ARE HERE)
 ↓
LLM Wrapper
 ↓
Mistral
 ↓
Response
```

---

# 🚀 Completion Checklist

* [x] Input structure defined
* [x] Output format fixed
* [x] Instructions added
* [x] Prompt tested
* [x] Response consistent

---

# ⛔ Do NOT Proceed Yet

Do NOT:

* Build agent
* Automate flow
* Create API

---

# 🎯 What Comes Next

After this:

👉 **Phase 4.3 — Signal → LLM Integration (End-to-End Reasoning)**

---

# 🧠 Mentor Insight

This step defines:

👉 How “smart” your AI feels

Not the model,
👉 but the prompt

---
