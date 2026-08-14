# Market Analysis

**Status:** Implemented

## Responsibility
Transform normalized market, news and event data into independent signals used by the recommendation pipeline.

## Typical signals
- Price/trend behavior.
- News/event signals.
- Corporate-action context.
- Confidence/quality metadata.

## Flow
```text
normalized data
   -> MarketAnalyzer
      -> price signals
      -> news signals
      -> event signals
      -> combined analysis
```

## Boundary
Market signals are evidence/features. They are not permission to bypass RAG grounding or to manufacture an LLM explanation.

## Planned evolution
- Historical backtesting.
- Leakage-safe feature windows.
- Domain sentiment such as FinBERT as an independently evaluated signal.
