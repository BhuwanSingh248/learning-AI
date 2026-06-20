# 📘 Phase 2 — Metrics Framework (STEP 2.1)

---

# 🎯 Objective

Introduce observability into the entire Stock Agent pipeline.

Current situation:

```text
Request
 ↓
Processing
 ↓
Response
```

Unknown:

* Where time is spent
* Which stage is slow
* Retrieval performance
* Reranker performance
* Grounding effectiveness
* LLM latency

---

Future:

```text
Request
 ↓
Retrieval (120ms)
 ↓
Reranker (340ms)
 ↓
Grounding (2ms)
 ↓
Prompt Builder (1ms)
 ↓
LLM (2100ms)
 ↓
Response
```

Every stage becomes measurable.

---

# 🧠 Why This Matters

Before:

```text
System feels slow
```

No idea why.

---

After:

```text
LLM = 92% of latency
```

or

```text
Reranker = bottleneck
```

or

```text
Retrieval returning too many chunks
```

Data-driven optimization becomes possible.

---

# 🧩 STEP 2.1.1 — Create Metrics Models

Create:

```text
src/metrics/models.py
```

---

Create a model to capture pipeline execution metrics.

Suggested fields:

```python
total_duration_ms

retrieval_duration_ms

reranker_duration_ms

grounding_duration_ms

prompt_build_duration_ms

llm_duration_ms

chunks_retrieved

chunks_after_rerank

grounded

model_name
```

---

Keep model generic.

Future additions:

```python
tokens_generated

prompt_tokens

completion_tokens

ttft_ms

cost
```

should not require redesign.

---

# 🧩 STEP 2.1.2 — Create Metrics Service

Create:

```text
src/metrics/service.py
```

Purpose:

```text
Centralized timing collection
```

Avoid scattered:

```python
time.time()
```

throughout the codebase.

---

Suggested API:

```python
metrics.start_stage("retrieval")

metrics.end_stage("retrieval")
```

---

Responsibilities:

* Start timer
* Stop timer
* Store durations
* Produce final metrics object

---

# 🧩 STEP 2.1.3 — Instrument Retrieval

Location:

```text
RAGRetriever
```

Measure:

```text
Hybrid Retrieval duration
```

Store:

```python
retrieval_duration_ms
```

Also capture:

```python
chunks_retrieved
```

before reranking.

---

# 🧩 STEP 2.1.4 — Instrument Reranker

Location:

```text
Reranker
```

Measure:

```text
Cross Encoder execution time
```

Store:

```python
reranker_duration_ms
```

Also capture:

```python
chunks_after_rerank
```

---

# 🧩 STEP 2.1.5 — Instrument Grounding

Location:

```text
GroundingService
```

Measure:

```text
grounding_duration_ms
```

Expected:

```text
Very small (<10ms)
```

Still track it.

---

Also capture:

```python
grounded
```

decision.

---

# 🧩 STEP 2.1.6 — Instrument Prompt Builder

Measure:

```text
Prompt construction time
```

Store:

```python
prompt_build_duration_ms
```

---

Future prompts may become large.

Tracking begins now.

---

# 🧩 STEP 2.1.7 — Instrument LLM

Location:

```text
ReasoningEngine
```

Measure:

```text
Model inference time
```

Store:

```python
llm_duration_ms
```

---

Additionally capture:

```python
model_name
```

Example:

```python
phi3-mini
```

or

```python
qwen2.5
```

---

Optional if available:

```python
prompt_length

response_length
```

---

# 🧩 STEP 2.1.8 — Instrument StockAgent

Location:

```text
StockAgent
```

Measure:

```text
Total request duration
```

Store:

```python
total_duration_ms
```

---

This represents:

```text
Full user-perceived latency
```

---

# 🧩 STEP 2.1.9 — Attach Metrics To Responses

For debugging purposes.

Example:

```json
{
  "answer": "...",
  "citations": [...],
  "metrics": {
    "total_duration_ms": 2840,
    "retrieval_duration_ms": 120,
    "reranker_duration_ms": 410,
    "grounding_duration_ms": 2,
    "llm_duration_ms": 2150
  }
}
```

---

Keep optional.

Can be hidden later.

---

# 🧩 STEP 2.1.10 — Create Debug Metrics Endpoint

Add:

```http
POST /debug/analyze
```

or

```http
GET /debug/metrics
```

---

Return:

```json
{
  "answer": "...",
  "metrics": {...}
}
```

Purpose:

```text
Performance inspection
```

without reading logs.

---

# 🧩 STEP 2.1.11 — Structured Logging

Emit:

```text
Symbol
Query
Grounded
Total Duration
Retrieval Duration
Reranker Duration
Grounding Duration
LLM Duration
```

---

Example:

```text
[METRICS]

Symbol=INFY

Total=2840ms

Retrieval=120ms

Reranker=410ms

Grounding=2ms

LLM=2150ms

Grounded=True
```

---

These logs become inputs for:

```text
Langfuse
Monitoring
Evaluation
```

later.

---

# 🧩 STEP 2.1.12 — Future Compatibility

Design metrics so they can later support:

```text
Model Benchmarks

Prompt Benchmarks

Langfuse

RAGAS

A/B Testing

Cost Tracking

Token Tracking
```

without schema redesign.

---

# 🧪 Validation Checklist

Verify:

```text
✓ Retrieval timing recorded

✓ Reranker timing recorded

✓ Grounding timing recorded

✓ Prompt timing recorded

✓ LLM timing recorded

✓ Total timing recorded

✓ Metrics returned in response

✓ Metrics logged
```

---

# 🚀 Deliverables

```text
src/metrics/models.py

src/metrics/service.py

Retrieval instrumentation

Reranker instrumentation

Grounding instrumentation

Prompt instrumentation

LLM instrumentation

StockAgent instrumentation

Metrics debug endpoint
```

---

# 🎯 Definition of Done

Executing:

```json
{
  "symbol": "INFY",
  "query": "Should I buy Infosys after recent earnings?"
}
```

returns:

```json
{
  "answer": "...",
  "citations": [...],
  "metrics": {
    "total_duration_ms": 2840,
    "retrieval_duration_ms": 120,
    "reranker_duration_ms": 410,
    "grounding_duration_ms": 2,
    "llm_duration_ms": 2150
  }
}
```

---

# 🔜 Next Step

After completion:

```text
Phase 2
↓
Step 2.2
Model Benchmarking Framework
```

Compare:

```text
Phi-3

Qwen 2.5

Gemma

Llama
```

using identical prompts, context, and queries.

At that point every optimization becomes measurable rather than speculative.
