# 📘 Phase 7 — RAG Integration (STEP 1: System Design & Placement)

---

# 🎯 Objective (This Step Only)

Design:

👉 Where RAG fits in your system
👉 What it will do
👉 What it will NOT do

---

# 🧠 Why This Step Matters

If you plug RAG incorrectly:

❌ messy system
❌ slow performance
❌ bad outputs

If done right:

✅ smarter reasoning
✅ better explanations
✅ scalable design

---

# 🧩 STEP 7.1.1 — Understand RAG Role

---

## RAG = Retrieval-Augmented Generation

👉 It means:

* Store knowledge (news)
* Retrieve relevant context
* Feed into LLM

---

## In YOUR system:

👉 RAG is ONLY for:

* News understanding
* Context enrichment

---

## NOT for:

❌ price prediction
❌ scoring
❌ calculations

---

# 🧩 STEP 7.1.2 — Identify Integration Point

---

## Current System:

```text
Data → Processing → Analysis → Reasoning → Output
```

---

## New System:

```text
Data → Processing → Analysis
              ↓
           RAG Layer
              ↓
        Reasoning (LLM)
              ↓
            Output
```

---

👉 RAG sits **between Analysis and LLM**

---

# 🧩 STEP 7.1.3 — Define RAG Responsibilities

---

## RAG Layer should:

* Store news embeddings
* Retrieve relevant news
* Provide context to LLM

---

## RAG should NOT:

* Fetch data
* Clean data
* Score data
* Replace analysis layer

---

# 🧩 STEP 7.1.4 — Define Data Flow

---

## Offline Flow (Indexing)

```text
News → Processing → Embedding → FAISS → Store IDs
```

---

## Online Flow (Query Time)

```text
User Query
 ↓
Signals generated
 ↓
Query embedding
 ↓
FAISS search (Top-K)
 ↓
Retrieve news
 ↓
Send to LLM
```

---

# 🧩 STEP 7.1.5 — Define Inputs & Outputs

---

## Input to RAG:

* symbol
* optional query (e.g., "recent performance")

---

## Output from RAG:

```text
Top-K relevant news items
```

---

👉 This will be appended to prompt

---

# 🧩 STEP 7.1.6 — Decide Retrieval Strategy

---

## For MVP:

* Use similarity search
* Top-K = 5

---

## Later (Backlog):

* hybrid search (keyword + vector)
* time-weighted retrieval

---

# 🧩 STEP 7.1.7 — Define Prompt Integration

---

## Current Prompt:

```text
Signals only
```

---

## New Prompt:

```text
Signals + Retrieved News Context
```

---

👉 This is the biggest upgrade

---

# 🧠 SOLID Principles Applied

---

## 🟢 SRP

RAG layer:
👉 ONLY retrieval logic

---

## 🟢 DIP

LLM does NOT know:
👉 where context comes from

---

## 🟢 OCP

You can:

* change vector DB
* improve retrieval
* add filters

---

# 🧠 Final Architecture

---

```text
Data → Processing → Analysis
 ↓
RAG (YOU ARE ADDING THIS)
 ↓
Reasoning (LLM)
 ↓
Agent → API
```

---

# 🚀 Completion Checklist

* [ ] You understand RAG role
* [ ] You know where it fits
* [ ] Data flow is clear
* [ ] Boundaries are defined

---

# ⛔ Do NOT Proceed Yet

Do NOT:

* Write FAISS code
* Generate embeddings
* Modify LLM
