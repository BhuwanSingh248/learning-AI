"use client";

import Link from "next/link";
import { DecisionBadge } from "@/features/analysis/components/decision-badge";
import { useAnalysisStore } from "@/store/analysis-store";

export function StockDetailScreen({ symbol }: { symbol: string }) {
  const suggestion = useAnalysisStore((state) =>
    state.response?.suggestions.find((item) => item.symbol === symbol),
  );

  if (!suggestion) {
    return (
      <section className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-8 shadow-panel">
        <p className="text-lg font-semibold">No session data found for {symbol}.</p>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-mist">
          Run an analysis from the dashboard first so the detail page has a symbol to inspect. The
          current backend does not yet expose a dedicated detail endpoint.
        </p>
        <Link
          href="/"
          className="mt-6 inline-flex rounded-full bg-flare px-5 py-3 text-sm font-semibold text-slate-950"
        >
          Return to dashboard
        </Link>
      </section>
    );
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel">
        <p className="text-xs uppercase tracking-[0.35em] text-flare/80">Summary</p>
        <div className="mt-5 flex flex-wrap items-center gap-4">
          <h2 className="text-4xl font-semibold tracking-tight">{suggestion.symbol}</h2>
          <DecisionBadge decision={suggestion.decision} />
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
            <p className="text-xs uppercase tracking-[0.22em] text-mist">Recommendation score</p>
            <p className="mt-3 text-4xl font-semibold">{suggestion.score.toFixed(2)}</p>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
            <p className="text-xs uppercase tracking-[0.22em] text-mist">Contract status</p>
            <p className="mt-3 text-base font-medium text-ink">Current MVP response loaded</p>
          </div>
        </div>
      </article>

      <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel">
        <p className="text-xs uppercase tracking-[0.35em] text-flare/80">Reasoning</p>
        <h3 className="mt-3 text-2xl font-semibold tracking-tight">Why this decision was returned</h3>
        <p className="mt-5 text-sm leading-8 text-mist">{suggestion.reason}</p>

        <div className="mt-8 rounded-[24px] border border-sun/20 bg-sun/10 p-5">
          <p className="text-sm font-semibold text-sun">Planned explainability expansion</p>
          <p className="mt-2 text-sm leading-7 text-slate-100/80">
            Momentum, sentiment, event scoring, news, and corporate actions belong here once the
            backend exposes them. This scaffold keeps the route and layout ready without fabricating
            those values client-side.
          </p>
        </div>
      </article>
    </section>
  );
}
