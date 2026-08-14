# learning-AI Component Documentation

This directory documents the backend components of `learning-AI`, what each component owns, how data moves through it, and whether the capability is **implemented today** or **planned**.

## Request and analysis
- [API Layer](./01-api-layer.md)
- [Stock Agent](./02-stock-agent.md)
- [Data Providers](./03-data-providers.md)
- [Market Analysis](./04-market-analysis.md)

## RAG pipeline
- [Ingestion, Chunking and Embeddings](./05-ingestion-chunking-embeddings.md)
- [PostgreSQL and FAISS](./06-storage-and-indexing.md)
- [Hybrid Retrieval](./07-hybrid-retrieval.md)
- [Reranking, Grounding and Citations](./08-reranking-grounding-citations.md)

## LLM and agent evolution
- [Prompting and LLM Reasoning](./09-llm-reasoning.md)
- [Agentic Components](./10-agentic-components.md)

## Quality and operations
- [Evaluation and Observability](./11-evaluation-observability.md)
- [Caching, Background Jobs and Infrastructure](./12-infrastructure.md)

## End-to-end flow

```text
Client
  -> FastAPI
  -> StockAgent
      -> DataService -> Providers
      -> DataValidator
      -> MarketAnalyzer
      -> NewsIndexer -> Chunker -> Embeddings -> PostgreSQL + FAISS
      -> HybridRetriever -> BM25 + FAISS
      -> CrossEncoder Reranker
      -> GroundingService
      -> Citation Context Builder
      -> Prompt Builder -> LLM Client -> Reasoning Engine
  -> Ranked / structured response

Future agent path:
StockAgent -> State Graph -> Tools -> Memory -> LLM -> Grounding -> Answer

Cross-cutting:
trace_id -> retrieval -> tools -> model -> final answer
Golden tasks -> quality/security gates -> CI
```

> **Status rule:** diagrams and descriptions distinguish implemented components from roadmap components. A planned component is not presented as production functionality.
