# 📘 Phase 1 — Advanced RAG (STEP 5.2: Citation Context Builder Integration)

---

# 🎯 Objective

Integrate citation-aware context into the retrieval pipeline.

Current:

```text id="v8qu7y"
Hybrid Retrieval
 ↓
Reranker
 ↓
Chunks
```

---

Future:

```text id="1tahpl"
Hybrid Retrieval
 ↓
Reranker
 ↓
Citation Context Builder
 ↓
CitationContext
```

---

# 🧠 Why This Step Exists

The builder now creates:

```text id="jw2xuz"
formatted_text
citations
```

---

This allows:

* explainability
* source tracing
* future grounding checks

---

# 🧩 STEP 5.2.1 — Rename Builder

---

Current:

```text id="mkn04l"
ContextBuilder
```

---

Recommended:

```text id="r1vvxp"
CitationContextBuilder
```

---

Reason:

Future system may contain:

* PromptBuilder
* ContextBuilder
* CitationContextBuilder

---

Avoid ambiguity.

---

# 🧩 STEP 5.2.2 — Integrate After Reranker

---

Current:

```text id="p4x0yd"
HybridRetriever
 ↓
Reranker
 ↓
Return Chunks
```

---

New:

```text id="8kcf6s"
HybridRetriever
 ↓
Reranker
 ↓
CitationContextBuilder
 ↓
CitationContext
```

---

Builder should receive:

```text id="j9mvjl"
top ranked chunks
```

only.

---

# 🧩 STEP 5.2.3 — Preserve Metadata

---

Verify:

```text id="v2cgkg"
chunk_id
source_id
timestamp
symbol
```

remain available after:

```text id="3zgrxv"
retrieval
 ↓
reranking
 ↓
citation building
```

---

No information loss.

---

# 🧩 STEP 5.2.4 — Define Output Contract

---

Builder returns:

```text id="w7o9x4"
CitationContext
```

---

Containing:

```text id="vzzm91"
formatted_text
citations
```

---

No raw strings.

No dictionaries.

Strong typing only.

---

# 🧩 STEP 5.2.5 — Update Agent Flow

---

Future flow:

```text id="k0x16x"
Query
 ↓
Hybrid Retrieval
 ↓
Reranker
 ↓
CitationContextBuilder
 ↓
Prompt Builder
 ↓
LLM
```

---

PromptBuilder should consume:

```text id="9f5cds"
CitationContext
```

not raw chunk list.

---

# 🧩 STEP 5.2.6 — Prepare API Layer

---

Do NOT implement yet.

Just verify:

Future response can expose:

```json id="r7azhi"
{
  "decision": "...",
  "reason": "...",
  "citations": [...]
}
```

---

because CitationContext already exists.

---

# 🧠 SOLID Review

---

## SRP

CitationContextBuilder:

```text id="o1bhkk"
chunks
 ↓
evidence package
```

---

PromptBuilder:

```text id="p03b8t"
evidence package
 ↓
prompt
```

---

LLM:

```text id="4m4v5k"
prompt
 ↓
reasoning
```

---

Perfect separation.

---

# 🚀 Deliverable

Verify:

* Builder renamed
* Integration point decided
* CitationContext used everywhere

---

No prompt modifications yet.

No refusal logic yet.

---

# 🎯 Success Criteria

You can answer:

1. Who creates citations?
2. Who formats evidence?
3. Who consumes evidence?
4. Who exposes citations to API?

without overlap.

---

# 🔜 Next Step

After this:

```text id="7c9y4h"
Phase 1
 ↓
Step 6.1
 ↓
Grounding & Refusal Design
```

---

# 🧠 Mentor Note

At this point:

Your system can now explain:

```text id="4a5rtu"
why
```

it answered.

Next step teaches it:

```text id="wq9t3i"
when not to answer
```

which is arguably more important.
