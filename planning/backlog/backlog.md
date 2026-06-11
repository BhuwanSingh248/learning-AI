# Future Enhancements & Backlog

The following technical items and structural plans have been bypassed entirely during the initial iterations of the MVP pipeline. They are parked here securely for future architectural expansions.

---

## 1. RAG & FAISS Vector Pipeline
*Originally designated as Phase 4 of the foundational architecture, bypassed directly to Mistral LLM wrappers to isolate determinism.*

**Outstanding Implementations:**
- **Sentence Transformation:** Integration of local `sentence-transformers` for creating dense token embeddings over retrieved historical news documentation.
- **FAISS Core:** Instantiating a `faiss-cpu` index matching the embedding dimensionality (Dim: 384 default) to run $L_2$ or Cosine similarity lookups. 
- **Postgres Alignment:** Build semantic schema extensions (e.g. `CREATE TABLE news_embeddings`) tying metadata to local FAISS indices.
- **Workflow:** Ensure the agent fetches `Top K` historic articles relevant to the ticker and injects them alongside the static technical metrics inside the prompt design phase for heightened context manipulation.

## 2. Analytical Feature Refinements (FinBERT)
*Deterministic keyword scoring (e.g. mapping explicit occurrences of 'growth' or 'loss') is exceptionally naive.*
- Swap out the foundational `NewsAnalyzer` scoring engine in favor of a robust FinBERT NLP implementation. Allows the pipeline to recognize complex negations and relative market terminology natively.

## 3. Asynchrony and System Core Optimizations
*Originally outlined in Phase 9 parameter planning.*
- **Async I/O:** Refactor `OpenBBProvider` fetches to operate asynchronously minimizing I/O bottlenecks when checking large lists of dynamic tickers simultaneously. 
- **Caching:** Integrate a `Redis` implementation handling cache hits over previously verified OpenBB responses mitigating extreme rate limits and saving bandwidth.
- **Dockerization:** Fully package the database requirements, `uv` managed Python workspace, and backend `Uvicorn` server inside structured Containers (`Dockerfile`, `docker-compose.yml`) ensuring clean deployment footprints. 

## 4. Enhanced Portfolio & Tools Expansion
- **Extended Signals:** Include explicit charting/signal dependencies like RSI, MACD, and Bollinger Bands into the `PriceAnalyzer`.
- **Advanced Agent Tooling:** Build out direct functional calling abilities in the event we map Mistral or another LLM directly into an agentic framework requiring `get_price()`, `calculate_dcf()`, etc. instead of our strictly guided deterministic logic chains.

## 5. Automated Grounding Calibration
- **Self-Tuning Thresholds:** Implement dynamic symbol resolution and automated classification F1-Score search to dynamically calibrate `GroundingService` thresholds. Detailed requirements are documented in [automated_grounding_calibration.md](file:///c:/Users/bhuwa/study/ai_stock_market/planning/backlog/automated_grounding_calibration.md).

