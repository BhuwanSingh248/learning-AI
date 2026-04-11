# Phase 2 - Frontend Workspace Setup Guide

---

# Objective

Decide how the UI project should be organized before implementation starts.

No UI code yet.
Only stack, structure, tooling, and environment planning.

---

# STEP 1 - Choose the frontend stack

Recommended:

* React + TypeScript
* Vite
* React Router
* TanStack Query
* Zustand
* Tailwind CSS
* Recharts

Why:

* fast setup
* typed API integration
* simple separation between server state and UI state

---

# STEP 2 - Define the future folder structure

Suggested structure:

```text
app/
  src/
    components/
    features/
    pages/
    services/
    store/
    hooks/
    types/
    utils/
```

---

# STEP 3 - Define environment variables

Minimum values:

* `VITE_API_BASE_URL`
* `VITE_APP_NAME`
* `VITE_ENABLE_MOCKS`

---

# STEP 4 - Decide testing layers

Plan for:

* unit tests
* component tests
* end-to-end tests

---

# STEP 5 - Decide architecture rules

Rules:

* no backend calls directly inside page components
* typed service layer for API access
* no frontend-only score calculations
* all status states handled in shared patterns

---

# Completion Checklist

* [ ] stack locked
* [ ] folder structure planned
* [ ] env contract written
* [ ] testing scope chosen
* [ ] architecture rules written
