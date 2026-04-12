# PHASE 2 - FRONTEND ARCHITECTURE & WORKSPACE SETUP

---

## Objective

Lock the frontend stack, workspace structure, and environment contract for a Next.js implementation of the stock-agent UI.

---

## Chosen Stack

* Next.js App Router
* React
* TypeScript
* TanStack Query
* Zustand
* React Hook Form
* Zod
* Tailwind CSS
* Recharts
* Vitest + Testing Library
* Playwright

Why Next.js instead of the original Vite recommendation:

* file-based routing fits the dashboard, detail, and status views well
* App Router gives a clean path to hybrid rendering later if market data pages need server components
* the user explicitly requested a Next.js setup for the UI workspace

---

## Workspace Structure

```text
ui_stock_agent/
  planning/
  task/
  app/
    src/
      app/
        status/
        stocks/[symbol]/
      components/
        providers/
      features/
        analysis/
          components/
      hooks/
      lib/
      services/
      store/
      types/
```

---

## Environment Contract

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_APP_NAME=UI Stock Agent
NEXT_PUBLIC_ENABLE_MOCKS=false
```

---

## Architecture Rules

* keep backend communication inside service modules
* keep server state in TanStack Query and session-level UI state in Zustand
* map backend snake_case payloads to frontend camelCase models in one place
* avoid business scoring or recommendation logic in the frontend
* prepare shared patterns for empty, loading, success, partial-failure, full-failure, and no-data states
* treat system status as contract-aware infrastructure feedback, not a separate analytics feature

---

## Testing Baseline

* unit tests for input parsing and API contract adapters
* component tests for the main analysis flow
* end-to-end coverage for submit, results render, and degraded API behavior

---

## Phase 2 Checklist

* [x] stack chosen
* [x] future folder structure defined
* [x] environment contract defined
* [x] state strategy decided
* [x] testing layers identified
