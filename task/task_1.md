# 📘 Phase 1 — Dependency Installation Guide (No Code Version)

---

# 🎯 Objective

Set up all required dependencies **step-by-step**, ensuring each component works before moving forward.

⚠️ Important Rule:
Install → Verify → Then proceed.
Do NOT install everything at once.

---

# 🧱 Step-by-Step Instructions

---

## ✅ STEP 1 — Install Environment Manager (uv)

### What to do:

* Install `uv` using pip
* Verify installation by checking version

### Why:

* Manages dependencies efficiently
* Keeps project isolated and clean

---

## ✅ STEP 2 — Initialize Project

### What to do:

* Create a new project using uv
* Navigate into the project folder

### Why:

* Sets up project structure
* Creates dependency configuration file

---

## ✅ STEP 3 — Install Core Libraries

### Libraries:

* pandas
* numpy

### Why:

* pandas → data manipulation (core of your system)
* numpy → numerical operations (used by FAISS and ML)

### Verification:

* Ensure both libraries import without errors

---

## ✅ STEP 4 — Install OpenBB (Data Source)

### What to do:

* Install OpenBB package
* Initialize login (anonymous is fine)
* Try fetching sample stock data

### Why:

* This is your **primary data source**
* Provides:

  * stock prices
  * news
  * corporate actions

⚠️ Do NOT proceed unless this works properly

---

## ✅ STEP 5 — Install Database Dependencies

### Libraries:

* sqlalchemy
* psycopg2-binary

### Why:

* sqlalchemy → database abstraction layer
* psycopg2 → PostgreSQL connector

### Verification:

* Ensure Python can import these libraries

---

## ✅ STEP 6 — Install FAISS (Vector Search Engine)

### What to do:

* Install FAISS CPU version

### Why:

* Core of your RAG system
* Performs similarity search on embeddings

### Verification:

* Create a small test index
* Add a vector
* Ensure count increases

---

## ✅ STEP 7 — Install Embedding Model Library

### Library:

* sentence-transformers

### Why:

* Converts text → vectors
* Required for FAISS

### Verification:

* Load model
* Generate embedding
* Ensure output dimension is 384

---

## ✅ STEP 8 — Install Transformers Library

### Library:

* transformers

### Why:

* Future use:

  * sentiment models (FinBERT)
  * advanced NLP

👉 Not critical now, but install early

---

## ✅ STEP 9 — Install API Framework

### Libraries:

* fastapi
* uvicorn

### Why:

* Will expose your backend as API
* Not used immediately, but required later

---

## ✅ STEP 10 — Install Environment Config Support

### Library:

* python-dotenv

### Why:

* Loads environment variables
* Used for:

  * DB connection
  * configs

---

# 🧠 Final Verification Checklist

Before moving forward, confirm:

* pandas and numpy working
* OpenBB successfully fetching data
* PostgreSQL connector installed
* FAISS working with sample vector
* Embedding model generating vectors
* All libraries import without errors

---

# ⚠️ Common Mistakes

* Installing everything together → hard to debug
* Skipping OpenBB test → breaks later phases
* Not verifying FAISS → RAG fails later
* Ignoring embedding dimension → mismatch errors

---

# 🎯 Completion Criteria

You are done with Phase 1 dependencies when:

* All libraries install successfully
* All components work independently
* No import or runtime errors

---

# 🚀 Next Step

Once done, confirm:

👉 “Phase 1 dependencies done”

Then we move to:

➡️ Infrastructure validation (DB + FAISS + OpenBB together)
➡️ Phase 2 — Clean architecture setup

---
