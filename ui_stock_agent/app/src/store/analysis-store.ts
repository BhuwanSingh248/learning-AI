"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AnalysisPhase, SuggestRequest, SuggestResponse } from "@/types/stock";

type AnalysisStore = {
  phase: AnalysisPhase;
  request: SuggestRequest | null;
  response: SuggestResponse | null;
  errorMessage: string | null;
  updatedAt: string | null;
  setLoading: (request: SuggestRequest) => void;
  setSuccess: (
    request: SuggestRequest,
    response: SuggestResponse,
    phase: Exclude<AnalysisPhase, "idle" | "loading" | "failure">,
    errorMessage?: string,
  ) => void;
  setFailure: (request: SuggestRequest, errorMessage: string) => void;
};

export const useAnalysisStore = create<AnalysisStore>()(
  persist(
    (set) => ({
      phase: "idle",
      request: null,
      response: null,
      errorMessage: null,
      updatedAt: null,
      setLoading: (request) =>
        set({
          phase: "loading",
          request,
          response: null,
          errorMessage: null,
          updatedAt: new Date().toISOString(),
        }),
      setSuccess: (request, response, phase, errorMessage) =>
        set({
          phase,
          request,
          response,
          errorMessage: errorMessage ?? null,
          updatedAt: new Date().toISOString(),
        }),
      setFailure: (request, errorMessage) =>
        set({
          phase: "failure",
          request,
          response: null,
          errorMessage,
          updatedAt: new Date().toISOString(),
        }),
    }),
    {
      name: "ui-stock-agent-analysis",
      partialize: (state) => ({
        phase: state.phase,
        request: state.request,
        response: state.response,
        errorMessage: state.errorMessage,
        updatedAt: state.updatedAt,
      }),
    },
  ),
);
