import { mockSuggestResponse, mockSystemStatus } from "@/features/analysis/mock-data";
import { env } from "@/lib/env";
import { apiClient } from "@/services/api-client";
import type {
  SuggestRequest,
  SuggestResponse,
  SuggestResponseApi,
  SystemStatus,
} from "@/types/stock";

function normalizeSuggestResponse(payload: SuggestResponseApi): SuggestResponse {
  return {
    suggestions: payload.suggestions.map((suggestion) => ({
      symbol: suggestion.symbol.toUpperCase(),
      score: suggestion.score,
      decision: suggestion.decision,
      reason: suggestion.reason,
    })),
  };
}

export async function suggestStocks(request: SuggestRequest): Promise<SuggestResponse> {
  if (env.enableMocks) {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return mockSuggestResponse;
  }

  const payload = await apiClient<SuggestResponseApi>("/suggest", {
    method: "POST",
    body: {
      symbols: request.symbols,
      lookback_days: request.lookbackDays,
    },
  });

  return normalizeSuggestResponse(payload);
}

export async function getSystemStatus(): Promise<SystemStatus> {
  if (env.enableMocks) {
    return mockSystemStatus;
  }

  try {
    await apiClient<Record<string, unknown>>("/openapi.json");

    return {
      level: "healthy",
      summary: "The frontend reached the FastAPI OpenAPI document successfully.",
      details:
        "This is a temporary probe. Replace it with a dedicated health endpoint once the backend exposes one.",
    };
  } catch (error) {
    return {
      level: "degraded",
      summary: "The frontend could not verify backend reachability through /openapi.json.",
      details:
        error instanceof Error
          ? error.message
          : "The status probe returned an unknown error.",
    };
  }
}
