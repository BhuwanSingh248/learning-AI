# 📘 Phase 1 — Advanced RAG (STEP 3.1: BM25 Retriever Design)

---

# 🎯 Objective

Introduce a keyword-based retrieval layer that complements semantic vector search.

This step builds the foundation for:

```text
Hybrid Retrieval
=
BM25 + FAISS
```

---

# 🧠 Why We Need BM25

Current retrieval pipeline:

```text
Query
 ↓
Embedding
 ↓
FAISS
 ↓
Top K Chunks
```

This works well for semantic similarity.

However, it may miss:

* Exact company names
* Ticker symbols
* Dividend dates
* Earnings dates
* Corporate action terminology
* Regulatory keywords

---

# Example

Query:

```text
Infosys dividend record date
```

A keyword search may outperform semantic search for this query.

---

# Goal

Combine:

```text
Semantic Search
+
Keyword Search
```

to improve retrieval quality.

---

# 🧩 STEP 3.1.1 — Create BM25 Module

---

## Create

```text
rag/
 └── bm25_retriever.py
```

---

## Responsibility

ONLY:

```text
Chunk Text
 ↓
BM25 Index
 ↓
Search
 ↓
Ranked Chunk IDs
```

---

## Must NOT Know About

* FAISS
* Embeddings
* Reranking
* LLM
* Prompts

---

# 🧩 STEP 3.1.2 — Define Public Interface

Before implementation, design the API.

---

Think about methods such as:

```text
add_chunks(...)
search(...)
```

---

Do NOT write implementation immediately.

---

# Questions To Answer

---

## Question 1

What should be indexed?

Options:

* Full news
* Chunks

---

Think carefully.

Your current architecture already migrated to:

```text
News
 ↓
Chunks
 ↓
Embeddings
```

---

## Question 2

What should search return?

Possible outputs:

```text
chunk_id
```

or

```text
RetrievedChunk
```

---

Think about future citation requirements.

---

## Question 3

Where should the BM25 index live?

---

Options:

* Memory only
* Rebuild on startup
* Persist to disk

---

For MVP:

Keep it simple.

---

# 🧩 STEP 3.1.3 — Design Search Contract

---

Input:

```text
query
top_k
```

---

Output:

```text
ranked chunk identifiers
```

or

```text
retrieval objects
```

---

Do not over-engineer.

Keep interface minimal.

---

# 🧩 STEP 3.1.4 — Design for Future Hybrid Retrieval

---

Remember:

Next step will combine:

```text
FAISS Results
+
BM25 Results
```

---

Therefore BM25 output should be easy to merge with:

```text
FAISS Search Results
```

---

Think ahead.

Do not couple BM25 to FAISS.

---

# 🧠 SOLID Principles

---

## SRP

BM25Retriever:

ONLY keyword retrieval.

---

## OCP

Future:

* BM25
* BM25+
* Elasticsearch

Should be replaceable.

---

## DIP

Higher layers should depend on:

```text
IRetriever
```

not BM25 implementation.

---

# 🚀 Deliverable

Before implementation, design:

* class name
* public methods
* inputs
* outputs

---

Show only:

```text
Class Skeleton
```

No retrieval logic yet.

---

# ⛔ Do NOT Do Yet

---

Do NOT:

* Merge with FAISS
* Build reranker
* Add citations
* Modify prompts

---

# 🎯 Success Criteria

You can clearly answer:

1. What does BM25Retriever own?
2. What does it return?
3. How will it integrate with Hybrid Retrieval later?

---

# 🔜 Next Step

After BM25Retriever design is approved:

```text
Phase 1
 ↓
Step 3.2
 ↓
Hybrid Retrieval Orchestrator
```

---

# 🧠 Mentor Note

At this stage:

You are not building search.

You are designing a retrieval abstraction.

Good abstractions make future upgrades easy.

Poor abstractions force rewrites.

Take time here.
