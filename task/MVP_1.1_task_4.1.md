# 📘 Phase 1 — Advanced RAG (STEP 4.1: Reranker Design)

---

# 🎯 Objective

Improve retrieval quality by ranking retrieved chunks according to their relevance to the user query.

Current pipeline:

```text id="hv8t7q"
Query
 ↓
FAISS Search
 +
BM25 Search
 ↓
Merged Results
```

Problem:

Merged results still contain noise.

---

# Example

Query:

```text id="1sjyq0"
Should I buy Infosys after earnings?
```

Retrieved chunks:

```text id="0pr4h4"
1. Infosys earnings beat estimates
2. Infosys dividend announcement
3. TCS dividend announcement
4. Infosys opens new office
5. Wipro market outlook
```

All are related.

Not all are equally relevant.

---

# Goal

Introduce:

```text id="vwy2j7"
Query
 +
Candidate Chunk
 ↓
Relevance Score
```

and retain only the most relevant chunks.

---

# Why Reranking Matters

Vector search retrieves:

```text id="z8iuhw"
possibly relevant chunks
```

---

Reranking identifies:

```text id="gvjzoi"
most relevant chunks
```

---

This usually produces the largest quality improvement after chunking.

---

# 🧩 STEP 4.1.1 — Create Reranker Module

---

Create:

```text id="ah6wkp"
rag/
 └── reranker.py
```

---

Responsibility:

```text id="m9g9ln"
query
+
candidate chunks
 ↓
relevance ranking
```

---

Must NOT:

* call FAISS
* call BM25
* call PostgreSQL
* call LLM

---

# 🧩 STEP 4.1.2 — Choose Reranking Model

---

Use a local Cross Encoder.

Recommended:

```text id="3bnkv4"
cross-encoder/ms-marco-MiniLM-L-6-v2
```

---

Why:

* Lightweight
* Fast
* Excellent retrieval quality
* Widely used in production RAG systems

---

# 🧩 STEP 4.1.3 — Design Public Interface

---

Before implementation, design:

```text id="evm02x"
Reranker
```

---

Think about:

### Constructor

What dependencies should be loaded?

---

### Public Method

Input:

```text id="26mk7p"
query
candidate_chunks
top_k
```

---

Output:

Should return:

```text id="pnm4z8"
ranked chunks
```

---

Question:

Will it return:

```text id="34ctpb"
chunks only
```

or

```text id="5x8u7g"
chunks + scores
```

Think ahead.

Future evaluation metrics may need scores.

---

# 🧩 STEP 4.1.4 — Define Candidate Input

---

The reranker should not care whether chunks came from:

```text id="49ocq6"
FAISS
```

or

```text id="bujlsk"
BM25
```

---

It should receive:

```text id="1i7m4f"
retrieved chunks
```

only.

---

Keep it retrieval-source agnostic.

---

# 🧩 STEP 4.1.5 — Prepare for Future Citation Support

---

Every candidate must preserve:

```text id="khmvbn"
chunk_id
source_id
symbol
timestamp
text
```

---

Future phases require this for:

* citations
* evidence tracking
* refusal logic

---

# 🧩 STEP 4.1.6 — Top-K Strategy

---

Example:

Input:

```text id="ntnmmc"
20 chunks
```

---

Output:

```text id="a78szh"
Top 5 chunks
```

---

The reranker should own:

```text id="l4adxt"
ranking
```

not retrieval.

---

# 🧠 SOLID Review

---

## SRP

Reranker:

ONLY evaluates relevance.

---

## DIP

Depends on:

```text id="g7db0r"
CrossEncoder abstraction
```

not retrieval systems.

---

## OCP

Future models:

```text id="79zm5o"
Cross Encoder
SBERT Reranker
Cohere Reranker
```

should be swappable.

---

# 🚀 Deliverable

Design:

```text id="jv7ev9"
Reranker class
```

with:

* constructor
* public method
* input types
* output types

---

Show class skeleton only.

Do NOT implement ranking logic yet.
---

Do NOT:

* integrate with HybridRetriever
* normalize scores
* add citations
* add refusal logic

---

# 🎯 Success Criteria

You can explain:

1. What retrieval owns
2. What reranker owns
3. What LLM owns

without overlap.

---

# 🔜 Next Step

After approval:

```text id="4w6e07"
Phase 1
 ↓
Step 4.2
 ↓
Reranker Implementation
```

---

# 🧠 Mentor Note

Retrieval finds candidates.

Reranking chooses winners.

LLM explains the result.

Keep those responsibilities separate.
