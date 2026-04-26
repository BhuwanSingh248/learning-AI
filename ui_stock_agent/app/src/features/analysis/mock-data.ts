import type { SuggestResponse, SystemStatus } from "@/types/stock";

export const mockSuggestResponse: SuggestResponse = {
  suggestions: [
    {
      symbol: "NVDA",
      score: 9.14,
      decision: "Bullish",
      reason:
        "Momentum remains strong and retrieved context highlights earnings strength, AI demand, and supportive analyst coverage.",
      signalBreakdown: {
        trend: "bullish",
        momentum: 0.88,
        volatility: 0.24,
        sentiment: 0.74,
        eventScore: 0.52,
      },
      rag: {
        enabled: true,
        retrievalStrategy: "similarity search",
        topK: 5,
        embeddingModel: "all-MiniLM-L6-v2",
        vectorDimension: 384,
        indexType: "flat-l2",
        promptMode: "signals+context",
        contextPreview:
          "Recent News: Nvidia posted stronger-than-expected data-center growth while analyst notes stayed constructive on AI demand.",
        contextItems: [
          {
            title: "Nvidia beats expectations on data-center revenue",
            summary: "Revenue growth and guidance both exceeded consensus estimates.",
            source: "Reuters",
            timestamp: "2026-04-12T08:15:00Z",
            relevanceScore: 0.98,
          },
          {
            title: "Analysts raise targets after AI demand stays elevated",
            summary: "Sell-side coverage remains positive as chip demand stays tight.",
            source: "Bloomberg",
            timestamp: "2026-04-11T14:30:00Z",
            relevanceScore: 0.93,
          },
        ],
      },
      prediction: {
        horizon: "short_term",
        rankBucket: "top_candidate",
        confidence: 0.89,
        expectedDirection: "bullish",
      },
    },
    {
      symbol: "MSFT",
      score: 8.42,
      decision: "Bullish",
      reason:
        "Stable strength profile remains intact, and retrieved context suggests cloud and enterprise demand are still supporting the trend.",
      signalBreakdown: {
        trend: "bullish",
        momentum: 0.63,
        volatility: 0.18,
        sentiment: 0.57,
        eventScore: 0.38,
      },
      rag: {
        enabled: true,
        retrievalStrategy: "similarity search",
        topK: 5,
        embeddingModel: "all-MiniLM-L6-v2",
        vectorDimension: 384,
        indexType: "flat-l2",
        promptMode: "signals+context",
        contextPreview:
          "Recent News: Microsoft cloud demand remains firm and recent enterprise updates continue to support the bullish case.",
        contextItems: [
          {
            title: "Azure demand remains resilient in enterprise refresh cycle",
            summary: "Cloud growth stays constructive despite mixed macro signals.",
            source: "The Wall Street Journal",
            timestamp: "2026-04-11T11:05:00Z",
            relevanceScore: 0.91,
          },
        ],
      },
      prediction: {
        horizon: "short_term",
        rankBucket: "top_candidate",
        confidence: 0.78,
        expectedDirection: "bullish",
      },
    },
    {
      symbol: "AAPL",
      score: 6.88,
      decision: "Neutral",
      reason:
        "Signals are constructive but mixed enough that conviction is lower than the leaders, and the retrieved context does not add enough fresh support to push the decision bullish.",
      signalBreakdown: {
        trend: "neutral",
        momentum: 0.29,
        volatility: 0.17,
        sentiment: 0.18,
        eventScore: 0.14,
      },
      rag: {
        enabled: true,
        retrievalStrategy: "similarity search",
        topK: 5,
        embeddingModel: "all-MiniLM-L6-v2",
        vectorDimension: 384,
        indexType: "flat-l2",
        promptMode: "signals+context",
        fallbackUsed: true,
        contextPreview:
          "Recent News: Coverage is mixed, with incremental product optimism offset by softer demand commentary.",
        contextItems: [
          {
            title: "Supply-chain checks show mixed iPhone demand signals",
            summary: "Some checks improved, but regional demand remains uneven.",
            source: "CNBC",
            timestamp: "2026-04-10T16:20:00Z",
            relevanceScore: 0.79,
          },
        ],
      },
      prediction: {
        horizon: "short_term",
        rankBucket: "neutral",
        confidence: 0.51,
        expectedDirection: "neutral",
      },
    },
  ],
};

export const mockSystemStatus: SystemStatus = {
  level: "healthy",
  summary: "Mock mode is enabled, so the frontend is simulating full Phase 7 telemetry without probing the live API.",
  details:
    "This is useful while the backend is offline or while front-end flows are being developed in parallel.",
  probeTarget: "mock://phase-7",
  subsystems: [
    {
      key: "api",
      label: "API",
      level: "healthy",
      summary: "Mock transport is responding with the current suggest contract plus optional Phase 7 fields.",
      metrics: [{ label: "Probe target", value: "mock://phase-7" }],
    },
    {
      key: "embedding_layer",
      label: "Embedding Layer",
      level: "healthy",
      summary: "The mock app is simulating all-MiniLM-L6-v2 embedding readiness.",
      metrics: [
        { label: "Model", value: "all-MiniLM-L6-v2" },
        { label: "Vector dimension", value: "384" },
      ],
    },
    {
      key: "vector_index",
      label: "FAISS Index",
      level: "healthy",
      summary: "Vector index metadata is available for the UI and using a flat L2 strategy.",
      metrics: [
        { label: "Index type", value: "flat-l2" },
        { label: "Top-K", value: "5" },
      ],
    },
    {
      key: "retrieval_pipeline",
      label: "Retrieval Pipeline",
      level: "healthy",
      summary: "Retrieved news is being formatted into concise context previews for the detail screen.",
      metrics: [{ label: "Retrieval", value: "similarity search" }],
    },
    {
      key: "reasoning",
      label: "Context-Aware Reasoning",
      level: "degraded",
      summary: "Signals remain primary and the system will fall back gracefully when context is weak or mixed.",
      metrics: [{ label: "Prompt mode", value: "signals+context" }],
      details:
        "The neutral Apple example demonstrates how the UI should represent fallback and uncertainty when signals and context do not align strongly.",
    },
  ],
};
