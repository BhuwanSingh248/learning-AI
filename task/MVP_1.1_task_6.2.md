# 📘 Phase 1 — Advanced RAG (STEP 6.2: Grounding Implementation)

---

# 🎯 Objective

Implement deterministic grounding rules that decide whether retrieved evidence is sufficient to proceed to LLM reasoning.

Current:

```text
Reranker
 ↓
Top Chunks
```

---

Future:

```text
Reranker
 ↓
Grounding Check
 ↓

Grounded?
 ├── YES → Prompt Builder
 └── NO  → Refusal
```

---

# 🧠 Why This Matters

A retrieval system will occasionally produce:

```text
Weak evidence
```

or

```text
No evidence
```

---

Without grounding:

```text
Weak Evidence
 ↓
LLM
 ↓
Hallucination
```

---

With grounding:

```text
Weak Evidence
 ↓
Grounding
 ↓
Refusal
```

---

# 🧩 STEP 6.2.1 — Implement Rule #1

---

Rule:

```text
candidate_count >= min_chunks
```

---

Purpose:

Ensure enough supporting evidence exists.

---

Example:

```text
0 chunks
```

Result:

```text
NOT GROUNDED
```

---

# 🧩 STEP 6.2.2 — Implement Rule #2

---

Rule:

```text
best_rerank_score >= threshold
```

---

Purpose:

Ensure at least one chunk strongly matches the query.

---

Example:

```text
Best Score = 0.03
Threshold = 0.30
```

Result:

```text
NOT GROUNDED
```

---

# 🧩 STEP 6.2.3 — Implement Rule #3

---

Rule:

```text
average_top_k_score >= threshold
```

---

Purpose:

Avoid situations where:

```text
1 strong chunk
+
many weak chunks
```

create misleading confidence.

---

Example:

```text
Top Scores:
0.85
0.82
0.12
0.08
0.04
```

Average:

```text
0.38
```

---

Use a configurable threshold.

---

# 🧩 STEP 6.2.4 — Confidence Score

---

Compute:

```text
confidence_score
```

---

For V1:

Use:

```text
average_top_k_score
```

---

Keep it simple.

---

# 🧩 STEP 6.2.5 — Decision Reasons

---

Return clear reasons.

Examples:

```text
Insufficient retrieved evidence.
```

---

```text
Top reranker score below threshold.
```

---

```text
Average evidence score below threshold.
```

---

These logs become extremely useful later.

---

# 🧩 STEP 6.2.6 — Success Decision

---

If all rules pass:

Return:

```text
is_grounded = True
```

---

Reason:

```text
Evidence passed all grounding checks.
```

---

# 🧩 STEP 6.2.7 — Logging

---

Log:

```text
query
candidate_count
best_score
average_score
decision
```

---

Future monitoring depends on this.

---

# 🧠 SOLID Review

---

GroundingService:

ONLY:

```text
evaluate evidence
```

---

Must NOT:

* call LLM
* build prompts
* retrieve chunks

---

# 🚀 Deliverable

Implement:

```python
GroundingService.evaluate()
```

---

Return:

```python
GroundingDecision
```

---

No integration yet.

No refusal messages yet.

No API changes yet.

---

# ⛔ Do NOT Build Yet

---

Do NOT:

* modify PromptBuilder
* modify StockAgent
* modify API response

---

Those belong to Step 6.3.

---

# 🎯 Success Criteria

You can answer:

1. Why grounding failed
2. Which rule failed
3. What confidence score was produced

---

# 🔜 Next Step

After implementation review:

```text
Phase 1
 ↓
Step 6.3
 ↓
Grounding Integration
```

---

# 🧠 Mentor Note

This is the first component in your system whose job is not to answer.

Its job is to decide whether answering is safe.
