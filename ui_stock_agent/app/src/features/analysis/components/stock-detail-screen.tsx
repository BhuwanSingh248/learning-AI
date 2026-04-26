"use client";

import Link from "next/link";
import { DecisionBadge } from "@/features/analysis/components/decision-badge";
import { useAnalysisStore } from "@/store/analysis-store";
import type { SuggestionItem } from "@/types/stock";

function formatSignedValue(value?: number) {
  if (typeof value !== "number") {
    return "--";
  }

  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}`;
}

function formatDateTime(value?: string) {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function MetricCard({
  label,
  value,
  caption,
}: {
  label: string;
  value: string;
  caption?: string;
}) {
  return (
    <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
      <p className="text-xs uppercase tracking-[0.22em] text-mist">{label}</p>
      <p className="mt-3 text-2xl font-semibold">{value}</p>
      {caption ? <p className="mt-2 text-sm leading-6 text-mist">{caption}</p> : null}
    </div>
  );
}

function SectionTitle({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="space-y-2">
      <p className="text-xs uppercase tracking-[0.35em] text-flare/80">{eyebrow}</p>
      <h3 className="text-2xl font-semibold tracking-tight">{title}</h3>
      <p className="text-sm leading-7 text-mist">{description}</p>
    </div>
  );
}

function SignalBreakdownSection({ suggestion }: { suggestion: SuggestionItem }) {
  const signal = suggestion.signalBreakdown;

  return (
    <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel">
      <SectionTitle
        eyebrow="Signals"
        title="Structured signal breakdown"
        description="Numeric indicators remain the primary decision input. These fields will appear automatically once the backend includes them."
      />

      {signal ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <MetricCard label="Trend" value={signal.trend?.toUpperCase() ?? "--"} />
          <MetricCard label="Momentum" value={formatSignedValue(signal.momentum)} />
          <MetricCard label="Volatility" value={formatSignedValue(signal.volatility)} />
          <MetricCard label="Sentiment" value={formatSignedValue(signal.sentiment)} />
          <MetricCard label="Event score" value={formatSignedValue(signal.eventScore)} />
          <MetricCard
            label="Decision mode"
            value={suggestion.rag?.enabled ? "Signals + context" : "Signals only"}
          />
        </div>
      ) : (
        <div className="mt-6 rounded-[24px] border border-dashed border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-mist">
          The current detail payload does not include momentum, volatility, sentiment, or event
          scores yet. This section is reserved for the Phase 7 signal contract without fabricating
          client-side values.
        </div>
      )}
    </article>
  );
}

function RagPipelineSection({ suggestion }: { suggestion: SuggestionItem }) {
  const rag = suggestion.rag;

  return (
    <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel">
      <SectionTitle
        eyebrow="RAG pipeline"
        title="How retrieval fits this decision"
        description="Tasks 7.1 to 7.5 place retrieval between analysis and reasoning. The UI keeps that architecture visible without assuming values the backend did not send."
      />

      {rag?.enabled ? (
        <div className="mt-6 space-y-4">
          <div className="rounded-[24px] border border-flare/20 bg-flare/10 p-4 text-sm leading-7 text-slate-100">
            Analysis to retrieval to reasoning is active for this symbol. Signals stay primary,
            and retrieved context is used as supporting evidence.
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <MetricCard label="Embedding model" value={rag.embeddingModel ?? "--"} />
            <MetricCard
              label="Vector dimension"
              value={rag.vectorDimension ? String(rag.vectorDimension) : "--"}
            />
            <MetricCard label="Index type" value={rag.indexType ?? "--"} />
            <MetricCard
              label="Retrieval"
              value={rag.retrievalStrategy ?? "--"}
              caption={typeof rag.topK === "number" ? `Top-K set to ${rag.topK}` : undefined}
            />
            <MetricCard label="Prompt mode" value={rag.promptMode ?? "signals+context"} />
            <MetricCard
              label="Fallback"
              value={rag.fallbackUsed ? "Signals-first fallback used" : "Context applied cleanly"}
            />
          </div>
        </div>
      ) : (
        <div className="mt-6 rounded-[24px] border border-dashed border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-mist">
          The current backend response is still operating in signals-only mode or has not exposed
          retrieval metadata yet. Once Phase 7 endpoints include RAG fields, this section will show
          embedding, FAISS, retrieval, and prompt-mode details here.
        </div>
      )}
    </article>
  );
}

function RetrievedContextSection({ suggestion }: { suggestion: SuggestionItem }) {
  const contextItems = suggestion.rag?.contextItems ?? [];

  return (
    <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel">
      <SectionTitle
        eyebrow="Context"
        title="Retrieved news and evidence"
        description="This is where the UI surfaces the retrieval output that gets appended to the reasoning prompt."
      />

      {suggestion.rag?.contextPreview ? (
        <div className="mt-6 rounded-[24px] border border-white/10 bg-slate-950/30 p-4">
          <p className="text-xs uppercase tracking-[0.22em] text-mist">Formatted context preview</p>
          <p className="mt-3 text-sm leading-7 text-slate-100/80">
            {suggestion.rag.contextPreview}
          </p>
        </div>
      ) : null}

      {contextItems.length ? (
        <div className="mt-6 grid gap-4">
          {contextItems.map((item, index) => (
            <article
              key={`${item.title}-${index}`}
              className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="space-y-2">
                  <h4 className="text-lg font-semibold">{item.title}</h4>
                  {item.summary ? (
                    <p className="text-sm leading-7 text-mist">{item.summary}</p>
                  ) : null}
                </div>
                {typeof item.relevanceScore === "number" ? (
                  <span className="rounded-full border border-flare/20 bg-flare/10 px-3 py-1 text-xs uppercase tracking-[0.18em] text-flare">
                    Match {item.relevanceScore.toFixed(2)}
                  </span>
                ) : null}
              </div>

              <div className="mt-4 flex flex-wrap gap-3 text-xs uppercase tracking-[0.18em] text-mist">
                {item.source ? <span>{item.source}</span> : null}
                {formatDateTime(item.timestamp) ? <span>{formatDateTime(item.timestamp)}</span> : null}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="mt-6 rounded-[24px] border border-dashed border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-mist">
          No retrieved context is available for this symbol yet. The UI is ready for Task 7.4 and
          7.5 payloads, including no-result fallbacks.
        </div>
      )}
    </article>
  );
}

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
      <div className="space-y-6">
        <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel">
          <p className="text-xs uppercase tracking-[0.35em] text-flare/80">Summary</p>
          <div className="mt-5 flex flex-wrap items-center gap-4">
            <h2 className="text-4xl font-semibold tracking-tight">{suggestion.symbol}</h2>
            <DecisionBadge decision={suggestion.decision} />
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <MetricCard label="Recommendation score" value={suggestion.score.toFixed(2)} />
            <MetricCard
              label="Reasoning mode"
              value={suggestion.rag?.enabled ? "Signals + context" : "Signals only"}
              caption={
                suggestion.rag?.fallbackUsed
                  ? "Context was present, but the backend fell back to signals-first behavior."
                  : undefined
              }
            />
          </div>
        </article>

        <SignalBreakdownSection suggestion={suggestion} />
        <RagPipelineSection suggestion={suggestion} />
      </div>

      <div className="space-y-6">
        <article className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel">
          <SectionTitle
            eyebrow="Reasoning"
            title="Why this decision was returned"
            description="The explanation below comes from the backend response. The UI does not invent additional financial logic."
          />
          <p className="mt-6 text-sm leading-8 text-mist">{suggestion.reason}</p>

          <div className="mt-8 rounded-[24px] border border-sun/20 bg-sun/10 p-5">
            <p className="text-sm font-semibold text-sun">Signals stay primary</p>
            <p className="mt-2 text-sm leading-7 text-slate-100/80">
              Tasks 7.1 to 7.5 make retrieval a supporting layer, not a replacement for structured
              analysis. This panel is ready to surface that balance once the backend exposes the
              richer Phase 7 contract.
            </p>
          </div>
        </article>

        <RetrievedContextSection suggestion={suggestion} />
      </div>
    </section>
  );
}
