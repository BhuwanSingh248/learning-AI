"use client";

import Link from "next/link";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { DecisionBadge } from "@/features/analysis/components/decision-badge";
import { useAnalysisStore } from "@/store/analysis-store";
import type { SuggestionItem } from "@/types/stock";

function formatSignedValue(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}`;
}

function MetaPill({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "default" | "accent" | "warn";
}) {
  const toneClasses =
    tone === "accent"
      ? "border-flare/20 bg-flare/10 text-flare"
      : tone === "warn"
        ? "border-sun/20 bg-sun/10 text-sun"
        : "border-white/10 bg-white/[0.04] text-ink";

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs uppercase tracking-[0.18em] ${toneClasses}`}
    >
      <span className="text-mist">{label}</span>
      <span>{value}</span>
    </span>
  );
}

function SuggestionMeta({ suggestion }: { suggestion: SuggestionItem }) {
  const { signalBreakdown, rag } = suggestion;

  return (
    <div className="flex flex-wrap gap-2">
      {signalBreakdown?.trend ? <MetaPill label="Trend" value={signalBreakdown.trend} /> : null}
      {typeof signalBreakdown?.momentum === "number" ? (
        <MetaPill label="Momentum" value={formatSignedValue(signalBreakdown.momentum)} />
      ) : null}
      {typeof signalBreakdown?.sentiment === "number" ? (
        <MetaPill label="Sentiment" value={formatSignedValue(signalBreakdown.sentiment)} />
      ) : null}
      {typeof signalBreakdown?.eventScore === "number" ? (
        <MetaPill label="Event" value={formatSignedValue(signalBreakdown.eventScore)} />
      ) : null}
      <MetaPill
        label="Mode"
        value={rag?.enabled ? "Signals + context" : "Signals only"}
        tone={rag?.enabled ? "accent" : "default"}
      />
      {rag?.enabled && typeof rag.topK === "number" ? (
        <MetaPill label="Top-K" value={String(rag.topK)} tone="accent" />
      ) : null}
      {rag?.fallbackUsed ? <MetaPill label="Fallback" value="Signals first" tone="warn" /> : null}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-[30px] border border-dashed border-white/10 bg-white/[0.03] p-8 text-sm text-mist">
      Submit a symbol batch to see ranked results, decision reasons, and comparison charts here.
    </div>
  );
}

export function ResultsPanel() {
  const { phase, response, request, errorMessage } = useAnalysisStore((state) => state);
  const ragEnabledCount =
    response?.suggestions.filter((suggestion) => suggestion.rag?.enabled).length ?? 0;
  const hasPhase7Fields =
    response?.suggestions.some(
      (suggestion) =>
        suggestion.rag?.enabled ||
        suggestion.rag?.contextPreview ||
        suggestion.signalBreakdown,
    ) ?? false;

  return (
    <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel backdrop-blur">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.35em] text-flare/80">Results</p>
            <h2 className="text-2xl font-semibold tracking-tight">Comparison surface</h2>
          </div>
          {request ? (
            <span className="rounded-full border border-white/10 px-4 py-2 text-xs uppercase tracking-[0.2em] text-mist">
              {request.symbols.length} symbols | {request.lookbackDays}d lookback
            </span>
          ) : null}
        </div>

        {phase === "idle" ? <EmptyState /> : null}

        {phase === "loading" ? (
          <div className="grid gap-4">
            {Array.from({ length: 3 }).map((_, index) => (
              <div
                key={index}
                className="h-28 animate-pulse rounded-[26px] border border-white/10 bg-white/[0.04]"
              />
            ))}
          </div>
        ) : null}

        {phase === "failure" ? (
          <div className="rounded-[30px] border border-ember/20 bg-ember/10 p-6 text-sm text-rose-100">
            <p className="font-semibold">The analysis request failed.</p>
            <p className="mt-2 text-rose-100/80">{errorMessage}</p>
          </div>
        ) : null}

        {(phase === "success" || phase === "partial-failure" || phase === "no-data") &&
        response ? (
          <div className="space-y-4">
            {hasPhase7Fields ? (
              <div className="rounded-[24px] border border-flare/20 bg-flare/10 px-4 py-4 text-sm text-slate-100">
                <p className="font-semibold text-flare">Phase 7 context-aware fields detected</p>
                <p className="mt-2 leading-7 text-slate-100/80">
                  {ragEnabledCount} of {response.suggestions.length} suggestions include retrieved
                  context metadata. Use the detail route to inspect signal breakdowns, retrieval
                  context, and fallback behavior in one place.
                </p>
              </div>
            ) : (
              <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-4 py-4 text-sm text-mist">
                The current backend response still uses the MVP contract. This results view is
                already prepared to surface Phase 7 signal and RAG fields as soon as they are
                returned.
              </div>
            )}

            {phase === "partial-failure" ? (
              <div className="rounded-[24px] border border-sun/20 bg-sun/10 px-4 py-3 text-sm text-sun">
                Some requested symbols did not return results. The UI is still surfacing the
                symbols that did.
              </div>
            ) : null}

            {phase === "no-data" ? (
              <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-4 py-4 text-sm text-mist">
                The backend responded successfully but returned no suggestions for this request.
              </div>
            ) : null}

            {response.suggestions.map((suggestion) => (
              <article
                key={suggestion.symbol}
                className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5 transition hover:border-flare/30"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-semibold">{suggestion.symbol}</h3>
                      <DecisionBadge decision={suggestion.decision} />
                    </div>
                    <p className="max-w-2xl text-sm leading-7 text-mist">{suggestion.reason}</p>
                  </div>

                  <div className="rounded-[22px] border border-white/10 bg-slate-950/30 px-4 py-3 text-right">
                    <p className="text-xs uppercase tracking-[0.22em] text-mist">Score</p>
                    <p className="mt-1 text-3xl font-semibold">
                      {suggestion.score.toFixed(2)}
                    </p>
                  </div>
                </div>

                <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
                  <SuggestionMeta suggestion={suggestion} />
                  <Link
                    href={`/stocks/${suggestion.symbol}`}
                    className="rounded-full border border-white/10 px-4 py-2 text-sm text-mist transition hover:border-flare/40 hover:text-ink"
                  >
                    Inspect detail
                  </Link>
                </div>

                {suggestion.rag?.contextPreview ? (
                  <div className="mt-5 rounded-[24px] border border-white/10 bg-slate-950/35 p-4">
                    <p className="text-xs uppercase tracking-[0.22em] text-mist">
                      Retrieved context preview
                    </p>
                    <p className="mt-3 text-sm leading-7 text-slate-100/80">
                      {suggestion.rag.contextPreview}
                    </p>
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        ) : null}
      </div>

      <div className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel backdrop-blur">
        <div className="mb-6 space-y-2">
          <p className="text-xs uppercase tracking-[0.35em] text-flare/80">At a glance</p>
          <h2 className="text-2xl font-semibold tracking-tight">Score spread</h2>
        </div>

        {response?.suggestions.length ? (
          <div className="h-[340px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={response.suggestions}
                layout="vertical"
                margin={{ left: 8, right: 8 }}
              >
                <CartesianGrid stroke="rgba(144,160,186,0.14)" horizontal={false} />
                <XAxis type="number" stroke="#90a0ba" />
                <YAxis
                  dataKey="symbol"
                  type="category"
                  width={72}
                  stroke="#90a0ba"
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  cursor={{ fill: "rgba(94, 242, 199, 0.08)" }}
                  contentStyle={{
                    background: "#0d1628",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "18px",
                    color: "#e8ecf4",
                  }}
                />
                <Bar dataKey="score" fill="#5ef2c7" radius={[0, 10, 10, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="rounded-[24px] border border-dashed border-white/10 bg-white/[0.03] p-8 text-sm text-mist">
            The chart fills in once at least one suggestion is returned.
          </div>
        )}

        <div className="mt-5 rounded-[24px] border border-white/10 bg-white/[0.04] p-4 text-sm text-mist">
          Scores still come from the backend. When Phase 7 fields are present, the same screen adds
          retrieval context without inventing any extra client-side ranking logic.
        </div>
      </div>
    </section>
  );
}
