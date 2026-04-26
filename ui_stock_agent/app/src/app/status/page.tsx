import { AppShell } from "@/components/layout/app-shell";
import { SystemStatusPanel } from "@/features/analysis/components/system-status-panel";

export default function StatusPage() {
  return (
    <AppShell
      eyebrow="Infra"
      title="System status"
      description="Health visibility for the current API plus the Phase 7 embedding, retrieval, and reasoning layers when the backend exposes them."
    >
      <div className="grid gap-6">
        <SystemStatusPanel detailed />
      </div>
    </AppShell>
  );
}
