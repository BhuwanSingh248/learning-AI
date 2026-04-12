import { AppShell } from "@/components/layout/app-shell";
import { SystemStatusPanel } from "@/features/analysis/components/system-status-panel";

export default function StatusPage() {
  return (
    <AppShell
      eyebrow="Infra"
      title="System status"
      description="Temporary health visibility while the backend evolves toward a dedicated health endpoint."
    >
      <div className="grid gap-6">
        <SystemStatusPanel detailed />
      </div>
    </AppShell>
  );
}
