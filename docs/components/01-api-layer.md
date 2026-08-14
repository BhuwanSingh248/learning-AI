# API Layer

**Status:** Implemented

## Responsibility
Expose the application contract to clients and translate HTTP requests into application-level commands.

## Main responsibilities
- FastAPI application startup and dependency wiring.
- Request validation through typed request models.
- `/suggest` for ranked stock suggestions.
- `/analyze` for stock analysis.
- Health/debug endpoints for service diagnostics.
- Exception handling and response serialization.

## Flow
```text
HTTP request
  -> request model
  -> dependency injection
  -> StockAgent
  -> response DTO
  -> HTTP response
```

## Boundary rule
The API should not contain retrieval algorithms, prompt construction, provider-specific logic, or model reasoning. Those belong to application/domain components.

## Planned evolution
- Stable versioned API contracts.
- Request authentication and rate limits.
- Streaming analysis endpoint.
- Trace ID propagation to every downstream component.
