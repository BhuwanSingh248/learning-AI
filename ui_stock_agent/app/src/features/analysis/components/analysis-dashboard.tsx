import { AppShell } from "@/components/layout/app-shell";
import { AnalysisForm } from "@/features/analysis/components/analysis-form";
import { Phase7SideBySidePanel } from "@/features/analysis/components/phase7-side-by-side-panel";
import { ResultsPanel } from "@/features/analysis/components/results-panel";
import { SystemStatusPanel } from "@/features/analysis/components/system-status-panel";

export function AnalysisDashboard() {
  return (
    <AppShell
      eyebrow="Unified UI"
      title="Validate ranked stock suggestions with context-aware detail"
      description="Submit a batch of symbols, compare returned recommendations, and inspect how Phase 7 retrieval and reasoning data fits into the same experience when the backend exposes it."
    >
      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <AnalysisForm />
        <SystemStatusPanel />
      </section>

      <Phase7SideBySidePanel />

      <ResultsPanel />
    </AppShell>
  );
}
