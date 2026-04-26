import { mockSuggestResponse, mockSystemStatus } from "@/features/analysis/mock-data";
import { env } from "@/lib/env";
import { apiClient } from "@/services/api-client";
import type {
  PredictionMeta,
  RagInsights,
  SignalBreakdown,
  SuggestRequest,
  SuggestResponse,
  SuggestResponseApi,
  SystemStatus,
  SystemStatusLevel,
  SystemSubsystemLevel,
  SystemSubsystemStatus,
} from "@/types/stock";

type HealthCheckApi = {
  label?: string;
  level?: string;
  status?: string;
  summary?: string;
  details?: string;
  model?: string;
  embedding_model?: string;
  top_k?: number;
  vector_dimension?: number;
  index_type?: string;
  retrieval_strategy?: string;
  prompt_mode?: string;
};

type HealthResponseApi = {
  level?: string;
  status?: string;
  summary?: string;
  details?: string;
  probe_target?: string;
  checks?: Record<string, HealthCheckApi>;
};

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function normalizeSignalBreakdown(
  payload?: SuggestResponseApi["suggestions"][number]["signal_breakdown"],
): SignalBreakdown | undefined {
  if (!payload) {
    return undefined;
  }

  const sentiment = isFiniteNumber(payload.sentiment)
    ? payload.sentiment
    : isFiniteNumber(payload.sentiment_score)
      ? payload.sentiment_score
      : undefined;
  const eventScore = isFiniteNumber(payload.event_score) ? payload.event_score : undefined;

  const normalized: SignalBreakdown = {};

  if (payload.trend?.trim()) {
    normalized.trend = payload.trend;
  }

  if (isFiniteNumber(payload.momentum)) {
    normalized.momentum = payload.momentum;
  }

  if (isFiniteNumber(payload.volatility)) {
    normalized.volatility = payload.volatility;
  }

  if (isFiniteNumber(sentiment)) {
    normalized.sentiment = sentiment;
  }

  if (isFiniteNumber(eventScore)) {
    normalized.eventScore = eventScore;
  }

  return Object.keys(normalized).length > 0 ? normalized : undefined;
}

function normalizeRagInsights(
  payload?: SuggestResponseApi["suggestions"][number]["rag"],
): RagInsights | undefined {
  if (!payload) {
    return undefined;
  }

  const contextItems = payload.context_items
    ?.map((item, index) => {
      const title = item.title?.trim() || `Context item ${index + 1}`;

      return {
        title,
        summary: item.summary?.trim() || undefined,
        source: item.source?.trim() || undefined,
        timestamp: item.timestamp,
        relevanceScore: isFiniteNumber(item.relevance_score) ? item.relevance_score : undefined,
      };
    })
    .filter(Boolean);

  const normalized: RagInsights = {
    enabled: payload.enabled ?? Boolean(contextItems?.length || payload.context_preview),
  };

  if (payload.retrieval_strategy?.trim()) {
    normalized.retrievalStrategy = payload.retrieval_strategy;
  }

  if (isFiniteNumber(payload.top_k)) {
    normalized.topK = payload.top_k;
  }

  if (payload.embedding_model?.trim()) {
    normalized.embeddingModel = payload.embedding_model;
  }

  if (isFiniteNumber(payload.vector_dimension)) {
    normalized.vectorDimension = payload.vector_dimension;
  }

  if (payload.index_type?.trim()) {
    normalized.indexType = payload.index_type;
  }

  if (payload.prompt_mode?.trim()) {
    normalized.promptMode = payload.prompt_mode;
  }

  if (typeof payload.fallback_used === "boolean") {
    normalized.fallbackUsed = payload.fallback_used;
  }

  if (payload.context_preview?.trim()) {
    normalized.contextPreview = payload.context_preview;
  }

  if (contextItems && contextItems.length > 0) {
    normalized.contextItems = contextItems;
  }

  return normalized;
}

function normalizePredictionMeta(
  payload?: SuggestResponseApi["suggestions"][number]["prediction"],
): PredictionMeta | undefined {
  if (!payload) {
    return undefined;
  }

  const normalized: PredictionMeta = {};

  if (payload.horizon?.trim()) {
    normalized.horizon = payload.horizon;
  }

  if (payload.rank_bucket?.trim()) {
    normalized.rankBucket = payload.rank_bucket;
  }

  if (isFiniteNumber(payload.confidence)) {
    normalized.confidence = payload.confidence;
  }

  if (payload.expected_direction?.trim()) {
    normalized.expectedDirection = payload.expected_direction;
  }

  return Object.keys(normalized).length > 0 ? normalized : undefined;
}

export function normalizeSuggestResponse(payload: SuggestResponseApi): SuggestResponse {
  return {
    suggestions: payload.suggestions.map((suggestion) => ({
      symbol: suggestion.symbol.toUpperCase(),
      score: suggestion.score,
      decision: suggestion.decision,
      reason: suggestion.reason,
      signalBreakdown: normalizeSignalBreakdown(
        suggestion.signal_breakdown ?? suggestion.signals,
      ),
      rag: normalizeRagInsights(suggestion.rag ?? suggestion.retrieval),
      prediction: normalizePredictionMeta(suggestion.prediction),
    })),
  };
}

function formatSubsystemLabel(key: string) {
  return key
    .split(/[_-]+/)
    .filter(Boolean)
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(" ");
}

function toSystemLevel(value?: string): SystemStatusLevel {
  switch (value?.toLowerCase()) {
    case "healthy":
    case "ok":
    case "up":
      return "healthy";
    case "unavailable":
    case "down":
    case "error":
      return "unavailable";
    default:
      return "degraded";
  }
}

function toSubsystemLevel(value?: string): SystemSubsystemLevel {
  switch (value?.toLowerCase()) {
    case "healthy":
    case "ok":
    case "up":
      return "healthy";
    case "degraded":
    case "warning":
      return "degraded";
    case "unavailable":
    case "down":
    case "error":
      return "unavailable";
    default:
      return "planned";
  }
}

function toSubsystemMetrics(check: HealthCheckApi) {
  const metrics: Array<{ label: string; value: string }> = [];

  const metricMap = [
    ["Model", check.model ?? check.embedding_model],
    ["Top-K", isFiniteNumber(check.top_k) ? String(check.top_k) : undefined],
    [
      "Vector dimension",
      isFiniteNumber(check.vector_dimension) ? String(check.vector_dimension) : undefined,
    ],
    ["Index type", check.index_type],
    ["Retrieval", check.retrieval_strategy],
    ["Prompt mode", check.prompt_mode],
  ] as const;

  for (const [label, value] of metricMap) {
    if (value) {
      metrics.push({ label, value });
    }
  }

  return metrics;
}

function createPlannedSubsystems(probeTarget: string, apiLevel: SystemSubsystemLevel) {
  const apiSummary =
    apiLevel === "healthy"
      ? `Reachability was confirmed through ${probeTarget}.`
      : `The frontend could not verify the backend through ${probeTarget}.`;

  return [
    {
      key: "api",
      label: "API",
      level: apiLevel,
      summary: apiSummary,
      details: "Replace the probe with a dedicated health contract when available.",
    },
    {
      key: "embedding_layer",
      label: "Embedding Layer",
      level: "planned" as const,
      summary: "Waiting for backend health data for the all-MiniLM-L6-v2 embedding stage.",
      details: "This panel is ready to surface model, dimension, and readiness metrics.",
    },
    {
      key: "vector_index",
      label: "FAISS Index",
      level: "planned" as const,
      summary: "Waiting for vector index status, dimension, and retrieval configuration.",
      details: "Task 7.3 can report index type, save/load state, and Top-K defaults here.",
    },
    {
      key: "retrieval_pipeline",
      label: "Retrieval Pipeline",
      level: "planned" as const,
      summary: "Waiting for query-to-context pipeline health and fallback signals.",
      details: "Task 7.4 can expose retrieval readiness and no-result fallback behavior here.",
    },
    {
      key: "reasoning",
      label: "Context-Aware Reasoning",
      level: "planned" as const,
      summary: "Waiting for status showing whether prompts use both signals and retrieved context.",
      details: "Task 7.5 can surface prompt mode and signals-vs-context behavior here.",
    },
  ] satisfies SystemSubsystemStatus[];
}

export function normalizeHealthResponse(payload: HealthResponseApi): SystemStatus {
  const level = toSystemLevel(payload.level ?? payload.status);
  const subsystems = payload.checks
    ? Object.entries(payload.checks).map(([key, check]) => ({
        key,
        label: check.label ?? formatSubsystemLabel(key),
        level: toSubsystemLevel(check.level ?? check.status),
        summary: check.summary ?? `${formatSubsystemLabel(key)} reported no summary.`,
        details: check.details,
        metrics: toSubsystemMetrics(check),
      }))
    : undefined;

  return {
    level,
    summary: payload.summary ?? "The backend returned health data.",
    details: payload.details ?? "Dedicated health information is available for the UI.",
    probeTarget: payload.probe_target ?? "/health",
    subsystems,
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
    const payload = await apiClient<HealthResponseApi>("/health");
    return normalizeHealthResponse(payload);
  } catch {
    try {
      await apiClient<Record<string, unknown>>("/openapi.json");

      return {
        level: "healthy",
        summary: "The frontend reached the backend successfully, but only through the OpenAPI fallback probe.",
        details:
          "A dedicated /health endpoint was not available, so the UI is showing planned RAG subsystem slots instead of live Phase 7 telemetry.",
        probeTarget: "/openapi.json",
        subsystems: createPlannedSubsystems("/openapi.json", "healthy"),
      };
    } catch (error) {
      return {
        level: "unavailable",
        summary: "The frontend could not verify backend reachability through either /health or /openapi.json.",
        details:
          error instanceof Error
            ? error.message
            : "The status probe returned an unknown error.",
        probeTarget: "/health",
        subsystems: createPlannedSubsystems("/health", "unavailable"),
      };
    }
  }
}
