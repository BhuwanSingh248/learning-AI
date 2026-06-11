import { describe, expect, it } from "vitest";
import { resolveAnalysisOutcome } from "@/features/analysis/analysis-outcome";
import type { SuggestRequest, SuggestResponse } from "@/types/stock";

const request: SuggestRequest = {
  symbols: ["AAPL", "MSFT"],
  lookbackDays: 90,
};

function responseWithSymbols(symbols: string[]): SuggestResponse {
  return {
    suggestions: symbols.map((symbol) => ({
      symbol,
      score: 7.5,
      decision: "Bullish",
      reason: `${symbol} reason`,
    })),
  };
}

describe("resolveAnalysisOutcome", () => {
  it("returns no-data when the backend sends an empty suggestion list", () => {
    expect(resolveAnalysisOutcome(request, { suggestions: [] })).toEqual({
      phase: "no-data",
    });
  });

  it("returns partial-failure with the missing symbols listed", () => {
    expect(resolveAnalysisOutcome(request, responseWithSymbols(["AAPL"]))).toEqual({
      phase: "partial-failure",
      message: "Missing results for MSFT.",
    });
  });

  it("returns success when every requested symbol has a suggestion", () => {
    expect(resolveAnalysisOutcome(request, responseWithSymbols(["AAPL", "MSFT"]))).toEqual({
      phase: "success",
    });
  });
});
