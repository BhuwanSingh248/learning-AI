export type SuggestionDecision = string;

export type SuggestRequest = {
  symbols: string[];
  lookbackDays: number;
};

export type SignalBreakdown = {
  trend?: string;
  momentum?: number;
  volatility?: number;
  sentiment?: number;
  eventScore?: number;
};

export type RagContextItem = {
  title: string;
  summary?: string;
  source?: string;
  timestamp?: string;
  relevanceScore?: number;
};

export type RagInsights = {
  enabled: boolean;
  retrievalStrategy?: string;
  topK?: number;
  embeddingModel?: string;
  vectorDimension?: number;
  indexType?: string;
  promptMode?: string;
  fallbackUsed?: boolean;
  contextPreview?: string;
  contextItems?: RagContextItem[];
};

export type PredictionMeta = {
  horizon?: string;
  rankBucket?: string;
  confidence?: number;
  expectedDirection?: string;
};

export type SuggestionItem = {
  symbol: string;
  score: number;
  decision: SuggestionDecision;
  reason: string;
  signalBreakdown?: SignalBreakdown;
  rag?: RagInsights;
  prediction?: PredictionMeta;
};

export type SuggestResponse = {
  suggestions: SuggestionItem[];
};

export type SuggestResponseApi = {
  suggestions: Array<{
    symbol: string;
    score: number;
    decision: string;
    reason: string;
    signal_breakdown?: {
      trend?: string;
      momentum?: number;
      volatility?: number;
      sentiment?: number;
      sentiment_score?: number;
      event_score?: number;
    };
    signals?: {
      trend?: string;
      momentum?: number;
      volatility?: number;
      sentiment?: number;
      sentiment_score?: number;
      event_score?: number;
    };
    rag?: {
      enabled?: boolean;
      retrieval_strategy?: string;
      top_k?: number;
      embedding_model?: string;
      vector_dimension?: number;
      index_type?: string;
      prompt_mode?: string;
      fallback_used?: boolean;
      context_preview?: string;
      context_items?: Array<{
        title?: string;
        summary?: string;
        source?: string;
        timestamp?: string;
        relevance_score?: number;
      }>;
    };
    retrieval?: {
      enabled?: boolean;
      retrieval_strategy?: string;
      top_k?: number;
      embedding_model?: string;
      vector_dimension?: number;
      index_type?: string;
      prompt_mode?: string;
      fallback_used?: boolean;
      context_preview?: string;
      context_items?: Array<{
        title?: string;
        summary?: string;
        source?: string;
        timestamp?: string;
        relevance_score?: number;
      }>;
    };
    prediction?: {
      horizon?: string;
      rank_bucket?: string;
      confidence?: number;
      expected_direction?: string;
    };
  }>;
};

export type AnalysisPhase =
  | "idle"
  | "loading"
  | "success"
  | "partial-failure"
  | "failure"
  | "no-data";

export type SystemStatusLevel = "healthy" | "degraded" | "unavailable";
export type SystemSubsystemLevel = SystemStatusLevel | "planned";

export type SystemSubsystemStatus = {
  key: string;
  label: string;
  level: SystemSubsystemLevel;
  summary: string;
  details?: string;
  metrics?: Array<{
    label: string;
    value: string;
  }>;
};

export type SystemStatus = {
  level: SystemStatusLevel;
  summary: string;
  details: string;
  probeTarget?: string;
  subsystems?: SystemSubsystemStatus[];
};
