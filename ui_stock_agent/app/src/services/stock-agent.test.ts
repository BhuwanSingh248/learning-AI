import { describe, expect, it } from "vitest";
import { normalizeHealthResponse, normalizeSuggestResponse } from "@/services/stock-agent";

describe("normalizeSuggestResponse", () => {
  it("maps optional phase 7 signal and rag payloads into the UI shape", () => {
    const response = normalizeSuggestResponse({
      suggestions: [
        {
          symbol: "aapl",
          score: 0.82,
          decision: "Bullish",
          reason: "Signals are strong and retrieved context supports the upside case.",
          signal_breakdown: {
            trend: "bullish",
            momentum: 0.72,
            volatility: 0.21,
            sentiment_score: 0.61,
            event_score: 0.44,
          },
          rag: {
            enabled: true,
            retrieval_strategy: "similarity search",
            top_k: 5,
            embedding_model: "all-MiniLM-L6-v2",
            vector_dimension: 384,
            index_type: "flat-l2",
            prompt_mode: "signals+context",
            fallback_used: false,
            context_preview: "Recent News: Apple reports strong earnings growth...",
            context_items: [
              {
                title: "Apple reports strong earnings growth",
                summary: "Revenue beats expectations.",
                source: "Reuters",
                relevance_score: 0.98,
              },
            ],
          },
        },
      ],
    });

    expect(response.suggestions[0]).toMatchObject({
      symbol: "AAPL",
      signalBreakdown: {
        trend: "bullish",
        momentum: 0.72,
        volatility: 0.21,
        sentiment: 0.61,
        eventScore: 0.44,
      },
      rag: {
        enabled: true,
        topK: 5,
        embeddingModel: "all-MiniLM-L6-v2",
        vectorDimension: 384,
        indexType: "flat-l2",
        promptMode: "signals+context",
      },
    });
  });
});

describe("normalizeHealthResponse", () => {
  it("normalizes check metrics for the status panel", () => {
    const status = normalizeHealthResponse({
      status: "healthy",
      summary: "Dedicated health endpoint is available.",
      details: "All phase 7 subsystems are reporting live metrics.",
      probe_target: "/health",
      checks: {
        embedding_layer: {
          status: "healthy",
          summary: "Embedding model is loaded.",
          model: "all-MiniLM-L6-v2",
          vector_dimension: 384,
        },
        retrieval_pipeline: {
          status: "degraded",
          summary: "Retrieval fallback was used for some requests.",
          top_k: 5,
          retrieval_strategy: "similarity search",
        },
      },
    });

    expect(status.level).toBe("healthy");
    expect(status.probeTarget).toBe("/health");
    expect(status.subsystems).toHaveLength(2);
    expect(status.subsystems?.[0]).toMatchObject({
      key: "embedding_layer",
      label: "Embedding Layer",
      level: "healthy",
    });
    expect(status.subsystems?.[1]?.metrics).toEqual(
      expect.arrayContaining([
        { label: "Top-K", value: "5" },
        { label: "Retrieval", value: "similarity search" },
      ]),
    );
  });
});
