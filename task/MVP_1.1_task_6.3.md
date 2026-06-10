# 📘 Phase 1 — Advanced RAG (STEP 6.3: Grounding Integration)

---

# 🎯 Objective

Integrate GroundingService into the application flow so that unsafe or weakly-supported queries are blocked before reaching the LLM.

Current:

```text
Query
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
Citation Context Builder
 ↓
Prompt Builder
 ↓
LLM
```

---

Future:

```text
Query
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
GroundingService
 ↓

Grounded?
 ├── YES
 │    ↓
 │ Citation Context Builder
 │    ↓
 │ Prompt Builder
 │    ↓
 │ LLM
 │
 └── NO
      ↓
      Refusal Response
```

---

# 🧠 Why This Step Matters

Today:

```text
Weak Context
 ↓
LLM
 ↓
Answer Anyway
```

---

After integration:

```text
Weak Context
 ↓
Grounding
 ↓
Refusal
```

---

This dramatically reduces hallucinations.

---

# 🧩 STEP 6.3.1 — Determine Ownership

---

GroundingService owns:

```text
Decision
```

---

StockAgent owns:

```text
Control Flow
```

---

PromptBuilder owns:

```text
Prompt Construction
```

---

Keep responsibilities separate.

---

# 🧩 STEP 6.3.2 — Integration Point

---

Insert grounding immediately after reranking.

---

Flow:

```text
HybridRetriever
 ↓
Reranker
 ↓
GroundingService
```

---

Input:

```text
ranked_chunks_with_scores
```

---

Output:

```text
GroundingDecision
```

---

# 🧩 STEP 6.3.3 — Handle Grounded Path

---

If:

```text
decision.is_grounded == True
```

---

Continue:

```text
CitationContextBuilder
 ↓
PromptBuilder
 ↓
LLM
```

---

No changes required to downstream components.

---

# 🧩 STEP 6.3.4 — Handle Refusal Path

---

If:

```text
decision.is_grounded == False
```

---

Do NOT:

```text
call LLM
```

---

Return immediately.

---

Example response:

```text
Insufficient evidence available to answer this question reliably.
```

---

Include:

```text
decision.reason
```

for diagnostics.

---

# 🧩 STEP 6.3.5 — Define Refusal Response Model

---

Avoid:

```text
plain string
```

---

Use a structured response.

---

Think about:

```text
RecommendationResponse
```

containing:

```text
success
reason
confidence_score
citations
```

---

Future API consumers will thank you.

---

# 🧩 STEP 6.3.6 — Logging

---

Log:

```text
query
grounded
confidence_score
reason
```

---

Examples:

```text
ALLOW
```

or

```text
REFUSE
```

---

These logs will later feed:

* Langfuse
* Monitoring
* Evaluation

---

# 🧩 STEP 6.3.7 — Preserve Existing Flow

---

Do NOT modify:

* FAISS
* BM25
* Hybrid Retrieval
* Reranker
* Citation Builder

---

Only insert GroundingService into orchestration.

---

# 🧠 SOLID Review

---

GroundingService:

```text
Can we trust the evidence?
```

---

StockAgent:

```text
What happens next?
```

---

PromptBuilder:

```text
How do we ask the model?
```

---

No overlap.

---

# 🚀 Deliverable

Update:

```text
StockAgent
```

to support:

```text
ALLOW
```

and

```text
REFUSE
```

paths.

---

No Langfuse.
No RAGAS.
No evaluation metrics.

---

# 🎯 Success Criteria

You can demonstrate:

### Query A

```text
Strong evidence
```

Result:

```text
LLM response generated
```

---

### Query B

```text
Weak evidence
```

Result:

```text
Refusal response returned
```

---

# 🔜 Next Step

After implementation:

```text
END-TO-END INTEGRATION TEST
```

---

# 🧠 Mentor Note

At this point your system gains a capability most hobby RAG projects never implement:

```text
Knowing when NOT to answer.
```

That is often more valuable than generating an answer.
