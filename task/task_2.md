# 📘 Phase 2 — External Tools Setup Guide (OpenBB + LLM + DB)

*(RAG Deferred — moved to backlog)*

---

# 🎯 Objective

Configure all external systems required for development:

* OpenBB (data source)
* Mistral via Ollama (LLM)
* PostgreSQL (database)
* Environment configuration

👉 No business logic yet — only setup & verification

---

# ⚠️ IMPORTANT

* RAG (FAISS + embeddings) is **deferred for now**
* Focus only on:

  * Data source
  * LLM
  * DB connectivity

---

# 🧱 STEP 1 — Configure OpenBB

---

## What to do:

1. Open a Python session inside your project environment
2. Initialize OpenBB login
3. Use default providers (no API key needed)

---

## What to verify:

* You can fetch stock data (example: US stock like AAPL)
* You can fetch news for a stock
* Data converts to a structured format (like table/dataframe)

---

## Notes:

* Uses free providers (Yahoo Finance)
* Indian stock support is partial
* News quality is limited (acceptable for now)

---

## Completion Criteria:

* OpenBB login works
* Data fetch works without error

---

# 🧱 STEP 2 — Configure PostgreSQL Connection

---

## What to do:

1. Ensure PostgreSQL is installed and running
2. Create a database (e.g., `stock_agent`)
3. Store DB connection string in `.env`

---

## What to verify:

* Application can connect to DB
* No authentication or connection errors

---

## Notes:

* No tables needed yet
* Only connection validation

---

## Completion Criteria:

* DB connection successful from project

---

# 🧱 STEP 3 — Configure Mistral (LLM)

---

## What to do:

1. Install Ollama (if not already installed)
2. Start Ollama service
3. Download Mistral model
4. Run Mistral locally

---

## What to verify:

* You can ask a question and get a response
* Model runs locally without crashing

---

## Notes:

* Model size ~4–5 GB
* CPU is fine (GPU not required)
* First run will be slow

---

## Completion Criteria:

* Mistral responds to prompts
* Ollama runs without issues

---

# 🧱 STEP 4 — Environment Configuration

---

## What to do:

Create a `.env` file and define:

* Database URL
* Basic system configs

---

## Suggested Variables:

* DB connection string
* Vector dimension (for future use)
* Top-K retrieval count (future use)

---

## What to verify:

* Environment variables load correctly
* Accessible from application

---

# 🧱 STEP 5 — Basic Integration Check (Manual)

---

## What to do:

Individually verify:

### OpenBB

* Fetch stock data

### PostgreSQL

* Connect successfully

### Mistral

* Responds to prompts

---

## Goal:

Ensure all systems work **independently**

---

# ⚠️ DO NOT DO YET

---

## ❌ Skip:

* FAISS integration
* Embedding pipelines
* RAG retrieval
* Agent logic
* API endpoints

---

# 🧠 Expected Output

After completing this phase:

* OpenBB ready for data fetching
* PostgreSQL ready for storage
* Mistral ready for reasoning
* Environment config working

---

# 🚀 Completion Checklist

* [ ] OpenBB working
* [ ] PostgreSQL connection verified
* [ ] Mistral running locally
* [ ] Environment variables working

---

# 🧠 Mentor Note

At this stage:

👉 You now have all **external dependencies ready**

Next phase will focus on:

➡️ Internal system building (Data Layer)

---

# 📌 Reminder

RAG (FAISS + embeddings) is intentionally **parked**
We will revisit it after core system is stable

---

# 👉 Next Step

Once done, confirm:

**“Phase 2 setup completed”**
