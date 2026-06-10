# 📘 Phase 1 — Advanced RAG (STEP 5.1: Citation-Aware Retrieval Design)

---

# 🎯 Objective

Transform retrieved context into evidence-backed context that can be traced back to its original source.

Current:

```text id="3vnqk9"
LLM
 ↑
Context String
```

---

Future:

```text id="7zv4p6"
LLM
 ↑
[1] Chunk
[2] Chunk
[3] Chunk
```

and

```text id="8phl4d"
Response
 +
Citations
```

---

# 🧠 Why Citations Matter

Without citations:

```text id="h70jlk"
LLM says something
```

but we don't know:

* where it came from
* which chunk supported it
* whether retrieval was correct

---

With citations:

```text id="4bmjlwm"
Decision
 ↓
Evidence
 ↓
Source
```

---

This is the foundation for:

* Explainability
* Trust
* Auditing
* Evaluation

---

# 🧩 STEP 5.1.1 — Introduce Citation Concept

---

Every retrieved chunk already contains:

```text id="x5t0a1"
chunk_id
source_id
symbol
timestamp
text
```

---

These will become citation references.

---

Example:

```text id="efldlg"
[1] chunk_id = AAPL_12
[2] chunk_id = AAPL_15
[3] chunk_id = AAPL_22
```

---

# 🧩 STEP 5.1.2 — Create Citation Model

---

Create a dedicated citation model.

Do NOT use raw database entities.

---

Think about:

```text id="owsh7m"
Citation
```

---

Possible fields:

```text id="u4ngm0"
citation_id
chunk_id
source_id
timestamp
text_preview
```

---

Keep it lightweight.

---

# 🧩 STEP 5.1.3 — Design Context Builder

---

Current:

```text id="0z7ey4"
context =
"news1 ... news2 ... news3 ..."
```

---

Future:

```text id="ly9gtt"
[1] chunk text

[2] chunk text

[3] chunk text
```

---

Purpose:

Allow the LLM to reference evidence explicitly.

---

# 🧩 STEP 5.1.4 — Citation Numbering Strategy

---

Question:

Where should numbering happen?

---

Options:

### Retrieval Layer

```text id="zjlwmf"
retriever assigns ids
```

---

### Context Builder

```text id="g7vd7k"
context formatter assigns ids
```

---

Think carefully.

---

Hint:

Retrieval should remain retrieval-focused.

---

# 🧩 STEP 5.1.5 — Preserve Source Information

---

Do NOT lose:

```text id="nlv5v8"
chunk_id
source_id
timestamp
```

during:

```text id="y4rhtg"
retrieval
 ↓
reranking
 ↓
prompt building
```

---

Future phases depend on this.

---

# 🧩 STEP 5.1.6 — Prepare API Response Shape

---

Current:

```json id="l0rbrm"
{
  "decision": "...",
  "reason": "..."
}
```

---

Future:

```json id="cwz4aj"
{
  "decision": "...",
  "reason": "...",
  "citations": [...]
}
```

---

Do NOT implement yet.

Just design.

---

# 🧩 STEP 5.1.7 — Citation Ownership

---

Ask:

Who owns citations?

---

Not:

```text id="1hnw3q"
FAISS
```

---

Not:

```text id="7d1a04"
BM25
```

---

Not:

```text id="3jlwmr"
Reranker
```

---

Think about:

```text id="rj2k7p"
Context Builder
```

or

```text id="3xq3pu"
Prompt Builder
```

---

Choose carefully.

---

# 🧠 SOLID Review

---

## SRP

Retrieval:

```text id="gx2vqz"
find evidence
```

---

Citation Builder:

```text id="w3jknu"
format evidence
```

---

LLM:

```text id="dt6z9j"
reason using evidence
```

---

Keep responsibilities separate.

---

# 🚀 Deliverable

Design:

```text id="87rhts"
Citation Model
```

and

```text id="1kqj3x"
Citation-Aware Context Builder
```

---

Show only:

* class skeletons
* responsibilities
* method signatures

---

No implementation yet.

---

# ⛔ Do NOT Build Yet

---

Do NOT:

* modify prompts
* modify reasoning layer
* modify API response

---

Those come later.

---

# 🎯 Success Criteria

You can explain:

1. What retrieval returns
2. What citations represent
3. Who formats citations
4. Who consumes citations

without overlap.

---

# 🔜 Next Step

After review:

```text id="u8r7o9"
Phase 1
 ↓
Step 5.2
 ↓
Citation Context Builder Implementation
```

---

# 🧠 Mentor Note

A good RAG system retrieves information.

A great RAG system can prove where that information came from.

This step is the beginning of that proof chain.
