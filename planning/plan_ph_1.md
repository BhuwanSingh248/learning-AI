# 🧱 PHASE 1 — REQUIREMENTS & INFRASTRUCTURE

---

## 🎯 Objective

Set up environment and finalize architecture decisions.

---

## ✅ Tech Stack (Locked)

* Data Source → OpenBB
* Vector Search → FAISS
* Metadata DB → PostgreSQL
* Embeddings → sentence-transformers
* LLM → Mistral 7B via Ollama
* Backend → FastAPI
* Env Manager → uv

---

## ⚙️ Setup Steps

### Environment

```bash
pip install uv
uv init stock-agent
cd stock-agent
```

---

### Dependencies

```bash
uv add openbb pandas numpy sqlalchemy psycopg2-binary \
faiss-cpu sentence-transformers transformers \
fastapi uvicorn python-dotenv
```

---

### PostgreSQL

```sql
CREATE DATABASE stock_agent;
```

---

### FAISS

```bash
uv add faiss-cpu
```

---

### LLM Setup

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run mistral
```

---

## 📁 Folder Structure

```text
src/
  config/
  data/
  processing/
  analysis/
  rag/
  llm/
  agent/
  api/
```

---

## ⚙️ Environment Variables

```env
DB_URL=postgresql://user:password@localhost:5432/stock_agent
VECTOR_DIM=384
TOP_K=5
```

---

## ✅ Phase 1 Checklist

* [ ] uv project runs
* [ ] OpenBB works
* [ ] PostgreSQL connects
* [ ] FAISS test works
* [ ] Embedding model works
* [ ] Ollama + Mistral running
