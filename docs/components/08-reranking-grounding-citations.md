# Reranking, Grounding and Citations

**Status:** Implemented

## Reranker
A CrossEncoder reranks retrieved query/document candidates using joint query-document scoring. This is more expensive than first-stage retrieval, so it should operate on a bounded candidate set.

## Grounding
`GroundingService` checks whether retrieved evidence is strong enough to support an answer. It is a safety boundary, not a confidence score that makes unsupported facts true.

```text
retrieved candidates
  -> CrossEncoder
  -> top evidence
  -> GroundingService
      ├── insufficient -> guarded refusal/uncertain result
      └── sufficient -> context construction
```

## Citations
The context builder preserves source/chunk identity so the generated answer can point back to supporting evidence.

## Non-negotiable invariant
The system must not present an unsupported LLM answer as grounded simply because the model generated it confidently.

## Planned hardening
- Citation precision/recall evaluation.
- Contradictory-evidence tests.
- Prompt-injection/poisoned-document tests.
- Trace ID linking from evidence to final answer.
