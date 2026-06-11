import type { AnalysisPhase, SuggestRequest, SuggestResponse } from "@/types/stock";

export type AnalysisOutcome = {
  phase: Exclude<AnalysisPhase, "idle" | "loading" | "failure">;
  message?: string;
};

export function resolveAnalysisOutcome(
  request: SuggestRequest,
  response: SuggestResponse,
): AnalysisOutcome {
  const missingSymbols = request.symbols.filter(
    (symbol) => !response.suggestions.some((suggestion) => suggestion.symbol === symbol),
  );

  if (response.suggestions.length === 0) {
    return { phase: "no-data" };
  }

  if (missingSymbols.length > 0) {
    return {
      phase: "partial-failure",
      message: `Missing results for ${missingSymbols.join(", ")}.`,
    };
  }

  return { phase: "success" };
}
