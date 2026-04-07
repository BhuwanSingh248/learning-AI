# 📘 Stock Recommendation AI Agent — Complete Phase-wise Plan (FAISS + PostgreSQL)

---

# 🎯 PROJECT GOAL

Build a **fully open-source AI-powered stock recommendation system** that:

* Uses **news + corporate actions + historical price**
* Uses **RAG (FAISS-based) for contextual reasoning**
* Generates **explainable stock suggestions**
* Exposes a **backend API**

---

# ⚙️ FINALIZED ARCHITECTURE

```text
Data (OpenBB)
   ↓
Data Layer (cleaning + normalization)
   ↓
Processing Layer (features + signals)
   ↓
RAG Layer (FAISS + PostgreSQL)
   ↓
LLM (Mistral via Ollama)
   ↓
Agent (decision + explanation)
   ↓
API (FastAPI)
```

---

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

---

# 🧱 PHASE 2 — BOILERPLATE & ARCHITECTURE

---

## 🎯 Objective

Create clean modular structure (no business logic yet).

---

## Tasks

* [ ] Create folder structure
* [ ] Setup config module:

  * env loader
  * DB connection
* [ ] Create main entry (`main.py`)
* [ ] Setup logging

---

## Output

* Clean, scalable architecture ready

---

# 🧱 PHASE 3 — DATA LAYER (OpenBB)

---

## 🎯 Objective

Fetch and standardize all required data.

---

## Data Types

### Price Data

* OHLCV
* Lookback-based

### News

* Title
* Summary
* Timestamp

### Corporate Actions

* Dividends
* Earnings
* Splits

---

## DataService Responsibilities

* Fetch data from OpenBB
* Convert to pandas
* Normalize schema
* Handle missing values

---

## Cleaning Rules

* Remove nulls
* Standardize timestamps (UTC)
* Deduplicate news
* Align time-series

---

## Output Format

### Price

```json
{
  "date": "...",
  "open": 0,
  "close": 0
}
```

---

### News

```json
{
  "title": "...",
  "summary": "...",
  "timestamp": "..."
}
```

---

## Output

* Clean structured data pipeline

---

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

---

# 🧱 PHASE 5 — PROCESSING & FEATURE ENGINEERING

---

## 🎯 Objective

Convert raw data into signals.

---

## Price Features

* [ ] Moving averages
* [ ] RSI
* [ ] Momentum

---

## News Features

* [ ] Sentiment (basic → FinBERT later)

---

## Corporate Actions

* [ ] Event scoring rules

---

## Scoring Formula (MVP)

```text
score =
  0.4 * trend +
  0.4 * sentiment +
  0.2 * corporate_action
```

---

## Output

* Feature-rich dataset

---

# 🧱 PHASE 6 — LLM INTEGRATION

---

## 🎯 Objective

Enable reasoning + explanation.

---

## Tasks

* [ ] Create LLM wrapper
* [ ] Connect Ollama
* [ ] Design prompts

---

## Input to LLM

* trend signals
* sentiment score
* retrieved news

---

## Output

```json
{
  "decision": "bullish",
  "reason": "positive sentiment + strong trend"
}
```

---

# 🧱 PHASE 7 — AGENT LAYER

---

## 🎯 Objective

Orchestrate full pipeline.

---

## Tasks

* [ ] Create tools:

  * get_price_data
  * get_news_context
  * get_features
* [ ] Combine signals
* [ ] Call LLM

---

## Flow

```text
Query → Agent → Data → RAG → LLM → Output
```

---

# 🧱 PHASE 8 — API LAYER

---

## 🎯 Objective

Expose system via FastAPI.

---

## Endpoint

### POST /suggest

```json
{
  "symbols": ["AAPL"],
  "lookback_days": 90
}
```

---

## Response

```json
{
  "suggestions": [
    {
      "symbol": "AAPL",
      "score": 0.82,
      "reason": "Strong trend + positive sentiment"
    }
  ]
}
```

---

# 🧱 PHASE 9 — OPTIMIZATION

---

## Performance

* [ ] Async calls
* [ ] Batch processing
* [ ] Caching (Redis)

---

## ML Improvements

* [ ] FinBERT
* [ ] Advanced models

---

## Infra

* [ ] Docker
* [ ] Monitoring

---

# 🚀 BUILD ORDER (STRICT)

1. Data Layer
2. RAG
3. Processing
4. LLM
5. Agent
6. API

---

# 🧠 FINAL NOTES

* Do NOT overuse LLM
* Data quality > model quality
* Build incrementally
* Validate each phase before moving ahead

---

# ✅ STATUS CHECKPOINT

Before Phase 2:

* [ ] All Phase 1 checklist completed

---

👉 Next step:

**“Phase 1 completed”**

---
