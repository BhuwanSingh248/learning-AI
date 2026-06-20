import os
import json
import glob
from typing import Dict, Any, List

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINES_DIR = os.path.join(EVAL_DIR, "baselines")
REPORT_PATH = os.path.join(EVAL_DIR, "model_benchmark_report.md")
RANKING_JSON_PATH = os.path.join(EVAL_DIR, "model_rankings.json")

def compile_rankings():
    baseline_files = glob.glob(os.path.join(BASELINES_DIR, "*_baseline.json"))
    
    if not baseline_files:
        print("Warning: No model baseline JSON files found in baselines/ directory.")
        return
        
    models_data = []
    
    for filepath in baseline_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            model_name = data.get("model_name", "unknown")
            metrics = data.get("metrics", {})
            latency = data.get("latency_ms", {})
            consistency_list = data.get("consistency", [])
            
            # Extract basic metric values
            rec_acc = metrics.get("recommendation_accuracy", 0.0)
            grounding_acc = metrics.get("grounding_accuracy", 0.0)
            hallucination_rate = metrics.get("hallucination_rate", 0.0)
            
            avg_consistency = 0.0
            if consistency_list:
                avg_consistency = sum(cr.get("consistency_pct", 0.0) for cr in consistency_list) / len(consistency_list)
                
            avg_latency = latency.get("total_avg", 0.0)
            
            # Compute sub-scores for ranking (all normalized between 0.0 and 1.0)
            acc_score = rec_acc
            grounding_score = grounding_acc
            
            # Hallucination subscore (lower is better, so 1.0 - rate)
            hallucination_score = max(0.0, min(1.0, 1.0 - hallucination_rate))
            
            # Consistency subscore
            consistency_score = avg_consistency / 100.0
            
            # Latency subscore (lower is better, 1.0 when latency is 0ms, 0.0 when latency >= 15000ms)
            latency_score = max(0.0, min(1.0, 1.0 - (avg_latency / 15000.0)))
            
            # Weighted Overall Score:
            # 40% Recommendation Accuracy
            # 25% Grounding Gate Accuracy
            # 15% Hallucination Rate
            # 10% Consistency Score
            # 10% Latency
            overall_score = (
                (acc_score * 0.40) +
                (grounding_score * 0.25) +
                (hallucination_score * 0.15) +
                (consistency_score * 0.10) +
                (latency_score * 0.10)
            )
            
            models_data.append({
                "model_name": model_name,
                "overall_score": round(overall_score * 100, 1),
                "recommendation_accuracy": rec_acc,
                "grounding_accuracy": grounding_acc,
                "hallucination_rate": hallucination_rate,
                "consistency_score": avg_consistency,
                "avg_latency_ms": avg_latency,
                "p95_latency_ms": latency.get("total_p95", 0.0),
                "scores": {
                    "accuracy": round(acc_score, 3),
                    "grounding": round(grounding_score, 3),
                    "hallucination": round(hallucination_score, 3),
                    "consistency": round(consistency_score, 3),
                    "latency": round(latency_score, 3)
                }
            })
            
        except Exception as e:
            print(f"Error parsing baseline file {filepath}: {e}")
            
    if not models_data:
        print("Error: No valid model data parsed from baselines.")
        return
        
    # Rank models by overall score descending
    ranked_models = sorted(models_data, key=lambda x: x["overall_score"], reverse=True)
    
    # Determine best models
    best_overall = ranked_models[0]["model_name"]
    
    # Best fast model (latency < 5000ms)
    fast_models = [m for m in ranked_models if m["avg_latency_ms"] < 5000]
    best_fast = fast_models[0]["model_name"] if fast_models else "None (< 5s)"
    
    # Best accuracy model (highest recommendation accuracy)
    best_accuracy = max(ranked_models, key=lambda x: x["recommendation_accuracy"])["model_name"]
    
    rankings_output = {
        "best_overall": best_overall,
        "best_fast_model": best_fast,
        "best_accuracy_model": best_accuracy,
        "rankings": ranked_models
    }
    
    # Save Rankings to JSON
    with open(RANKING_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rankings_output, f, indent=2)
    print(f"Saved rankings JSON to: {RANKING_JSON_PATH}")
    
    # Generate Markdown Report
    generate_markdown_report(rankings_output)

def generate_markdown_report(rankings_output: Dict[str, Any]):
    rankings = rankings_output["rankings"]
    
    rows = []
    for idx, r in enumerate(rankings):
        rows.append(
            f"| {idx+1} | **{r['model_name']}** | {r['overall_score']}% | {r['recommendation_accuracy']:.1%} | {r['grounding_accuracy']:.1%} | {r['hallucination_rate']:.1%} | {r['consistency_score']:.1f}% | {r['avg_latency_ms']/1000:.2f}s ({r['p95_latency_ms']/1000:.2f}s) |"
        )
        
    table_rows = "\n".join(rows)
    
    markdown_content = f"""# Stock Agent Model Benchmarking Report

This report summarizes the comparative evaluations of multiple local LLM models against the golden evaluation dataset (60 Cases), ranking their overall suitability for the autonomous recommendation agent.

---

## 🏆 Model Leaderboard Rankings

| Rank | Model Name | Overall Score | Rec Accuracy | Grounding Accuracy | Hallucination Rate | Consistency | Avg (P95) Latency |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
{table_rows}

---

## 📊 Optimal Deployment Decisions

* **🏆 Best Overall Model:** `{rankings_output["best_overall"]}`
  * *Rationale:* Selected based on the weighted formula prioritizing high recommendation accuracy, low hallucination risk, and stable decision consistency.
* **⚡ Best Fast Model (< 5s):** `{rankings_output["best_fast_model"]}`
  * *Rationale:* Offers the highest quality tradeoff while maintaining latency bounds for real-time customer interactive requests.
* **🎯 Best Accuracy Model:** `{rankings_output["best_accuracy_model"]}`
  * *Rationale:* Maximizes investment recommendation alignment with historical market event outcomes.

---

## 🔬 Benchmark Methodology & Weights

The overall score is calculated as a weighted average of normalized metric scores:
* **40% Recommendation Accuracy:** Agreement rate with historical market outcomes.
* **25% Grounding Gate Accuracy:** Correctly allowing grounded queries and refusing ungrounded queries.
* **15% Hallucination Rate:** Frequency of hallucinated citations or stock symbols.
* **10% Consistency Score:** Decision consistency when repeating identical queries 10 times.
* **10% Latency Score:** Speed penalty for execution latency (linearly penalized up to 15s).
"""
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Generated benchmark report at: {REPORT_PATH}")

if __name__ == "__main__":
    compile_rankings()
