# 🎯 Task: Automated Grounding Calibration & Self-Tuning Thresholds

## 📘 Objective
Automate the manual grounding calibration and threshold selection process into a dynamic, self-tuning, and schedulable pipeline. This eliminates hardcoded calibration lists and manual environment file tuning, ensuring the gating parameters adapt dynamically as new news data is ingested.

---

## 🧩 Key Requirements

### 1. Dynamic Ticker & Company Name Resolution
* **Automatic Symbol Extraction**: Replace the hardcoded target symbols with a dynamic query to the database (e.g., `SELECT DISTINCT symbol FROM rag_news_metadata`).
* **Dynamic Company Lookup**: Integrate with data providers (like OpenBB's company profile endpoints) to automatically resolve stock tickers to clean company names (e.g., `INFY` $\rightarrow$ `Infosys`, `RELIANCE.NS` $\rightarrow$ `Reliance Industries`), removing the need for a manual `symbol_name_map`.

### 2. Automated Optimization Engine (Threshold Search)
* **Calibration Labeling**: Model the evaluation as a classification problem:
  * **Positive (Relevant) set**: Queries mapped from clean company names (expected to pass).
  * **Negative (Irrelevant) set**: Out-of-domain queries (e.g., Mars colonization, capital of France).
* **Grid Search / Optimization**: Programmatically evaluate a range of candidate thresholds for `GROUNDING_MIN_SCORE` (e.g., `-6.0` to `-2.0`) and `GROUNDING_MIN_TOP3_AVERAGE` (e.g., `-11.0` to `-7.0`).
* **F1-Score Maximization**: Select the threshold combination that maximizes the classification **F1-Score** (achieving maximum recall of relevant news while keeping false positives at zero).

### 3. Auto-Persist Configuration
* **Configuration Sync**: Implement a service that programmatically saves the chosen optimal thresholds back into the system:
  * Option A: Directly overwrite `.env` parameter configurations.
  * Option B (Recommended): Save to a `system_config` table in PostgreSQL which the running API server checks periodically.

### 4. Schedulable Pipeline Execution
* **Tuning Trigger**: Configure the tuning script to run as a nightly Cron job or a post-indexing trigger.
* **Auto-Reporting**: Generate and save updated [calibration_report.md](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/calibration_report.md) and [calibration_results.json](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/calibration_results.json) assets automatically for audit trail tracking.

---

## 🚀 Acceptance Criteria
* Running the calibration script requires no manual configuration inputs.
* The script outputs a mathematical evaluation summary showing the F1-Score optimization progress.
* System configurations are updated automatically, and uvicorn reloads dynamically (or database config caches are invalidated) to apply the new thresholds.
