# StockAgent

**Status:** Implemented, with agentic extensions planned

## Responsibility
`StockAgent` is the application-level orchestrator. It coordinates data collection, validation, market signals, news indexing, retrieval, grounding and LLM reasoning.

## Current flow
```text
request
  -> fetch market/news data
  -> validate/normalize
  -> index news when required
  -> generate market signals
  -> retrieve supporting evidence
  -> rerank
  -> grounding decision
      -> insufficient evidence: refuse/return guarded result
      -> sufficient evidence: build context
  -> prompt + LLM reasoning
  -> score/rank final result
```

## Why it exists
It keeps the API thin and gives the application one place to enforce the order and failure semantics of the analysis pipeline.

## Planned evolution
Replace increasingly complex branching with an explicit state graph. Agent state will carry `trace_id`, evidence, tool permissions, tool results, model output and final structured answer.
