# 📘 Phase 1 — Advanced RAG (STEP 3.2: Hybrid Retrieval Orchestrator)

---

# 🎯 Objective

Combine:

```text
FAISS Search
+
BM25 Search
```

into a single retrieval interface.

---

# 🧠 Why This Exists

Currently you have:

### Retriever A

```text
Query
 ↓
Embedding
 ↓
FAISS
 ↓
Top K Semantic Results
```

---

### Retriever B

```text
Query
 ↓
BM25
 ↓
Top K Keyword Results
```

---

Both work independently.

Now we need:

```text
Query
 ↓
Hybrid Retriever
 ├── FAISS
 └── BM25
 ↓
Merged Results
```

---

# 🧩 STEP 3.2.1 — Create Hybrid Retriever Module

---

Create:

```text
rag/
 └── hybrid_retriever.py
```

---

Responsibility:

ONLY:

```text
coordinate retrieval
```

---

Must NOT:

* rerank
* call LLM
* format citations

---

# 🧩 STEP 3.2.2 — Constructor Design

---

HybridRetriever should receive:

```text
FAISSStore
BM25Retriever
EmbeddingModel
```

through dependency injection.

---

Do NOT instantiate them internally.

---

Reason:

```text
DIP
```

---

# 🧩 STEP 3.2.3 — Define Search Contract

---

Think about:

```python
search(
    query: str,
    top_k: int
)
```

---

Input:

```text
query
top_k
```

---

Output:

A unified retrieval result collection.

---

Do not return:

```text
context string
```

yet.

---

Return:

retrieval objects.

---

# 🧩 STEP 3.2.4 — Retrieval Flow

---

Flow:

```text
Query
 ↓
Embed Query
 ↓
FAISS Search
 ↓

Query
 ↓
BM25 Search
 ↓

Merge
```

---

Keep both retrievals independent.

---

# 🧩 STEP 3.2.5 — Merge Strategy

---

For MVP:

```text
FAISS Top 10
+
BM25 Top 10
```

---

Combine.

---

Remove duplicates.

---

No weighting.

No scoring normalization.

No ranking logic.

---

Simple union.

---

# 🧩 STEP 3.2.6 — Deduplication Strategy

---

Question:

What uniquely identifies a result?

Think about:

```text
chunk_id
```

---

Use chunk_id.

---

Rule:

```text
same chunk_id
=
same chunk
```

---

Keep only one copy.

---

# 🧩 STEP 3.2.7 — Preserve Metadata

---

Every result must continue carrying:

```text
chunk_id
source_id
symbol
timestamp
text
```

---

Future systems depend on this.

---

Specifically:

* reranker
* citations
* refusal logic

---

# 🧠 SOLID Review

---

## SRP

HybridRetriever:

ONLY orchestration.

---

## DIP

Depends on:

```text
FAISS abstraction
BM25 abstraction
```

---

Not implementations.

---

## OCP

Future:

```text
FAISS
BM25
ElasticSearch
OpenSearch
```

can be added.

---

# 🚀 Deliverable

Design:

```text
HybridRetriever
```

with:

* constructor
* search()

Only skeleton first.

---

No merge implementation yet.

---

# ⛔ Do NOT Build Yet

---

Do NOT:

* rerank
* cite
* prompt engineer
* score normalize

---

# 🎯 Success Criteria

You can explain:

1. What HybridRetriever owns
2. What BM25 owns
3. What FAISS owns

without overlap.

---

# 🔜 Next Step

After review:

```text
Phase 1
 ↓
Step 3.3
 ↓
Merge Logic Implementation
```

Then later:

```text
Step 4
 ↓
Reranking
```

---

# 🧠 Mentor Note

This is your first true orchestration layer inside RAG.

Keep it thin.

The thinner it is,
the easier future upgrades become.
