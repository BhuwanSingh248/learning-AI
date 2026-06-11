"use client";

import Link from "next/link";
import { DecisionBadge } from "@/features/analysis/components/decision-badge";
import { useAnalysisStore } from "@/store/analysis-store";
import type { SuggestionItem } from "@/types/stock";

const EMPTY_SUGGESTIONS: SuggestionItem[] = [];

function formatPercent(value?: number) {
  if (typeof value !== "number") {
    return "--";
  }

  const clamped = Math.max(0, Math.min(1, value));
  return `${Math.round(clamped * 100)}%`;
}

function PredictionPanel() {
  const suggestions = useAnalysisStore(
    (state) => state.response?.suggestions ?? EMPTY_SUGGESTIONS,
  );

  if (!suggestions.length) {
    return (
      <div className="rounded-[24px] border border-dashed border-white/10 bg-white/[0.03] p-5 text-sm text-mist">
        Run a batch to see top candidates and next prediction metadata.
      </div>
    );
  }

  const topPredictions = suggestions.slice(0, 3);

  return (
    <div className="space-y-4">
      {topPredictions.map((suggestion, index) => (
        <article
          key={suggestion.symbol}
          className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="rounded-full border border-flare/20 bg-flare/10 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-flare">
                  #{index + 1}
                </span>
                <h3 className="text-lg font-semibold">{suggestion.symbol}</h3>
              </div>
              <DecisionBadge decision={suggestion.decision} />
            </div>
            <div className="text-right">
              <p className="text-xs uppercase tracking-[0.2em] text-mist">Score</p>
              <p className="mt-1 text-2xl font-semibold">{suggestion.score.toFixed(2)}</p>
            </div>
          </div>

          <div className="mt-4 grid gap-2 text-xs uppercase tracking-[0.16em] text-mist sm:grid-cols-2">
            <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
              Horizon: {suggestion.prediction?.horizon ?? "short_term"}
            </div>
            <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
              Bucket: {suggestion.prediction?.rankBucket ?? "not_set"}
            </div>
            <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
              Confidence: {formatPercent(suggestion.prediction?.confidence)}
            </div>
            <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
              Direction: {suggestion.prediction?.expectedDirection ?? "not_set"}
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <Link
              href={`/stocks/${suggestion.symbol}`}
              className="rounded-full border border-white/10 px-3 py-2 text-xs uppercase tracking-[0.16em] text-mist transition hover:border-flare/40 hover:text-ink"
            >
              Open detail
            </Link>
          </div>
        </article>
      ))}
    </div>
  );
}

function RagActivityPanel() {
  const suggestions = useAnalysisStore(
    (state) => state.response?.suggestions ?? EMPTY_SUGGESTIONS,
  );

  if (!suggestions.length) {
    return (
      <div className="rounded-[24px] border border-dashed border-white/10 bg-white/[0.03] p-5 text-sm text-mist">
        RAG activity appears here once analysis runs.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {suggestions.map((suggestion) => {
        const rag = suggestion.rag;
        const contextCount = rag?.contextItems?.length ?? 0;

        return (
          <article
            key={suggestion.symbol}
            className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4"
          >
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-base font-semibold">{suggestion.symbol}</h3>
              <span
                className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.18em] ${
                  rag?.enabled
                    ? "border-flare/20 bg-flare/10 text-flare"
                    : "border-white/10 bg-slate-950/30 text-mist"
                }`}
              >
                {rag?.enabled ? "RAG on" : "RAG off"}
              </span>
            </div>

            <div className="mt-3 grid gap-2 text-xs uppercase tracking-[0.16em] text-mist sm:grid-cols-2">
              <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
                Top-K: {typeof rag?.topK === "number" ? rag.topK : "--"}
              </div>
              <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
                Items: {contextCount}
              </div>
              <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
                Retrieval: {rag?.retrievalStrategy ?? "--"}
              </div>
              <div className="rounded-full border border-white/10 bg-slate-950/30 px-3 py-2">
                Fallback: {rag?.fallbackUsed ? "yes" : "no"}
              </div>
            </div>

            {rag?.contextPreview ? (
              <p className="mt-4 text-sm leading-7 text-mist">{rag.contextPreview}</p>
            ) : (
              <p className="mt-4 text-sm leading-7 text-mist">
                No context preview was returned for this symbol.
              </p>
            )}
          </article>
        );
      })}
    </div>
  );
}

export function Phase7SideBySidePanel() {
  const phase = useAnalysisStore((state) => state.phase);

  if (phase === "idle") {
    return null;
  }

  return (
    <section className="grid gap-6 lg:grid-cols-2">
      <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel backdrop-blur">
        <div className="mb-5 space-y-2">
          <p className="text-xs uppercase tracking-[0.35em] text-flare/80">Next prediction</p>
          <h2 className="text-2xl font-semibold tracking-tight">Top candidates</h2>
          <p className="text-sm leading-7 text-mist">
            Ranked candidate view for immediate decisions, synced with backend prediction metadata.
          </p>
        </div>
        <PredictionPanel />
      </article>

      <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel backdrop-blur">
        <div className="mb-5 space-y-2">
          <p className="text-xs uppercase tracking-[0.35em] text-flare/80">RAG activity</p>
          <h2 className="text-2xl font-semibold tracking-tight">Background retrieval</h2>
          <p className="text-sm leading-7 text-mist">
            Live trace of retrieval mode, context volume, and fallback behavior side by side with
            prediction output.
          </p>
        </div>
        <RagActivityPanel />
      </article>
    </section>
  );
}
