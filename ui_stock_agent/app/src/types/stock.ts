export type SuggestionDecision = string;

export type SuggestRequest = {
  symbols: string[];
  lookbackDays: number;
};

export type SuggestionItem = {
  symbol: string;
  score: number;
  decision: SuggestionDecision;
  reason: string;
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
  }>;
};

export type AnalysisPhase =
  | "idle"
  | "loading"
  | "success"
  | "partial-failure"
  | "failure"
  | "no-data";

export type SystemStatus = {
  level: "healthy" | "degraded" | "unavailable";
  summary: string;
  details: string;
};
