# Evaluation and Observability

**Status:** Roadmap with existing hooks/metrics

## Golden evaluation
The golden-task suite measures retrieval, grounding, citation correctness, refusal behavior, prompt-injection resistance, tool permission boundaries and structured output validity.

## Trace model
Every run receives:

`trace_id -> retrieval -> reranker -> grounding -> tools -> model -> final answer`

The trace must also record safe model/index/prompt versions and latency/token metadata.

## Metrics
- Recall@K, MRR, nDCG.
- Citation precision/recall.
- Grounded-answer and unsupported-claim rates.
- Safe-refusal and permission-denial correctness.
- Schema validity.
- Latency and token/cost measurements.

## CI
A deterministic smoke subset runs on pull requests. A larger real-model suite can run on main/nightly. Security assertions remain deterministic and are never delegated solely to an LLM judge.

## Observability target
OpenTelemetry-compatible spans allow export to a tracing backend without coupling domain logic to one vendor.
