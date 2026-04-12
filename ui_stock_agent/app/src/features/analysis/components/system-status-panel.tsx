"use client";

import { useSystemStatus } from "@/hooks/use-system-status";
import { env } from "@/lib/env";

const levelStyles: Record<string, string> = {
  healthy: "text-flare",
  degraded: "text-sun",
  unavailable: "text-ember",
};

export function SystemStatusPanel({ detailed = false }: { detailed?: boolean }) {
  const { data, isLoading, isError, error } = useSystemStatus();

  return (
    <section className="rounded-[30px] border border-white/10 bg-[var(--surface)] p-6 shadow-panel backdrop-blur">
      <div className="mb-6 space-y-2">
        <p className="text-xs uppercase tracking-[0.35em] text-flare/80">System status</p>
        <h2 className="text-2xl font-semibold tracking-tight">Backend reachability</h2>
        <p className="max-w-xl text-sm leading-7 text-mist">
          The page checks `openapi.json` as a temporary health indicator until the backend adds a
          dedicated status endpoint.
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
                <dd className="font-mono text-xs">/openapi.json</dd>
              </div>
            </dl>
          </div>

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
