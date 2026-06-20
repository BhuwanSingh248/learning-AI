# 📈 AI Stock Recommendation Agent (Advanced RAG Pipeline)

Welcome to the **AI Stock Recommendation Agent** repository. This project implements a production-grade investment advisory system that coordinates quantitative technical indicators, corporate action scoring, and semantic news retrieval inside a local, private Large Language Model (LLM) reasoning flow.

The core of the intelligence lies in a custom **Advanced RAG (Retrieval-Augmented Generation) Pipeline** designed to prevent LLM hallucinations by evaluating and gating retrieved news content against calibrated logit confidence thresholds.

---

## 🗺️ Master System Architecture Flow

The following flow diagram maps out the complete online and offline pipeline. Current implementations are marked in solid boxes, while future enhancements from the backlog are indicated with **dotted boxes and lines**:

```mermaid
flowchart TD
    subgraph Current["Live Pipeline (Phase 1)"]
        User["User / Client"] -->|"POST /suggest"| RouteSuggest["routes/suggest"]
        
        %% Ingestion
        RouteSuggest -->|"1. Ingest Data"| DataService["DataService"]
        DataService -->|"Fetch Prices & News"| OpenBB["OpenBBProvider"]
        DataService -->|"Fetch Indian News"| Composite["CompositeDataProvider (Marketaux/GNews)"]
        
        %% Indexing
        Composite -->|"2. Chunk & Embed"| Chunker["News Chunker (Sentence Splitter)"]
        Chunker -->|"600-token chunks"| Embedder["EmbeddingModel (all-MiniLM-L6-v2)"]
        Embedder -->|"3. Index Vectors"| FAISS["FAISS Index Store"]
        Chunker -->|"Store Metadata"| PostgreSQL["Postgres (rag_news_metadata)"]
        
        %% Retrieval
        RouteSuggest -->|"4. Retrieve Context"| RAGRetriever["RAGRetriever"]
        RAGRetriever -->|"Hybrid Query"| HybridRetriever["HybridRetriever"]
        HybridRetriever -->|"Semantic Search"| FAISS
        HybridRetriever -->|"Keyword Search"| BM25["BM25Retriever"]
        
        %% Reranking
        FAISS & BM25 -->|"Union & Deduplicate"| Merged["Merged Candidates"]
        Merged -->|"5. Score Relevance"| Reranker["Reranker (CrossEncoder)"]
        
        %% Grounding & Refusal
        Reranker -->|"Ranked Pairs"| Grounding["Grounding Gate (Threshold Checks)"]
        Grounding -->|FAIL: Score < -5.0 or Top3-Avg < -9.0| Refusal["LLM Bypassed: Structured Neutral Response"]
        Grounding -->|PASS| Citations["CitationContextBuilder (Gapless Brackets)"]
        
        %% Reasoning LLM
        Citations -->|"Context + Tech Signals"| Reasoning["ReasoningEngine"]
        Reasoning -->|"Financial Prompt"| LLM["Ollama Client (phi3:mini)"]
        LLM -->|"Parse Recommendation"| Output["Ranked Suggestions / Response"]
    end

    subgraph Backlog["Future Backlog Upgrades"]
        %% Backlog updates linked with dotted arrows
        DataService -.->|"Dynamic Cache"| Redis[("Redis Caching Layer")]
        Redis -.-> OpenBB
        
        Chunker -.->|"Dockerized App"| Docker["Docker Containerization"]
        
        Reranker -.->|"Dynamic Thresholds"| AutoTune["Self-Tuning Optimization Engine"]
        AutoTune -.->|Auto-Update .env/DB| Grounding
        
        Reasoning -.->|"NLP Sentiment"| FinBERT["FinBERT Sentiment Model"]
        FinBERT -.-> Output
        
        OpenBB -.->|"Extended Charts"| Indicators["Technical Indicators (RSI, MACD)"]
        Indicators -.-> Reasoning
    end
    
    %% Styles
    classDef current fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef backlog fill:#fbe9e7,stroke:#d84315,stroke-width:2px,stroke-dasharray: 5 5;
    
    class User,RouteSuggest,DataService,OpenBB,Composite,Chunker,Embedder,FAISS,PostgreSQL,RAGRetriever,HybridRetriever,BM25,Merged,Reranker,Grounding,Refusal,Citations,Reasoning,LLM,Output current;
    class Redis,Docker,AutoTune,FinBERT,Indicators backlog;
```

---

## 🚀 Key Functional Modules

### 1. Ingestion & In-Memory Indicators
* **Decoupled Data Fetching:** Complies with the Dependency Inversion Principle (DIP). Relies on the `IDataProvider` interface to load stock price logs and corporate event updates from Yahoo Finance (via OpenBB).
* **Multi-Source News Routing:** Leverages `CompositeDataProvider` to route US market queries to OpenBB, and Indian market queries (`.NS` / `.BO` tickers) to **Marketaux** and **GNews** APIs, resolving Yahoo Finance's sparse data coverage on domestic tickers.

### 2. Advanced RAG Ingestion Pipeline
* **Coherent Text Chunking:** Combines article titles and summaries, splitting them using sentence boundary tracking. Chunks are sized to `600 tokens` (`2400 characters`) with a carried-over `100 token` (`400 characters`) overlap.
* **Vector Index & Metadata Mapping:** Converts text chunks into 384-dimensional dense vectors using a local `all-MiniLM-L6-v2` sentence-transformer. Embeddings are stored in a FAISS FlatL2 Index (`IndexIDMap`), while chunk metadata is saved in a PostgreSQL table (`rag_news_metadata`) matching the vector IDs.

### 3. Online Hybrid Retrieval & Neural Rerank
* **Keyword + Semantic search:** Concurrently triggers a semantic similarity search in FAISS and a keyword matching query inside an in-memory `BM25Okapi` retriever. Candidates are combined and deduplicated based on their unique `chunk_id`.
* **Cross-Encoder Reranking:** Candidate chunks are scored against queries using the local neural reranker `cross-encoder/ms-marco-MiniLM-L-6-v2` to determine exact relevance.

### 4. Grounding Gating & Citation Context
* **Early Refusal Gating:** Evaluates three strict threshold rules:
  1. Minimum candidate chunk count $\ge 1$.
  2. Peak reranker logit score $\ge -5.0$.
  3. Average logit score of the Top-3 reranker chunks $\ge -9.0$.
* **LLM Bypass:** If any grounding rule fails, the prompt builder and LLM reasoning steps are bypassed. The system immediately returns a structured `Neutral` decision: *"Insufficient evidence available to answer this question reliably."*
* **Citation-Aware Prompts:** If rules pass, the system generates sequentially numbered bracketed citations (`[1]`, `[2]`) pointing back to source publication dates and IDs.

### 5. Local LLM Reasoning
* **Private Offline Inference:** Prompts containing technical signals and formatted citation context are processed by a local `Ollama` server running the `phi3:mini` model. Output text is parsed dynamically using Regex.

---

## 🛠️ Setup & Local Execution

### 1. Requirements & Dependencies
Make sure you have **PostgreSQL** running locally and **Ollama** installed and listening on port `11434`.

Initialize the virtual environment and fetch dependencies using the `uv` tool:
```bash
# Verify uv installation and install dependency packages
uv sync
```

### 2. Configure Environment Parameters
Create a [.env](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/.env) file inside the `stock-agent/` directory:
```env
DB_URL=postgresql+asyncpg://stock_agent_admin:12345678@localhost:5432/stock_agent
MARKETAUX_API_KEY=your_key_here
GNEWS_API_KEY=your_key_here
LLM_MODEL=phi3:mini
OLLAMA_LOCAL_URL=http://localhost:11434
GROUNDING_MIN_SCORE=-7.0
GROUNDING_MIN_TOP3_AVERAGE=-10.5
GROUNDING_MIN_CHUNKS=1
```

### 3. Initialize Database Schemas
Run the database setup script to create tables and verify asyncpg drivers:
```bash
uv run python stock-agent/setup_db.py
```

### 4. Start the Application Server
Run the FastAPI application locally:
```bash
uv run python stock-agent/main.py
```
The server will boot and begin listening on **`http://127.0.0.1:8000`**. You can access the interactive Swagger documentation by navigating to `http://127.0.0.1:8000/docs`.

---

## 🧪 Verification, Evaluation & Benchmarking

### 1. Subsystem Readiness Probes
The **`GET /health`** route performs real runtime status checks of external subsystems (confirming PostgreSQL async reachability, FAISS indexes loaded on disk, and Ollama server responsiveness). It also verifies news freshness, warning if no new articles have been indexed within the last 24 hours.

### 2. Intermediate QA Debug Routes
Use debug POST endpoints to trace data through the RAG pipeline step-by-step without calling the LLM:
* **`POST /debug/retrieval`**: Evaluates individual FAISS, BM25, and merged candidate counts.
* **`POST /debug/rerank`**: Ranks candidates and returns Cross-Encoder logit scores.
* **`POST /debug/grounding`**: Breaks down rule outcomes (ALLOW/REFUSE decisions).

### 3. Automated Test Suite
Run the pytests verifying grounding regressions and E2E pathways:
```bash
# Run tests
uv run pytest stock-agent/tests/
```

### 4. Golden Dataset Evaluation Framework (Phase 2.7 & Closure)
Evaluate the active model against a golden dataset of 100+ test cases:
```bash
# Run the evaluation engine (in mock/simulation mode)
uv run python stock-agent/evaluation/run_evaluation.py --mock
```
This produces `evaluation_report.md` summarizing precision, recall, and grounding metrics.

### 5. Multi-Model Benchmarking Leaderboard (Phase 2.8)
Benchmark and rank all supported models (`qwen2.5:3b`, `mistral:7b`, `llama3.1:8b`, `phi4`, `gemma3`) on a weighted score matrix:
```bash
# Run the benchmark engine
uv run python stock-agent/evaluation/run_benchmark.py --mock
```
This generates:
* Model comparison report: [model_benchmark_report.md](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/evaluation/model_benchmark_report.md)
* Comparison rankings data: [model_rankings.json](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/evaluation/model_rankings.json)
* Captured baseline configs: `stock-agent/evaluation/baselines/*.json`

### 6. Phase 2 Closure API Endpoints
The following endpoints were added to support frontend integrations and diagnostics:
* **`GET /capabilities`**: Returns lists of supported and unsupported capabilities (e.g. `news_analysis`, `recommendations`, etc.).
* **`GET /models`**: Returns the active model configurations.
* **`GET /pipeline/status`**: Returns health checks for critical RAG pipeline components: database, FAISS index, cross-encoder reranker, and local Ollama server status.
* **`GET /evaluation/results`**: Exposes the latest golden dataset evaluation metrics scorecard.
* **`GET /benchmark/results`**: Exposes the multi-model benchmarking rankings.
* **`POST /historical-events/search`**: Exposes semantic similarity lookups over historical macro events (e.g., searching for war or tariffs).
* **`POST /signals`**: Exposes signal extraction analytics over raw recommendation texts.

---

## 📂 Codebase Tour

* [main.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/main.py): Application entry point and lifespan connection hooks.
* [src/config/settings.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/config/settings.py): Centralized configuration loader.
* [src/metrics/](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/metrics/): Metrics models and timing collection service.
* [src/llm/](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/llm/): Model registry, prompt builders, text prompts, and provider abstractions.
* [src/rag/grounding.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/grounding.py): Evaluator applying the calibrated threshold rules.
* [src/rag/hybrid_retriever.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/hybrid_retriever.py): Semantic and keyword search query merger.
* [src/rag/reranker.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/reranker.py): Logit score ranks candidates.
* [src/agent/stock_agent.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/agent/stock_agent.py): High-level brain orchestrating the analytical flow.
* [src/api/routes/debug.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/api/routes/debug.py): REST routers exposing intermediate RAG matrices.
* [evaluation/](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/evaluation/): Golden dataset, run scripts, ranking algorithms, and baseline metrics folder.

---

## 📈 Future Backlog Enhancements (Dotted Paths in Diagram)
Further project updates are planned to build on this foundational baseline:
1. **Redis Caching Layer**: Cache OpenBB provider responses to mitigate API rate limits.
2. **Dockerization**: Fully containerize database tables, the local Ollama instance, and the backend FastAPI application for unified deployment setups.
3. **FinBERT Integration**: Swap basic keyword-based sentiment metrics for a financial-grade FinBERT model to parsing complex negations in financial news.
4. **Self-Tuning Optimization**: Implement a threshold search script to dynamically search and calibrate Grounding parameters on PostgreSQL without manual reviews.
5. **Technical Indicators Expansion**: Add charting metrics (RSI, MACD, Bollinger Bands) to signal processing to enhance decision inputs.
