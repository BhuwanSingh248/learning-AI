# 🧱 PHASE 4 — RAG + VECTOR PIPELINE (FAISS)

---

## 🎯 Objective

Enable semantic retrieval over news data.

---

## Architecture

```text
News → Clean → Embed → FAISS → Retrieve → PostgreSQL → Context
```

---

## Tasks

### Embeddings

* [ ] Load sentence-transformer model
* [ ] Create embedding function

---

### FAISS

* [ ] Initialize index (dim=384)
* [ ] Add vectors
* [ ] Save/load index

---

### PostgreSQL Table

```sql
news_embeddings (
  id SERIAL PRIMARY KEY,
  symbol TEXT,
  news TEXT,
  timestamp TIMESTAMP
)
```

---

### Pipeline

* [ ] Clean news text
* [ ] Generate embeddings
* [ ] Store:

  * FAISS → vectors
  * PostgreSQL → metadata

---

### Retrieval

* [ ] Query → embedding
* [ ] FAISS search (TOP_K = 5)
* [ ] Fetch metadata

---

## Output

* Working RAG system
