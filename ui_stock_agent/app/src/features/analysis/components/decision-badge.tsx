import type { SuggestionDecision } from "@/types/stock";

const decisionStyles: Record<string, string> = {
  bullish: "bg-flare/15 text-flare ring-1 ring-flare/30",
  bearish: "bg-ember/15 text-ember ring-1 ring-ember/30",
  neutral: "bg-sun/15 text-sun ring-1 ring-sun/30",
};

export function DecisionBadge({ decision }: { decision: SuggestionDecision }) {
  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${
        decisionStyles[decision.toLowerCase()] ?? "bg-white/10 text-ink ring-1 ring-white/10"
      }`}
    >
      {decision}
    </span>
  );
}
