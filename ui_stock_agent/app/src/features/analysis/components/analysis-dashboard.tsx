import { AppShell } from "@/components/layout/app-shell";
import { AnalysisForm } from "@/features/analysis/components/analysis-form";
import { ResultsPanel } from "@/features/analysis/components/results-panel";
import { SystemStatusPanel } from "@/features/analysis/components/system-status-panel";

export function AnalysisDashboard() {
  return (
    <AppShell
      eyebrow="Phase 1 MVP"
      title="Validate ranked stock suggestions quickly"
      description="Submit a batch of symbols, compare the returned recommendations, and inspect the reasoning without losing sight of backend health."
    >
      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <AnalysisForm />
        <SystemStatusPanel />
      </section>

      <ResultsPanel />
    </AppShell>
  );
}
