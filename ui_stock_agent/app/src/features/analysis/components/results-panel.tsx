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

function EmptyState() {
  return (
    <div className="rounded-[30px] border border-dashed border-white/10 bg-white/[0.03] p-8 text-sm text-mist">
      Submit a symbol batch to see ranked results, decision reasons, and comparison charts here.
    </div>
  );
}

export function ResultsPanel() {
  const { phase, response, request, errorMessage } = useAnalysisStore((state) => state);

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
                  <p className="text-xs uppercase tracking-[0.22em] text-mist">
                    Reason is sourced from the backend response contract
                  </p>
                  <Link
                    href={`/stocks/${suggestion.symbol}`}
                    className="rounded-full border border-white/10 px-4 py-2 text-sm text-mist transition hover:border-flare/40 hover:text-ink"
                  >
                    Inspect detail
                  </Link>
                </div>
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
              <BarChart data={response.suggestions} layout="vertical" margin={{ left: 8, right: 8 }}>
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
      </div>
    </section>
  );
}
