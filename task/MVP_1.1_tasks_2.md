# 📘 Phase 2 — Advanced RAG (STEP 2: Chunk Embedding + Storage Upgrade)

---

# 🎯 Objective

Upgrade your pipeline to:

👉 Embed **chunks instead of full documents**
👉 Store chunk-level vectors + metadata

---

# 🧠 Why This Step Matters

Before:

* 1 news = 1 vector ❌
* coarse retrieval
* low relevance

---

After:

* 1 news = multiple chunk vectors ✅
* fine-grained retrieval
* high relevance

---

# 🧩 STEP 2.1 — Update Data Flow

---

## Old Flow

```text
News → Embed → FAISS
```

---

## New Flow

```text
News
 ↓
Chunker (DONE)
 ↓
Chunks
 ↓
Embedding (per chunk)
 ↓
FAISS
 ↓
PostgreSQL (metadata)
```

---

---

# 🧩 STEP 2.2 — Update Embedding Module

---

## Current behavior:

* accepts full text
* returns single vector

---

## New behavior:

👉 Accept chunk.text
👉 Return vector per chunk

---

## Important:

* DO NOT change embedding model
* DO NOT change dimension

---

---

# 🧩 STEP 2.3 — Update Storage Logic

---

## FAISS should store:

```text
vector → index_id
```

---

## PostgreSQL should store:

```text
index_id → {
  chunk_id,
  source_id,
  symbol,
  text,
  timestamp
}
```

---

👉 This mapping is critical for:

* retrieval
* citation

---

---

# 🧩 STEP 2.4 — Indexing Strategy

---

For each news item:

1. Generate chunks
2. Loop over chunks:

   * embed chunk.text
   * add to FAISS
   * store metadata

---

---

# 🧩 STEP 2.5 — Update FAISS Add Method

---

## Old:

```text
add(vector)
```

---

## New:

```text
add(vector, index_id)
```

---

👉 index_id must map to DB row

---

---

# 🧩 STEP 2.6 — Ensure Consistency

---

⚠️ MUST MATCH:

* embedding model (same everywhere)
* vector dimension
* index ordering

---

---

# 🧩 STEP 2.7 — Backfill Existing Data

---

If you already stored news:

👉 Reprocess:

* delete old vectors
* re-chunk
* re-embed
* re-store

---

---

# 🧠 SOLID Principles Applied

---

## SRP

* Chunker → splitting
* Embedding → vectorizing
* Storage → persistence

---

## DIP

Retriever depends on:
👉 abstraction, not FAISS directly

---

---

# 🧠 System Now Looks Like

---

```text
News
 ↓
Chunker
 ↓
Chunk Embeddings
 ↓
FAISS Index
 ↓
PostgreSQL Metadata
```

---

# 🚀 Completion Checklist

* [ ] Chunk embedding working
* [ ] FAISS updated
* [ ] Metadata stored per chunk
* [ ] Mapping correct
* [ ] No dimension mismatch

---

# ⛔ Do NOT Proceed Yet

Do NOT:

* implement hybrid retrieval
* add reranker
* modify prompt

---