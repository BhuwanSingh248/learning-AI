# 🚀 MVP 1: AI Stock Recommendation Agent - Technical Task Log

This document consolidates the end-to-end development of the AI Stock Agent MVP. It tracks the objectives, technical achievements, and implementation flows for every phase of the project.

---

## 🏗️ Phase 1 — Infrastructure & Requirements
**Objective:** Establish a rock-solid development environment with all required external services (Database, LLM) and package management.
**Achievement:** Successfully initialized a `uv` project with a working PostgreSQL connection and a local `Ollama` instance running the `Mistral` 7B model.

### 🛠️ Technical Flow:
1. **Environment Management:** Used `uv` for fast, reproducible dependency management.
2. **Dependency Stack:** Installed `openbb`, `pandas`, `sqlalchemy`, `asyncpg`, `fastapi`, `uvicorn`, and `pydantic`.
3. **Local Services:**
   - **PostgreSQL:** Created `stock_agent` database for future metadata and RAG storage.
   - **Ollama/Mistral:** Verified local LLM inference for disconnected reasoning.

---

## 🏗️ Phase 2 — Boilerplate & Clean Architecture
**Objective:** Design a scalable, modular folder structure that enforces Separation of Concerns (SoC).
**Achievement:** Created the `src/` hierarchy and established centralized configuration/logging modules.

### 🛠️ Technical Flow:
1. **Directory Structure:** Created `config`, `data`, `processing`, `analysis`, `llm`, `agent`, and `api` modules.
2. **Centralized Config:** Implemented `src/config/settings.py` using `pydantic-settings`.
3. **Database Bridge:** Built `src/config/database.py` with SQLAlchemy `async_engine`.
4. **Standardized Logging:** Established `src/config/logger.py` for unified debugging.

---

## 🧱 Phase 3 — Data Layer & Signal Engineering
**Objective:** Build a decoupled data fetching system and transform raw data into quantitative signals.
**Achievement:** Implemented a SOLID-compliant Data Layer and a deterministic feature engineering engine.

### 🛠️ Technical Flow:
1. **Interfaces (DIP):** Defined `IDataProvider` abstract base class.
2. **OpenBB Integration:** Implemented `OpenBBProvider` to fetch OHLCV, News, and Corporate Actions.
3. **Data Service:** Created `DataService` as the unified entry point for all raw data requests.
4. **Standardization:** Developed `DataValidator` to handle nulls, normalize timestamps, and de-duplicate news.
5. **Market Analysis:** Created modular analyzers:
   - **PriceAnalyzer:** Computes MA trends, Momentum (5-day return), and Volatility (StdDev).
   - **NewsAnalyzer:** Derives sentiment (-1.0 to 1.0) using keyword-matching logic.
   - **EventAnalyzer:** Scores corporate events (Dividends, Splits, Earnings).

---

## 🧠 Phase 4 — LLM Reasoning Integration
**Objective:** Bridge quantitative math and qualitative reasoning using the local Mistral LLM.
**Achievement:** Developed a structured prompting system and a reasoning engine that interprets signals into human-readable advice.

### 🛠️ Technical Flow:
1. **LLM Client:** Built `LLMClient` to handle HTTP communication with local Ollama (`localhost:11434`).
2. **Prompt Engineering:** Created `PromptBuilder` to transform `CombinedMarketSignal` objects into structured financial prompts.
3. **Reasoning Engine:** Developed `ReasoningEngine` to:
   - Transmit structured prompts to Mistral.
   - Parse raw LLM text using Regex to extract `Decision` and `Reason` fields.
   - Apply "Neutral" fallbacks if LLM output is malformed or times out.

---

## 🤖 Phase 5 — Agent Orchestration
**Objective:** Create a high-level brain to coordinate the entire pipeline for multiple ticker symbols.
**Achievement:** Successfully implemented `StockAgent`, enabling multi-stock analysis and dynamic ranking.

### 🛠️ Technical Flow:
1. **Pipeline Orchestration:** `StockAgent` loops through symbols, sequentially calling: `DataService` → `DataValidator` → `MarketAnalyzer` → `ReasoningEngine`.
2. **Ranking Logic:** Weighted scoring formula: `(Momentum * 0.4) + (Sentiment * 0.4) + (EventScore * 0.2)`.
3. **Fault Tolerance:** Per-symbol `try/except` blocks to ensure a single failure doesn't crash the entire batch.

---

## 🌐 Phase 6 — API Layer & Documentation
**Objective:** Expose the AI Agent's intelligence via a production-ready REST API.
**Achievement:** Built a FastAPI service with strict schema validation and full end-to-end integration.

### 🛠️ Technical Flow:
1. **Schemas (Contracts):** Defined `SuggestRequest` and `SuggestResponse` using Pydantic.
2. **REST Routes:** Created the `/suggest` POST endpoint to trigger the Orchestration Agent.
3. **Lifespan Management:** Refactored `main.py` to use `fastapi.lifespan`, verifying DB connection before requests are served.
4. **E2E Validation:** Verified full flow from HTTP Request → OpenBB Fetch → LLM Decision → HTTP Response.

---

## 🧠 Phase 7 — RAG Integration (Semantic Enrichment)

**Objective:** Enhance the LLM's reasoning by providing it with relevant, retrieved financial news context.
**Achievement:** Successfully implemented a full RAG pipeline using FAISS and sentence-transformers, integrated into the reasoning engine.

### 🛠️ Technical Flow:
1. **Embedding Layer:** Built `src/rag/embedder.py` using `all-MiniLM-L6-v2` (384-dim vectors).
2. **Vector Storage:** Implemented `src/rag/faiss_store.py` with a FAISS FlatL2 index and PostgreSQL metadata bridge (`rag_news_metadata`).
3. **Retrieval Pipeline:** Developed `src/rag/retriever.py` orchestrating query embedding, similarity search, and metadata reconstruction.
4. **Prompt Enrichment:** Updated `src/llm/prompt_builder.py` to inject retrieved context into LLM prompts with strict reasoning guardrails.
5. **Agent Integration:** Upgraded `StockAgent` to perform async context retrieval before LLM inference.

---

### 📋 Step 7.1 — System Design & Placement ✅

**Objective:** Define where RAG fits in the system, what it does, and what it does NOT do.

**RAG Role:**
- ✅ Stores news embeddings
- ✅ Retrieves relevant news context
- ✅ Provides context to LLM
- ❌ Does NOT fetch data, clean data, score data, or replace the analysis layer

**Integration Point:**
```
Data → Processing → Analysis
             ↓
          RAG Layer
             ↓
      Reasoning (LLM)
             ↓
           Output
```

**Retrieval Strategy (MVP):** Similarity search, Top-K = 5

**Completion Checklist:**
- [x] RAG role understood
- [x] Integration point defined
- [x] Data flow clear
- [x] Boundaries established

---

### 📋 Step 7.2 — Embedding Layer ✅

**Objective:** Build a clean Embedding Layer that converts news text → 384-dim vectors.

**Model:** `all-MiniLM-L6-v2` — fast, lightweight, good semantic understanding.

**Input:** Raw text (news title + summary combined).
**Output:** `[0.12, -0.98, 0.45, ..., 0.33]` — 384 float values matching FAISS dimension.

**Key Rules:**
- This module is the ONLY place embeddings are created.
- Same model used for indexing AND querying (otherwise retrieval breaks).
- Supports single text and batch text embedding.

**Completion Checklist:**
- [x] Embedding module created
- [x] Model loads correctly
- [x] Text → vector works
- [x] Output dimension = 384
- [x] Consistent results

---

### 📋 Step 7.3 — FAISS Index (Vector Storage & Search) ✅

**Objective:** Build a FAISS-based vector index for storing embeddings and performing similarity search.

**Index Type:** FlatL2 (simple, accurate, no tuning required for MVP).
**Dimension:** 384 (matching embedding model output).

**Metadata Mapping (PostgreSQL):**
- Stores: `id`, `symbol`, `news_text`, `timestamp`
- FAISS stores only vectors; Postgres stores the actual data.

**Data Flow:**
```
Text → Embedding
 ↓
FAISS Index
 ↓
Top-K IDs
 ↓
PostgreSQL → Metadata
```

**Key Features:** Index saved to disk and loaded on startup to avoid rebuilding.

**Completion Checklist:**
- [x] FAISS module created
- [x] Index initialized
- [x] Vectors added
- [x] Search working
- [x] Metadata mapping working
- [x] Index saved/loaded

---

### 📋 Step 7.4 — Retrieval Pipeline ✅

**Objective:** Build an end-to-end pipeline: query → embed → FAISS search → Postgres fetch → LLM-ready context.

**Input:** `symbol` + optional `query` string.
**Output:** Structured `RetrievalResult` with formatted text block.

**Flow:**
```
Query
 ↓
Embedding (Step 7.2)
 ↓
FAISS Search (Step 7.3)
 ↓
Top-K IDs → PostgreSQL fetch
 ↓
Relevant News
 ↓
Formatted Context Block
```

**Context Limits:** Top-K = 5, max 1000 chars per item to prevent LLM overload.
**Fallback:** Returns `"No significant recent news found."` when index is empty.

**Completion Checklist:**
- [x] Retrieval module created
- [x] Query → embedding works
- [x] FAISS search integrated
- [x] Metadata fetched
- [x] Context formatted
- [x] Fallback working

---

### 📋 Step 7.5 — LLM + RAG Integration ✅

**Objective:** Upgrade the reasoning layer to use both signals AND retrieved news context.

**Before:** `Signals → LLM → Decision`
**After:** `Signals + Retrieved News → LLM → Smarter Decision`

**Design Rules:**
- Signals = primary (structured truth)
- Context = supporting evidence only
- LLM must NOT hallucinate or override signal logic

**Updated Prompt Structure:**
1. Role instruction (financial analyst persona)
2. Quantitative signals (trend, momentum, sentiment, event score)
3. Retrieved news context (NEW)
4. Strict output format: `Decision:` + `Reason:`

**Edge Cases Handled:**
- No context available → fall back to signals only
- Conflicting signals vs news → mention uncertainty in reasoning

**Completion Checklist:**
- [x] Reasoning module updated
- [x] Context passed correctly
- [x] Prompt includes context
- [x] Output improved
- [x] Edge cases handled

---

### 📋 Step 7.6 — Backend API Plan for UI Integration ✅

**Objective:** Expose Phase 7 internals through stable API contracts for UI consumption.

**Endpoints:**
- `POST /suggest` — Extended with optional `signal_breakdown`, `rag`, and `prediction` fields.
- `GET /health` — Real subsystem readiness checks (not hardcoded).
- `GET /debug/symbol/{symbol}` — Single symbol QA endpoint.

**Key Fixes Implemented:**
- `/health` now performs real runtime probes (DB, FAISS, Ollama).
- `rag.fallback_used` correctly reflects whether context items were retrieved.
- `rag.context_items` now populated from retriever pipeline.
- `prediction.expected_direction` supports `bullish | bearish | neutral`.
- `RagDebugInfo.context_items` uses `Field(default_factory=list)`.

**Schemas Added:** `SignalBreakdown`, `RagContextItem`, `RagDebugInfo`, `PredictionMeta`, `HealthCheckItem`, `HealthResponse`.

**Acceptance Criteria:**
- [x] `/suggest` returns optional enriched fields for UI
- [x] `/health` reports real subsystem readiness
- [x] `rag.context_items` and `fallback_used` are accurate
- [x] `prediction.expected_direction` supports neutral
- [x] Old clients still work without contract break

---

## 🌐 Phase 8 — Indian Market News Integration

### 📋 Step 8.1 — Backend News Pipeline for Indian Stocks 🔧

**Objective:** Unlock robust RAG functionality for Indian Stock Market (NSE/BSE) by integrating specialized news APIs.

**Current Limitations:**
- OpenBB (Yahoo Finance) yields extremely sparse or no news for `.NS` and `.BO` tickers.
- RAG fallback logic triggers constantly on Indian stocks, relying entirely on technical signals.

**Architecture Changes:**

| Provider | Role |
|---|---|
| `OpenBBProvider` | Prices & Corporate Actions always; US stock news |
| `MarketauxProvider` | Primary news for Indian stocks (100 free req/day) |
| `GNewsProvider` | Fallback news for Indian stocks (100 free req/day) |

**Routing Logic in `CompositeDataProvider`:**
- Prices & Corporate Actions → `OpenBBProvider`
- News for US stocks → `OpenBBProvider`
- News for Indian stocks → `MarketauxProvider` → fallback to `GNewsProvider`

**Implementation Checklist:**
- [ ] Add `MARKETAUX_API_KEY` and `GNEWS_API_KEY` to `settings.py` and `.env`
- [ ] Create `src/data/providers/marketaux_provider.py`
- [ ] Create `src/data/providers/gnews_provider.py`
- [ ] Create `src/data/providers/composite_provider.py` with routing and fallback logic
- [ ] Update `routes.py` to instantiate and inject `CompositeDataProvider`
- [ ] Verify via `GET /debug/symbol/RELIANCE.NS`

**Acceptance Criteria:**
- [ ] Marketaux and GNews configurable via environment variables
- [ ] Indian stock requests successfully retrieve news context
- [ ] API returns `rag.fallback_used: false` for Indian stocks
- [ ] System gracefully falls back to GNews if Marketaux fails

---

## 🚀 MVP 1 Completion & E2E Validation

**Achievement:** Verified the entire system end-to-end, confirming that technical signals and semantic news context are correctly utilized by the LLM to generate ranked stock recommendations.

### 🧪 Final E2E Status:
- ✅ Data Providers (OpenBB) functional
- ✅ Signal Engineering (Technical/Sentiment/Events) calculated correctly
- ✅ RAG Pipeline (Embedding/FAISS/Postgres) operational
- ✅ LLM Reasoning (Ollama/Mistral) producing structured advice
- ✅ API Gateway (FastAPI) serving async recommendations
- 🔧 Phase 8.1 — Indian market news pipeline (in progress)
