# Data Providers

**Status:** Implemented

## Components
- `DataService`: application-facing abstraction.
- Provider interface: common contract for external data sources.
- Composite provider: combines available market/news providers.
- OpenBB: market and financial data.
- News providers: external news ingestion sources.

## Flow
```text
DataService
   -> provider interface
      -> OpenBB / news provider(s)
   -> normalized domain data
```

## Design rule
Provider-specific SDKs and response formats must stay behind the provider boundary. `StockAgent` should consume normalized domain data rather than know which provider supplied it.

## Failure behavior
A provider failure should be classified as transient/permanent and should not silently produce fabricated market data. Partial-source behavior must be explicit.

## Planned evolution
- Retry/backoff and circuit breaking.
- Provider response caching.
- Provider freshness metadata.
- Background ingestion through Celery.
- Trace spans for every provider call.
