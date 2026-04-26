"use client";

import { useSystemStatus } from "@/hooks/use-system-status";
import { env } from "@/lib/env";
import type { SystemSubsystemStatus } from "@/types/stock";

const levelStyles: Record<string, string> = {
  healthy: "text-flare",
  degraded: "text-sun",
  unavailable: "text-ember",
};

const subsystemBadgeStyles: Record<string, string> = {
  healthy: "border-flare/20 bg-flare/10 text-flare",
  degraded: "border-sun/20 bg-sun/10 text-sun",
  unavailable: "border-ember/20 bg-ember/10 text-ember",
  planned: "border-white/10 bg-white/[0.05] text-mist",
};

function SubsystemCard({
  subsystem,
  detailed,
}: {
  subsystem: SystemSubsystemStatus;
  detailed: boolean;
}) {
  return (
    <article className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-ink">{subsystem.label}</h3>
        <span
          className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.18em] ${
            subsystemBadgeStyles[subsystem.level] ?? subsystemBadgeStyles.planned
          }`}
        >
          {subsystem.level}
        </span>
      </div>

      <p className="mt-3 text-sm leading-7 text-mist">{subsystem.summary}</p>

      {subsystem.metrics?.length ? (
        <dl className="mt-4 space-y-2 text-xs uppercase tracking-[0.16em] text-mist">
          {subsystem.metrics.map((metric) => (
            <div key={`${subsystem.key}-${metric.label}`} className="flex items-center justify-between gap-3">
              <dt>{metric.label}</dt>
              <dd className="font-mono text-[11px] text-ink">{metric.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}

      {detailed && subsystem.details ? (
        <p className="mt-4 text-sm leading-7 text-slate-100/75">{subsystem.details}</p>
      ) : null}
    </article>
  );
}

export function SystemStatusPanel({ detailed = false }: { detailed?: boolean }) {
  const { data, isLoading, isError, error } = useSystemStatus();
  const subsystems = data?.subsystems ?? [];

  return (
    <section className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel backdrop-blur">
      <div className="mb-6 space-y-2">
        <p className="text-xs uppercase tracking-[0.35em] text-flare/80">System status</p>
        <h2 className="text-2xl font-semibold tracking-tight">Backend and Phase 7 readiness</h2>
        <p className="max-w-xl text-sm leading-7 text-mist">
          The UI prefers a dedicated `/health` endpoint and falls back to `openapi.json` when the
          backend is still on the earlier MVP contract.
        </p>
      </div>

      {isLoading ? (
        <div className="h-36 animate-pulse rounded-[26px] border border-white/10 bg-white/[0.04]" />
      ) : null}

      {isError ? (
        <div className="rounded-[24px] border border-ember/20 bg-ember/10 p-5 text-sm text-rose-100">
          <p className="font-semibold">Status probe failed.</p>
          <p className="mt-2 text-rose-100/80">
            {error instanceof Error ? error.message : "Unable to reach the backend status probe."}
          </p>
        </div>
      ) : null}

      {data && !isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
            <p className="text-xs uppercase tracking-[0.22em] text-mist">Current level</p>
            <p className={`mt-3 text-3xl font-semibold ${levelStyles[data.level] ?? "text-ink"}`}>
              {data.level}
            </p>
            <p className="mt-2 text-sm leading-7 text-mist">{data.summary}</p>
          </div>

          <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
            <p className="text-xs uppercase tracking-[0.22em] text-mist">Environment</p>
            <dl className="mt-3 space-y-3 text-sm text-ink">
              <div className="flex items-center justify-between gap-3">
                <dt className="text-mist">API base URL</dt>
                <dd className="font-mono text-xs">{env.apiBaseUrl}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-mist">Mock mode</dt>
                <dd className="font-mono text-xs">
                  {env.enableMocks ? "enabled" : "disabled"}
                </dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="text-mist">Probe target</dt>
                <dd className="font-mono text-xs">{data.probeTarget ?? "/health"}</dd>
              </div>
            </dl>
          </div>

          {subsystems.length ? (
            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 md:col-span-2">
              <p className="text-xs uppercase tracking-[0.22em] text-mist">Phase 7 modules</p>
              <div
                className={`mt-4 grid gap-4 ${
                  detailed ? "lg:grid-cols-2" : "md:grid-cols-2"
                }`}
              >
                {subsystems.map((subsystem) => (
                  <SubsystemCard
                    key={subsystem.key}
                    subsystem={subsystem}
                    detailed={detailed}
                  />
                ))}
              </div>
            </div>
          ) : null}

          {detailed ? (
            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 md:col-span-2">
              <p className="text-xs uppercase tracking-[0.22em] text-mist">Notes</p>
              <p className="mt-3 text-sm leading-7 text-mist">{data.details}</p>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
