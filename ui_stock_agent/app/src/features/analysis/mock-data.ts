import type { SuggestResponse, SystemStatus } from "@/types/stock";

export const mockSuggestResponse: SuggestResponse = {
  suggestions: [
    {
      symbol: "NVDA",
      score: 9.14,
      decision: "Bullish",
      reason:
        "Momentum remains strong and recent market narrative is supportive of continued upside.",
    },
    {
      symbol: "MSFT",
      score: 8.42,
      decision: "Bullish",
      reason:
        "Stable strength profile with broad-based resilience across the recent lookback window.",
    },
    {
      symbol: "AAPL",
      score: 6.88,
      decision: "Neutral",
      reason:
        "Signals are constructive but mixed enough that conviction is lower than the leaders.",
    },
  ],
};

export const mockSystemStatus: SystemStatus = {
  level: "healthy",
  summary: "Mock mode is enabled, so the frontend is using local fixtures instead of probing the API.",
  details:
    "This is useful while the backend is offline or while front-end flows are being developed in parallel.",
};
