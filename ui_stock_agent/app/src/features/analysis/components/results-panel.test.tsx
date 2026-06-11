import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it } from "vitest";
import { ResultsPanel } from "@/features/analysis/components/results-panel";
import { useAnalysisStore } from "@/store/analysis-store";

function renderWithQueryClient() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ResultsPanel />
    </QueryClientProvider>,
  );
}

describe("ResultsPanel", () => {
  afterEach(() => {
    cleanup();
    useAnalysisStore.setState({
      phase: "idle",
      request: null,
      response: null,
      errorMessage: null,
      updatedAt: null,
    });
  });

  it("announces loading results with a status region", () => {
    useAnalysisStore.setState({
      phase: "loading",
      request: { symbols: ["AAPL"], lookbackDays: 90 },
      response: null,
      errorMessage: null,
      updatedAt: "2026-06-12T00:00:00.000Z",
    });

    renderWithQueryClient();

    expect(
      screen.getByRole("status", { name: /analysis results are loading/i }),
    ).toBeInTheDocument();
  });

  it("shows failures as alerts with a retry action", () => {
    useAnalysisStore.setState({
      phase: "failure",
      request: { symbols: ["AAPL"], lookbackDays: 90 },
      response: null,
      errorMessage: "Backend unavailable",
      updatedAt: "2026-06-12T00:00:00.000Z",
    });

    renderWithQueryClient();

    expect(screen.getByRole("alert")).toHaveTextContent("Backend unavailable");
    expect(screen.getByRole("button", { name: /retry last request/i })).toBeEnabled();
  });
});
