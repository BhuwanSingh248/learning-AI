# Caching, Background Jobs and Infrastructure

**Status:** Roadmap

## Redis
Use Redis for cache-aside patterns, embedding/retrieval caching, rate limits and coordination where required. Cache keys must include the relevant model/index/config version and must not mix users or symbols.

## Celery
Move news ingestion and expensive indexing work out of request handling:

```text
scheduler
  -> Celery task
  -> fetch
  -> normalize/dedupe
  -> chunk
  -> batch embed
  -> persist
  -> build/activate index
```

Retries must be bounded, idempotent and observable. Exhausted failures go to a dead-letter workflow.

## Docker
Containerize API, workers, PostgreSQL, Redis and local model-serving dependencies for reproducible development.

## AWS
Production deployment separates API, workers, data stores, object/index artifacts and model serving. Secrets use a managed secret store and workloads use least-privilege IAM.

## CI/CD
CI runs tests and AI quality/security gates, builds a versioned image and promotes the same artifact through environments rather than rebuilding for deployment.
