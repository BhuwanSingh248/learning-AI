# PHASE 2 - FRONTEND ARCHITECTURE & WORKSPACE SETUP

---

## Objective

Lock the frontend stack and the future project structure before any UI code is written.

---

## Recommended Stack

* React
* TypeScript
* Vite
* React Router
* TanStack Query
* Zustand
* React Hook Form
* Zod
* Tailwind CSS
* Recharts
* Vitest
* Playwright

---

## Suggested Future Structure

```text
ui_stock_agent/
  planning/
  task/
  app/
    src/
      components/
      features/
      pages/
      services/
      store/
      hooks/
      types/
      styles/
```

---

## Environment Requirements

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=UI Stock Agent
VITE_ENABLE_MOCKS=false
```

---

## Architecture Rules

* keep backend communication inside service modules
* keep server state separate from view state
* derive display models from typed API models
* avoid business scoring logic in the frontend

---

## Phase 2 Checklist

* [ ] stack chosen
* [ ] future folder structure defined
* [ ] environment contract defined
* [ ] state strategy decided
* [ ] testing layers identified
