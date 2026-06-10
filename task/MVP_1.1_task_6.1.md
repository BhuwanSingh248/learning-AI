# 📘 Phase 1 — Advanced RAG (STEP 6.1: Grounding & Refusal Design)

---

# 🎯 Objective

Prevent hallucinations by ensuring the system only answers when sufficient evidence exists.

Current:

```text
Query
 ↓
Retrieval
 ↓
LLM
 ↓
Answer
```

---

Problem:

The LLM can still answer even when retrieval quality is poor.

---

Future:

```text
Query
 ↓
Retrieval
 ↓
Reranker
 ↓
Grounding Check
 ↓

Enough Evidence?
 ├── YES → LLM
 └── NO  → Refuse
```

---

# 🧠 Why This Matters

Without grounding:

```text
User Question
 ↓
Weak Context
 ↓
Confident Wrong Answer
```

---

With grounding:

```text
User Question
 ↓
Weak Context
 ↓
Refusal
```

---

Refusal is often better than hallucination.

---

# 🧩 STEP 6.1.1 — Create Grounding Module

---

Create:

```text
rag/
 └── grounding.py
```

---

Responsibility:

```text
retrieved evidence
 ↓
confidence evaluation
 ↓
allow / refuse
```

---

Must NOT:

* call FAISS
* call BM25
* call LLM
* build prompts

---

# 🧩 STEP 6.1.2 — Define Grounding Input

---

Input should contain:

```text
query
reranked_chunks
```

---

Do not pass:

```text
raw vector scores
```

directly yet.

---

Use the final reranked candidates.

---

# 🧩 STEP 6.1.3 — Define Grounding Output

---

Think about:

```text
GroundingDecision
```

---

Possible fields:

```text
is_grounded
reason
confidence_score
```

---

Keep it simple.

---

# 🧩 STEP 6.1.4 — Initial Grounding Rules

---

Version 1 should use deterministic rules.

Examples:

### Rule 1

Minimum retrieved chunks:

```text
>= N chunks
```

---

### Rule 2

Minimum reranker score:

```text
best_score >= threshold
```

---

### Rule 3

Average score threshold:

```text
top_k_average >= threshold
```

---

No AI judging yet.

---

Deterministic only.

---

# 🧩 STEP 6.1.5 — Refusal Strategy

---

When grounding fails:

Return:

```text
Insufficient evidence available to answer this question reliably.
```

---

Do NOT send weak context to LLM.

---

Important:

Refusal occurs BEFORE reasoning.

---

# 🧩 STEP 6.1.6 — Future Evolution

---

Today:

```text
Rule-based grounding
```

---

Later:

```text
LLM-as-Judge
```

or

```text
Faithfulness Evaluation
```

---

Not now.

---

# 🧩 STEP 6.1.7 — Integration Point

---

Future flow:

```text
Hybrid Retrieval
 ↓
Reranker
 ↓
Grounding Check
 ↓
LLM
```

---

Grounding sits between:

```text
Reranker
```

and

```text
Prompt Builder
```

---

# 🧠 SOLID Review

---

## SRP

Grounding:

```text
Can we trust the evidence?
```

---

LLM:

```text
Explain the evidence.
```

---

Separate concerns.

---

# 🚀 Deliverable

Design:

```text
GroundingDecision
GroundingService
```

---

Show:

* class skeleton
* fields
* public methods

---

No implementation yet.

---

# ⛔ Do NOT Build Yet

---

Do NOT:

* call LLM for validation
* use RAGAS
* use Langfuse
* implement faithfulness metrics

---

Those come later.

---

# 🎯 Success Criteria

You can explain:

1. What grounding does
2. When refusal happens
3. Why refusal happens before LLM

---

# 🔜 Next Step

After approval:

```text
Phase 1
 ↓
Step 6.2
 ↓
Grounding Implementation
```

---

# 🧠 Mentor Note

A trustworthy AI system is not the one that always answers.

A trustworthy AI system is the one that knows when it should not answer.
