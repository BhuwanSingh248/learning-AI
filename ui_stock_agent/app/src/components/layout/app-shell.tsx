import Link from "next/link";
import { env } from "@/lib/env";

type AppShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
};

export function AppShell({
  eyebrow,
  title,
  description,
  children,
}: AppShellProps) {
  return (
    <main className="min-h-screen bg-hero">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 py-8 sm:px-10">
        <header className="rounded-[28px] border border-white/10 bg-[rgba(7,14,27,0.72)] px-6 py-5 shadow-panel backdrop-blur">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-3">
              <p className="text-xs uppercase tracking-[0.35em] text-flare/80">
                {eyebrow}
              </p>
              <div className="space-y-2">
                <h1 className="text-3xl font-semibold tracking-tight sm:text-5xl">
                  {title}
                </h1>
                <p className="max-w-xl text-sm leading-7 text-mist sm:text-base">
                  {description}
                </p>
              </div>
            </div>

            <nav className="flex flex-wrap items-center gap-3 text-sm text-mist">
              <Link
                href="/"
                className="rounded-full border border-white/10 px-4 py-2 transition hover:border-flare/40 hover:text-ink"
              >
                Dashboard
              </Link>
              <Link
                href="/status"
                className="rounded-full border border-white/10 px-4 py-2 transition hover:border-flare/40 hover:text-ink"
              >
                System status
              </Link>
              <span className="rounded-full bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.25em]">
                {env.appName}
              </span>
            </nav>
          </div>
        </header>

        {children}
      </div>
    </main>
  );
}
