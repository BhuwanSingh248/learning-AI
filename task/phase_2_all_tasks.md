# 📘 Phase 2 — Consolidated Task List (Steps 2.1 to 2.8)

## 🎯 Phase 2 Objective
Enhance the Stock Recommendation Agent by adding a robust metrics/observability framework, advanced prompting abstractions, multi-query expansion, neural reranking integrations, citation attributions, and a complete evaluation/benchmarking suite.

---

## 🗂️ Consolidated Task Checklist

### 🧩 Step 2.1 — Metrics & Observability Framework
- [x] Create metric models (`src/metrics/models.py`) to capture timing info
- [x] Create centralized metrics service (`src/metrics/service.py`) for stage-by-stage timings
- [x] Instrument RAG retrieval to track query durations and chunk counts
- [x] Instrument Cross-Encoder Reranker to track neural scoring latency
- [x] Instrument Grounding Service to measure threshold gate speeds
- [x] Instrument Prompt Builder & LLM Reasoning Engine for inference metrics
- [x] Attach metrics object to API analysis responses and structure logs

### 🧩 Step 2.2 — Prompt Builder & Recommendation Prompting
- [x] Create prompt and recommendation models (`src/llm/models.py`)
- [x] Build prompt builder service (`src/llm/prompt_builder.py`)
- [x] Externalize system prompts to text version files (`src/llm/prompts/system_v1.txt`)
- [x] Standardize JSON output schemas containing recommendation, confidence, and reasoning
- [x] Integrate prompt construction with early grounding gating refusal logic

### 🧩 Step 2.3 — Multi-Query Expansion
- [x] Design LLM-driven query expansion prompts
- [x] Generate multiple semantic sub-queries from a single user input
- [x] Retrieve and combine documents across all expanded queries in the hybrid retriever
- [x] Implement document deduplication to maintain high relevance without redundancy

### 🧩 Step 2.4 — Neural Reranking Integration
- [x] Connect Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) to rank combined BM25 and vector chunks
- [x] Map logit scores to select Top-K relevant candidates
- [x] Fine-tune reranking flow to align with grounding gate thresholds

### 🧩 Step 2.5 — Citation & Source Attribution
- [x] Construct gapless context brackets mapping citations (`[1]`, `[2]`) to source metadata
- [x] Include citation metadata (e.g. publish dates, article URLs) in final API responses
- [x] Verify that citations match ground-truth retrieve blocks

### 🧩 Step 2.6 — End-to-End Pipeline Validation
- [x] Construct query validation dataset (`tests/e2e/test_queries.json`) containing 20+ scenarios
- [x] Write E2E integration test suite (`tests/e2e/test_pipeline_e2e.py`) utilizing FastAPI test clients
- [x] Mock LLM inference to test serialization and metrics collection under CI/CD

### 🧩 Step 2.7 — Evaluation Framework
- [x] Create golden evaluation dataset (`evaluation/evaluation_dataset.json`) with 60 test cases
- [x] Write evaluation runner (`evaluation/run_evaluation.py`) to compute precision, recall, and accuracy
- [x] Output evaluation results to baseline configurations and compiled `evaluation_report.md`

### 🧩 Step 2.8 — Model Benchmarking Framework
- [x] Create supported model definitions (`src/llm/model_registry.py`)
- [x] Design generic `LLMProvider` abstractions and local `OllamaProvider` wrappers (`src/llm/providers/`)
- [x] Implement benchmarking runner (`evaluation/run_benchmark.py`) and ranking script (`evaluation/model_ranking.py`)
- [x] Remove console emojis to prevent Windows `UnicodeEncodeError` crashes
- [x] Implement simulation profile mock modes to enable instant local validation
- [x] Generate comparative reports (`evaluation/model_benchmark_report.md`) ranking registry LLMs

---

## 🎯 Definition of Done
1. API responses include detailed execution metrics and structured citation blocks.
2. The entire integrated RAG pipeline is validated by automated integration and regression tests.
3. Multiple models can be benchmarked against identical golden datasets, generating comparative score matrix reports.
