# 📘 AI Stock Agent — Senior Engineering Roadmap

---

# 🧠 Project Context

This project is a **production-style AI stock analysis system** with:

* Data → Processing → Analysis → RAG → LLM → Agent → API
* Built with SOLID principles
* Currently functional (MVP complete)

---

# 🎯 Goal

Evolve system into:

👉 **Advanced RAG-powered, measurable, production-grade AI system**

---

# ⚠️ Core Principle

> Do NOT build everything at once
> Focus on **depth, not breadth**

---

# 🧱 PHASE 0 — LLM Stability (BLOCKER)

---

## 🎯 Goal

Ensure reliable local LLM performance

---

## Action

Replace Mistral (unstable locally) with:

### 🥇 Recommended

* Phi-3 Mini (GGUF, quantized)

### 🥈 Alternative

* Llama 3 8B (quantized)

---

## Reason

* Lower RAM usage
* Faster inference
* More stable locally

---

# 🥇 PHASE 1 — Advanced RAG (CORE UPGRADE)

⏱️ Duration: 2–3 weeks

---

## 🎯 Goal

Improve **retrieval quality + reasoning grounding**

---

## Tasks

### 1. Chunking Layer

* Chunk size: 500–800 tokens
* Overlap: 100 tokens
* Store:

  * chunk_id
  * source_id
  * text

---

### 2. Hybrid Retrieval

* Vector search (FAISS)
* * Keyword search (BM25)
* Merge results

---

### 3. Reranker

* Cross-encoder (local)
* Input: query + chunk pairs
* Re-rank top 20 → keep top 5

---

### 4. Citation System

* Each chunk gets ID
* LLM receives numbered references
* API returns structured citations

---

### 5. Refusal Logic

* If retrieval confidence is low:

  * Do NOT call LLM
  * Return safe fallback

---

## ❌ Do NOT

* Add LangGraph
* Do fine-tuning
* Optimize prematurely

---

# 🥈 PHASE 2 — Observability & Metrics

⏱️ Duration: 1–2 weeks

---

## 🎯 Goal

Make system **measurable and debuggable**

---

## Metrics

* Total latency
* Time to first token (TTFT)
* Tokens/sec
* Failure rate
* Citation coverage
* Cost per request (approx)

---

## Tools

* Langfuse (recommended)

---

## Outcome

Ability to answer:

👉 “Is the system improving?”

---

# 🥉 PHASE 3 — Model & Prompt Experiments

⏱️ Duration: 1–2 weeks

---

## 🎯 Goal

Understand LLM behavior

---

## Tasks

* Compare models:

  * Phi-3
  * Llama
  * Mistral (optional revisit)

* Temperature experiments

* Prompt version tracking (prompt gating)

---

# 🟡 PHASE 4 — Extended Learning Features

⏱️ Optional

---

## 1. PDF Ingestion

Pipeline:

* PDF → text → chunk → embed → RAG

---

## 2. RAG Evaluation

Use:

* RAGAS

---

## 3. LangChain / LangGraph

Only if needed — not mandatory

---

# 🔴 PHASE 5 — Training (Advanced)

⏱️ Last priority

---

## 🎯 Goal

Improve model via fine-tuning

---

## Tools

* TRL (HuggingFace)

---

## Steps

### 1. SFT (LoRA / QLoRA)

* Train on domain-specific prompts

---

### 2. DPO (Preference Tuning)

* Compare outputs
* Train ranking model

---

## ⚠️ Warning

* Requires dataset
* Requires evaluation pipeline
* Easy to overfit

---

# ⚫ LOW PRIORITY (FINAL)

---

* Async processing
* Redis caching
* Multi-LLM orchestration
* Portfolio optimization
* Full infra scaling

---

# 🧠 Weekly Execution Plan (20 hrs/week)

---

## Week 1–2

* Chunking
* Hybrid retrieval

---

## Week 3

* Reranker
* Citation system

---

## Week 4

* Metrics & logging

---

# 🧠 Key Engineering Insight

---

## System Quality Depends On:

```text
Retrieval Quality → Context Quality → LLM Output Quality
```

---

# 🚀 Immediate Next Step

---

1. Replace LLM → Phi-3 Mini (quantized)
2. Start Phase 1:

   * Chunking design

---

