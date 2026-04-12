# Phase 7.1 — RAG System Design

> **Status**: Design complete. No implementation yet.  
> **Next Step**: Phase 7.2 — FAISS indexing & embedding implementation.

---

## 1. What is RAG?

**RAG = Retrieval-Augmented Generation**

Instead of relying purely on the LLM's baked-in training knowledge,
we fetch *current, relevant* context and inject it into the prompt at
query time. For a stock agent this means:

| Step | What happens |
|------|-------------|
| Store | News articles are chunked, embedded, and saved in FAISS |
| Retrieve | At analysis time, Top-K news items relevant to the symbol are pulled |
| Augment | Those news snippets are appended to the LLM prompt |

---

## 2. Where does RAG sit?

### Before (Phase 1–6):

```
Data → Processing → Analysis → Reasoning (LLM) → Agent → API
```

### After (Phase 7+):

```
Data → Processing → Analysis
                        ↓
                    RAG Layer      ← NEW
                        ↓
                Reasoning (LLM)
                        ↓
                    Agent → API
```

RAG sits **between Analysis and LLM Reasoning** only.  
It has no visibility into data fetching or scoring.

---

## 3. RAG Responsibilities (SRP)

### ✅ RAG WILL:
- Store news embeddings (offline indexing phase)
- Retrieve Top-K relevant news for a given symbol/query
- Return plain text snippets ready to inject into the LLM prompt

### ❌ RAG will NOT:
- Fetch data from APIs → that is `src/data/`
- Clean or chunk raw text → that is `src/processing/`
- Score or weight signals → that is `src/analysis/`
- Build/send prompts or call the LLM → that is `src/llm/`
- Replace the analysis layer

---

## 4. Data Flows

### Offline Flow — Indexing (batch)

```
Raw News Articles
      ↓
  Text Chunking / Cleaning     (src/processing — future)
      ↓
  Embedding Model              (e.g., sentence-transformers)
      ↓
  FAISS Index                  (stored on disk)
      ↓
  News Store (ID → text map)   (JSON / SQLite)
```

### Online Flow — Query Time

```
symbol = "AAPL", query = "recent earnings performance"
      ↓
  Query embedding produced
      ↓
  FAISS similarity search → Top-5 IDs
      ↓
  Lookup IDs in news store → text snippets
      ↓
  RetrievalResult(symbol, items=[...])
      ↓
  Injected into LLM prompt by PromptBuilder
```

---

## 5. Inputs & Outputs

### Input to `RAGRetriever.retrieve()`

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol`  | `str` | Ticker being analysed (e.g. `"AAPL"`) |
| `query`   | `str` | Optional free-text context hint |
| `top_k`   | `int` | Max results; defaults to **5** for MVP |

### Output — `RetrievalResult`

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | The ticker |
| `items`  | `list[str]` | Top-K news snippets, most-similar first |

---

## 6. Retrieval Strategy

### MVP

| Choice | Value |
|--------|-------|
| Search type | Pure similarity search |
| Index | FAISS (flat L2 or cosine) |
| Top-K | 5 |

### Backlog (future phases)

- Hybrid search — keyword + vector combined score
- Time-weighted retrieval — prefer recent news
- Symbol-filtered search — filter by ticker metadata

---

## 7. Prompt Integration

### Current Prompt (Phase 1–6):

```
--- START OF DATA ---
Stock: AAPL
Trend: Bullish
Momentum: 0.87
Sentiment: 0.62
Event Score: 0.40
--- END OF DATA ---

You are a professional financial analyst...
```

### New Prompt (Phase 7+):

```
--- START OF DATA ---
Stock: AAPL
Trend: Bullish
Momentum: 0.87
Sentiment: 0.62
Event Score: 0.40
--- END OF DATA ---

--- RELEVANT NEWS CONTEXT ---
- Apple Q2 earnings beat expectations by 12%, driven by iPhone sales.
- Analysts at Goldman Sachs raised AAPL price target to $220.
- iPhone 17 supply chain signals strong pre-order demand.
- Apple announced $90B buyback program this quarter.
- Consumer sentiment for Apple brand at 5-year high.
--- END OF NEWS CONTEXT ---

You are a professional financial analyst...
```

The `PromptBuilder` will be extended (Phase 7.2) to accept an optional
`RetrievalResult` and append the news block.  The LLM layer never calls
`RAGRetriever` directly — the `ReasoningEngine` will orchestrate both.

---

## 8. SOLID Principles Applied

| Principle | How it applies |
|-----------|---------------|
| **SRP** | `RAGRetriever` does one thing: retrieve relevant context |
| **DIP** | LLM depends on `RetrievalResult` (plain data), not FAISS internals |
| **OCP** | Vector DB, Top-K, and metric can be swapped without touching LLM/analysis |

---

## 9. Final Architecture Map

```
src/
├── data/           ← Providers, fetchers (Data Layer)
├── processing/     ← Cleaning, normalisation
├── analysis/       ← Signal engineering
│
├── rag/            ← NEW: Retrieval-Augmented Generation Layer
│   ├── __init__.py         (package + public exports)
│   └── retriever.py        (RAGRetriever + RetrievalResult stubs)
│
├── llm/            ← Prompt building + LLM calls + response parsing
│   ├── prompt_builder.py   (to be extended in Phase 7.2)
│   └── reasoning.py        (to be extended in Phase 7.2)
│
└── agent/          ← Orchestration → API
```

---

## 10. Completion Checklist (Phase 7.1)

- [x] RAG role understood: news retrieval context enrichment only
- [x] Integration point defined: between Analysis and LLM Reasoning
- [x] Offline (indexing) data flow documented
- [x] Online (query-time) data flow documented
- [x] Inputs (`symbol`, `query`, `top_k`) and output (`RetrievalResult`) defined
- [x] Retrieval strategy chosen: similarity search, Top-K = 5 (MVP)
- [x] Prompt integration strategy documented
- [x] `src/rag/` package scaffold created with typed stubs
- [x] SOLID principles mapped

---

> ⛔ **Do NOT proceed to Phase 7.2 until this design is reviewed.**  
> No FAISS code. No real embeddings. No LLM modifications.
