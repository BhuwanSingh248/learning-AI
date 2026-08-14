# 📘 Phase 2 — Complete & Consolidated Descriptive Task List

## 🎯 Phase 2 Objective & Architectural Context
Enhance the Stock Recommendation Agent by adding a robust metrics/observability framework, advanced prompting abstractions, multi-query expansion, neural reranking integrations, citation attributions, and a complete evaluation/benchmarking suite. This transitions the system from speculative reasoning to measurable, data-driven outcomes.

---

## 🗂️ Consolidated Descriptive Task Checklist

### 🧩 Step 2.1 — Metrics & Observability Framework
**Objective:** Expose detailed latency metrics per processing stage (Retrieval, Reranking, Grounding, Prompt Construction, and LLM inference) to make system optimization transparent and data-driven.

* **Checklist:**
  - [x] **STEP 2.1.1: Create Metrics Models:** Design `src/metrics/models.py` capturing durations, chunk counts (retrieved vs. reranked), grounding state, and active model names.
  - [x] **STEP 2.1.2: Create Metrics Service:** Define `src/metrics/service.py` to collect stage timings using clean `.start_stage()` and `.end_stage()` APIs.
  - [x] **STEP 2.1.3: Instrument Retrieval:** Track time spent in hybrid vector (FAISS) and keyword (BM25) lookups, storing `retrieval_duration_ms` and `chunks_retrieved`.
  - [x] **STEP 2.1.4: Instrument Reranker:** Measure Cross-Encoder reranker execution time (`reranker_duration_ms`) and record `chunks_after_rerank`.
  - [x] **STEP 2.1.5: Instrument Grounding:** Measure duration of the threshold evaluations (`grounding_duration_ms`) and capture the final `grounded` flag.
  - [x] **STEP 2.1.6: Instrument Prompt Builder:** Measure context formatting and citation injection latency (`prompt_build_duration_ms`).
  - [x] **STEP 2.1.7: Instrument LLM:** Track reasoning model response generation latency (`llm_duration_ms`).
  - [x] **STEP 2.1.8: Instrument StockAgent:** Capture total perceived user request latency (`total_duration_ms`) at the orchestrator boundary.
  - [x] **STEP 2.1.9: Attach Metrics to Responses:** Append structured metrics data into public REST responses for client accessibility.
  - [x] **STEP 2.1.10: Create Debug Endpoint:** Extend or implement `/debug/analyze` to return pipeline diagnostics.
  - [x] **STEP 2.1.11: Structured Logging:** Log timing parameters as key-value pairs format `[METRICS] Symbol=INFY Total=Xms ...` for external auditing tools.
  - [x] **STEP 2.1.12: Future Compatibility:** Ensure schema compatibility for token count, completion speed, and A/B test routing variables.

---

### 🧩 Step 2.2 — Prompt Builder & Recommendation Prompting
**Objective:** Transform raw grounded evidence and indicators into structured prompts that guide the LLM to output predictable JSON conforming to recommendation schemas.

* **Checklist:**
  - [x] **STEP 2.2.1: Create Prompt Models:** Design `src/llm/models.py` implementing structured parameters (`RecommendationPrompt`, `PromptPayload`) to represent inputs.
  - [x] **STEP 2.2.2: Create PromptBuilder:** Implement `src/llm/prompt_builder.py` responsible for compiling system and user context prompts.
  - [x] **STEP 2.2.3: Define System Prompt:** Externalize system prompt guidelines to `src/llm/prompts/system_v1.txt` to enforce factual grounding.
  - [x] **STEP 2.2.4: Build User Prompt Template:** Map retrieved news summaries and sequentially-indexed citations dynamically into the user context prompt.
  - [x] **STEP 2.2.5: Standardize Output Schema:** Add strict instructions formatting output as a JSON dictionary matching required properties.
  - [x] **STEP 2.2.6: Create RecommendationResponse Model:** Implement Pydantic validation for the fields: recommendation (BUY/SELL/HOLD), confidence, and citations.
  - [x] **STEP 2.2.7: Prompt Versioning:** Structure prompt files under `src/llm/prompts/` (e.g. `system_v1.txt`, `system_v2.txt`) to allow regression benchmarking.
  - [x] **STEP 2.2.8: Unit Tests:** Add test cases evaluating behavior under strong, weak, and empty citation context sets.
  - [x] **STEP 2.2.9: Integration with Grounding:** Connect grounding outcomes to prompt creation; short-circuit to refusal outputs immediately if grounding fails.
  - [x] **STEP 2.2.10: Debug Endpoint:** Expose compiled raw prompt texts on the `/debug/analyze` route for inspection.

---

### 🧩 Step 2.3 — Reasoning Engine
**Objective:** Convert raw LLM text streams into typed, validated, and citation-consistent investment recommendations.

* **Checklist:**
  - [x] **STEP 2.3.1: Create Recommendation Models:** Implement `src/reasoning/models.py` specifying the `RecommendationType` enum (`BUY`, `HOLD`, `SELL`, `INSUFFICIENT_DATA`).
  - [x] **STEP 2.3.2: Create Reasoning Engine:** Implement `src/reasoning/reasoning_engine.py` to interface with providers, parsing responses into structured models.
  - [x] **STEP 2.3.3: Enforce JSON Output:** Configure API execution parameters to demand structured JSON outputs and restrict plain essay text.
  - [x] **STEP 2.3.4: JSON Parsing Layer:** Add regex-based JSON cleaners to extract dictionaries even if models wrap outputs in markdown code blocks.
  - [x] **STEP 2.3.5: Recommendation Validation:** Validate that output actions match exact enum values; fallback to `INSUFFICIENT_DATA` if unrecognized choices are found.
  - [x] **STEP 2.3.6: Confidence Validation:** Clamp model confidence ratings within the `0.0` to `1.0` boundaries.
  - [x] **STEP 2.3.7: Citation Validation:** Compare returned citation indices against supplied indices; strip references to documents that were not part of the source context.
  - [x] **STEP 2.3.8: Grounding Integration:** Avoid calling the LLM entirely if the grounding gate rejects input, returning a structured refusal directly.
  - [x] **STEP 2.3.9: Metrics Integration:** Record `llm_duration_ms` and model metadata inside the pipeline metrics storage.
  - [x] **STEP 2.3.10: StockAgent Integration:** Update agent flow to leverage the new reasoning engine instead of direct text responses.
  - [x] **STEP 2.3.11: API Response Cleanup:** Replace stringified nested JSON outputs in `/analyze` responses with clean, flat schemas.
  - [x] **STEP 2.3.12: Unit Tests:** Cover JSON parsing fallbacks, invalid enums, out-of-bounds confidence values, and citation verification tests.

---

### 🧩 Step 2.4 — Signal Engine & Recommendation Scoring
**Objective:** transition from raw LLM sentiment analysis to deterministic, evidence-based recommendations by extracting explicit signals and aggregating scores in the application layer.

* **Checklist:**
  - [x] **STEP 2.4.1: Create Signal Models:** Design `src/signals/models.py` introducing `SignalType` (`POSITIVE`, `NEGATIVE`, `RISK`, `MARKET`) and signal structures.
  - [x] **STEP 2.4.2: Create Signal Extraction Engine:** Implement `src/signals/signal_engine.py` to identify occurrences of earnings, contracts, exits, and risks.
  - [x] **STEP 2.4.3: Signal Scoring:** Establish scoring weights (Positive = +1.0, Negative = -1.0, Risk = -0.5) inside extracted models.
  - [x] **STEP 2.4.4: Recommendation Score Calculator:** Implement `src/signals/scoring.py` computing cumulative signal values.
  - [x] **STEP 2.4.5: Recommendation Thresholds:** Apply score logic to map final actions (`score >= 2.0` -> `BUY`, `score <= -1.0` -> `SELL`, otherwise -> `HOLD`).
  - [x] **STEP 2.4.6: Confidence Calculation:** Compute confidence based on signal density, grounding results, and evidence weights.
  - [x] **STEP 2.4.7: LLM as Analyst:** Adjust LLM tasks to focus on extracting fact-based signal patterns rather than deciding the final stock action.
  - [x] **STEP 2.4.8: Recommendation Explanation:** Return signal lists in responses to explain the recommendation's mathematical backing.
  - [x] **STEP 2.4.9: Metrics Integration:** Track count parameters (`positive_signal_count`, etc.) under the metrics telemetry structure.
  - [x] **STEP 2.4.10: API Integration:** Incorporate the signal processing stages into the main active StockAgent pipeline.

---

### 🧩 Step 2.5 — Historical Event Learning & Analog Analysis
**Objective:** Cross-reference current news events with similar historical occurrences to contextualize decisions with historical outcome statistics.

* **Checklist:**
  - [x] **STEP 2.5.1: Create Historical Event Models:** Design `src/history/models.py` capturing event metadata and subsequent stock returns over 1d, 7d, 30d, and 90d.
  - [x] **STEP 2.5.2: Create Event Store:** Implement `src/history/event_store.py` providing storage APIs for macro events.
  - [x] **STEP 2.5.3: Event Embeddings:** Index event descriptions in a local semantic store (FAISS or separate history index).
  - [x] **STEP 2.5.4: Similar Event Retriever:** Implement `src/history/event_retriever.py` to find historical matches using cosine distance.
  - [x] **STEP 2.5.5: Outcome Analyzer:** Build outcome calculators (`src/history/outcome_analyzer.py`) aggregating returns across relevant lookups.
  - [x] **STEP 2.5.6: Sector-Level Learning:** Group historical stock reactions by industry sectors (e.g. tech, defense, manufacturing) to map broad sector trends.
  - [x] **STEP 2.5.7: Historical Signal Generation:** Generate signals expressing historical outcomes and join them with the active scoring engine.
  - [x] **STEP 2.5.8: Recommendation Integration:** Wire historical retrievals into the agent orchestrator pipeline.
  - [x] **STEP 2.5.9: Explainability:** Output similarity scores and historical returns in the API output to trace decisions.
  - [x] **STEP 2.5.10: Metrics:** Capture matching statistics, similarity averages, and query counts.
  - [x] **STEP 2.5.11: Initial Dataset:** Populate `data/historical_events.json` with major market events (COVID, rate hikes, wars, trade tariffs).

---

### 🧩 Step 2.6 — End-to-End Recommendation Pipeline Validation
**Objective:** Verify integration correctness, reliability, and observability across all RAG components from input to API response.

* **Checklist:**
  - [x] **STEP 2.6.1: Create Test Dataset:** Create `tests/e2e/test_queries.json` with 20+ queries covering positive, negative, and out-of-domain prompts.
  - [x] **STEP 2.6.2: Validate Retrieval:** Test that retrieval query runs yield chunks and log retrieval durations.
  - [x] **STEP 2.6.3: Validate Reranker:** Ensure rerankers produce score spreads where relevant queries score higher than irrelevant ones.
  - [x] **STEP 2.6.4: Validate Grounding:** Test that grounding gating allows relevant queries and refuses invalid ones.
  - [x] **STEP 2.6.5: Validate Prompt Builder:** Ensure generated prompts contain system directions, citations, and queries without being blank.
  - [x] **STEP 2.6.6: Validate Reasoning Engine:** Ensure reasoning components parse output JSON and avoid exposing raw LLM outputs.
  - [x] **STEP 2.6.7: Validate Signal Engine:** Test that signal extractors parse positive, negative, and risk items accurately.
  - [x] **STEP 2.6.8: Validate Final Recommendation:** Check that final choices belong to the supported recommendation type enums.
  - [x] **STEP 2.6.9: API Response Audit:** Confirm `/analyze` endpoints output clean, flat JSON instead of nested stringified JSON blocks.
  - [x] **STEP 2.6.10: Metrics Validation:** Verify that timing parameters (retrieval, reranking, grounding, LLM, total) are populated in responses.
  - [x] **STEP 2.6.11: Failure Scenario Testing:** Test pipeline behavior under edge cases (unsupported symbols, empty queries, weak evidence).
  - [x] **STEP 2.6.12: Create Validation Report:** Compile all outcomes into `phase_2_6_validation_report.md`.

---

### 🧩 Step 2.7 — Evaluation Framework
**Objective:** Establish a repeatable and measurable framework to evaluate RAG retrieval, grounding, and recommendation quality.

* **Checklist:**
  - [x] **STEP 2.7.1: Create Golden Evaluation Dataset:** Create `evaluation/evaluation_dataset.json` with 60 gold test cases (positive, negative, risk, refusal).
  - [x] **STEP 2.7.2: Retrieval Evaluation:** Compute Recall@K and Precision@K to measure chunk quality.
  - [x] **STEP 2.7.3: Grounding Evaluation:** Measure true/false positives and negatives to calculate Grounding F1, Precision, and Recall.
  - [x] **STEP 2.7.4: Signal Evaluation:** Compute precision and recall for extracted signal classifications.
  - [x] **STEP 2.7.5: Recommendation Evaluation:** Calculate recommendation accuracy against expected gold outcomes.
  - [x] **STEP 2.7.6: Citation Evaluation:** Compute citation accuracy and verify references map back to valid source text.
  - [x] **STEP 2.7.7: Consistency Evaluation:** Execute identical queries 10 times to measure output stability.
  - [x] **STEP 2.7.8: Hallucination Evaluation:** Check for unsupported claims and hallucinated citations (target < 5%).
  - [x] **STEP 2.7.9: Performance Evaluation:** Measure average, P95, and max latency values per stage.
  - [x] **STEP 2.7.10: Create Evaluation Runner:** Build `evaluation/run_evaluation.py` to automate evaluations.
  - [x] **STEP 2.7.11: Generate Evaluation Report:** Output metric details to `evaluation_report.md`.
  - [x] **STEP 2.7.12: Baseline Storage:** Save baseline outputs inside `evaluation/baselines/` for comparison.

---

### 🧩 Step 2.8 — Model Benchmarking Framework
**Objective:** Compare model latency, grounding accuracy, and reasoning consistency across multiple LLMs to guide model selection.

* **Checklist:**
  - [x] **STEP 2.8.1: Create Model Registry:** Create `src/llm/model_registry.py` defining supported models (`qwen2.5:3b`, `mistral:7b`, `llama3.1:8b`, `phi4`, `gemma3`).
  - [x] **STEP 2.8.2: Create Provider Abstraction:** Create `src/llm/providers/` containing `base.py` and local `ollama.py` classes.
  - [x] **STEP 2.8.3: Reuse Evaluation Dataset:** Set up the benchmark runner to consume the golden evaluation dataset.
  - [x] **STEP 2.8.4: Create Benchmark Runner:** Build `evaluation/run_benchmark.py` to evaluate each model in the registry.
  - [x] **STEP 2.8.5: Recommendation Quality Metrics:** Collect recommendation accuracy and grounding gate rates per model.
  - [x] **STEP 2.8.6: Performance Metrics:** Record average latency, P95 latency, and generation speed per model.
  - [x] **STEP 2.8.7: Resource Utilization Metrics:** Record CPU and RAM footprint during execution.
  - [x] **STEP 2.8.8: Consistency Testing:** Run repeating queries to score decision stability per model.
  - [x] **STEP 2.8.9: Hallucination Comparison:** Track citation validity rates for each model.
  - [x] **STEP 2.8.10: Generate Benchmark Report:** Output comparative metrics to `evaluation/model_benchmark_report.md`.
  - [x] **STEP 2.8.11: Create Model Ranking Engine:** Build `evaluation/model_ranking.py` using weighted scoring logic.
  - [x] **STEP 2.8.12: Baseline Storage:** Write baseline stats to `evaluation/baselines/{model_name}_baseline.json`.
  - [x] **STEP 2.8.13: Console Compatibility:** Avoid output emojis in logs to prevent Windows encoding crashes.
  - [x] **STEP 2.8.14: Simulation Profile Mock Mode:** Implement simulated profiles for registry models (`--mock` flag) to allow instant local validation.

---

### 🧩 Step 2.9 — Phase 2 Closure & Missing Items Backlog
**Objective:** Address identified critical functional gaps, API improvements, evaluation coverage, historical retrieval engine gaps, frontend readiness, and operational requirements.

* **Checklist:**
  - [x] **STEP 2.9.1: Query Intent Routing:** Implement intent router bypassing RAG for `FUNDAMENTAL` query intent in `src/query_router/`.
  - [x] **STEP 2.9.2: Grounding Threshold Calibration:** Review and relax default grounding thresholds (`GROUNDING_MIN_SCORE = -7.0`, `GROUNDING_MIN_AVERAGE_SCORE = -10.5`) in `src/config/settings.py` and `.env`.
  - [x] **STEP 2.9.3: Empty Symbol Diagnostics:** Add detailed `failure_type` to RAG and grounding refusals.
  - [x] **STEP 2.9.4: Add Supported Capability Metadata:** Implement `GET /capabilities` returning supported/unsupported features.
  - [x] **STEP 2.9.5: Model Metadata Endpoint:** Implement `GET /models` returning active reasoning model configurations.
  - [x] **STEP 2.9.6: Pipeline Status Endpoint:** Implement `GET /pipeline/status` checking connectivity of FAISS, DB, reranker, and Ollama.
  - [x] **STEP 2.9.7: Evaluation Dataset Coverage:** Expand golden dataset to 102 cases covering positive/negative/risk news, refusal, and historical queries.
  - [x] **STEP 2.9.8: Benchmark Runner Validation:** Verify execution paths for registry models Mistral, Qwen, Llama, and Phi4 in `run_benchmark.py`.
  - [x] **STEP 2.9.9: Historical Events Validation:** Mark dataset as seed data and add documentation `data/historical_events_readme.md`.
  - [x] **STEP 2.9.10: Historical Similarity Evaluation:** Add unit tests validating similarity-based semantic lookups (`Russia-Ukraine War`) in `tests/history/test_history.py`.
  - [x] **STEP 2.9.11: Missing Visualization Endpoints:** Add endpoints `GET /evaluation/results`, `GET /benchmark/results`, `POST /historical-events/search`, and `POST /signals` to enable UI representation.
  - [x] **STEP 2.9.12: Recommendation Explainability:** Return aggregated signals, historical matches, and citations in the JSON response model of the `/analyze` endpoint.
  - [x] **STEP 2.9.13: News Freshness Monitoring:** Implement freshness health checks in `/health` (alerting if no news indexed in last 24h).
  - [x] **STEP 2.9.14: Duplicate Indexing Protection:** Prevent duplicate article insertions in `NewsIndexer` by verifying MD5 hashes.
  - [x] **STEP 2.9.15: RAG Observability:** Build relational database logging table `rag_pipeline_metrics` (via `MetricRecord`) and persist latency and grounding gate stats.
