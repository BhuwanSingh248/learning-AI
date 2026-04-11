# 📈 MVP 1: Master Planning Document

This document consolidates all phase-wise planning strategies for the AI Stock Recommendation Agent. It defines the high-level roadmap and architectural vision for the system components.

---

## 🏗️ Phase 1 — Requirements & Infrastructure
**Objective:** Set up the foundational environment and technical stack.
- **Tech Stack:** OpenBB, FAISS, PostgreSQL, Mistral (Ollama), FastAPI, Python (uv).
- **Setup:** uv project initialization, database creation, and local LLM deployment.
- **Goal:** A verified, connected infrastructure ready for modular development.

---

## 🧩 Phase 2 — Boilerplate & Architecture
**Objective:** Establish a clean, modular structure.
- **Design:** Separation of concerns via folder hierarchy (`src/config`, `src/data`, etc.).
- **Initial Setup:** Environment loading, database connection pooling, and centralized logging.
- **Outcome:** A scalable codebase framework.

---

## 🧱 Phase 3 — Data Layer (Direct API Access)
**Objective:** standardize data fetching logic.
- **Data Types:** Price OHLCV, News Headlines, and Corporate Actions (Dividends/Splits).
- **Service Responsibility:** Provider abstraction, pandas normalization, and UTC timestamp alignment.
- **Outcome:** Clean, structured data pipelines.

---

## 🔍 Phase 4 — RAG + Vector Pipeline (Semantic Retrieval)
**Objective:** Enable semantic context for news analysis.
- **Architecture:** News -> Clean -> Embed -> FAISS -> PostgreSQL Metadata Store.
- **Logic:** Sentence-transformer embeddings, FAISS CPU index lookups, and metadata retrieval.
- **Outcome:** A working semantic search system for historical financial news.

---

## 📊 Phase 5 — Processing & Feature Engineering
**Objective:** Transform raw data into actionable technical signals.
- **Features:** Moving Averages, RSI, Momentum, and Corporate Action scoring.
- **MVP Scoring:** A weighted formula combining Trends, Sentiment, and Events.
- **Outcome:** A feature-rich dataset for AI reasoning.

---

## 🧠 Phase 6 — LLM Integration (Reasoning Engine)
**Objective:** Deploy the Reasoning Layer using Mistral.
- **Architecture:** Prompt design, LLM client connections, and structured output parsing.
- **Output:** Consistent "Bullish/Bearish/Neutral" decisions with explainable reasoning bullet points.

---

## 🤖 Phase 7 — Agent Orchestration
**Objective:** Pipeline integration for multi-stock analysis.
- **Flow:** User Query -> Agent Loop -> Data -> Analysis -> RAG -> LLM Reasoning -> Consolidated Output.

---

## 🌐 Phase 8 — API Gateway
**Objective:** Expose the logic via FastAPI REST endpoints.
- **Interface:** `POST /suggest` receiving symbol arrays and returning ranked suggestions.

---

## ⚙️ Phase 9 — System Optimizations
**Objective:** Performance and infrastructure hardening.
- **Optimizations:** Async I/O, Batching, Redis caching, and FinBERT sentiment refinement.
- **Infrastructure:** Dockerization and system monitoring.
