# UI Stock Agent - Complete Phase-wise Plan

---

# PROJECT GOAL

Build a clean, modern UI for the stock recommendation agent that:

* accepts one or more stock symbols
* sends analysis requests to the backend
* presents ranked suggestions clearly
* explains why a stock is bullish, bearish, or neutral
* stays usable during loading, partial failures, and no-data cases

---

# MVP USER OUTCOME

The user should be able to:

* enter symbols and a lookback window
* run analysis in one action
* compare ranked results quickly
* inspect per-stock reasoning, signals, and supporting context
* understand when the system is unavailable or still processing

---

# RECOMMENDED UI ARCHITECTURE

```text
User
  ->
Frontend App (React + TypeScript)
  ->
Query/State Layer
  ->
Backend API
  ->
Stock Agent Pipeline
```

---

# RECOMMENDED STACK

* Frontend App -> React + TypeScript + Vite
* Routing -> React Router
* Server State -> TanStack Query
* Local UI State -> Zustand
* Forms -> React Hook Form + Zod
* Styling -> Tailwind CSS + CSS variables
* Charts -> Recharts
* Unit Tests -> Vitest + Testing Library
* E2E Tests -> Playwright

---

# PHASE 1 - REQUIREMENTS & PRODUCT SCOPE

## Objective

Define what the UI must do before implementation begins.

## Output

* clear MVP scope
* screen inventory
* data requirements
* success criteria

---

# PHASE 2 - FRONTEND ARCHITECTURE & WORKSPACE SETUP

## Objective

Decide the frontend stack, folder structure, and environment contract.

## Output

* locked frontend stack
* future project structure
* API base URL strategy
* testing strategy baseline

---

# PHASE 3 - INFORMATION ARCHITECTURE & USER FLOWS

## Objective

Design the routes, page layout, and primary analysis flow.

## Core Flows

* analyze symbols
* view ranked results
* drill into one stock
* recover from errors

---

# PHASE 4 - DESIGN SYSTEM & COMPONENT STRATEGY

## Objective

Define the reusable UI primitives and visual language.

## Core Areas

* typography and color tokens
* cards, tables, inputs, badges, charts
* skeleton and empty states
* responsive behavior

---

# PHASE 5 - DASHBOARD & RESULTS EXPERIENCE

## Objective

Plan the main screen where users run analysis and compare outcomes.

## Sections

* header and app shell
* symbol input form
* result summary cards
* ranked list or table
* quick charts and signal indicators

---

# PHASE 6 - STOCK DETAIL & EXPLAINABILITY EXPERIENCE

## Objective

Plan the detail view that explains one stock deeply.

## Sections

* decision summary
* score breakdown
* price trend snapshot
* recent news
* corporate actions
* AI reason text

---

# PHASE 7 - API INTEGRATION & DATA CONTRACTS

## Objective

Map frontend needs to backend endpoints and response shapes.

## Required Contracts

* request payload for multi-symbol analysis
* response model for ranked suggestions
* optional detail endpoint for richer views
* health endpoint for system status

---

# PHASE 8 - QUALITY, ACCESSIBILITY & PERFORMANCE

## Objective

Make sure the UI is usable, accessible, and fast.

## Focus

* keyboard usability
* contrast and readable states
* mobile and tablet layouts
* loading and retry behavior
* test coverage for critical flows

---

# PHASE 9 - RELEASE & FUTURE ROADMAP

## Objective

Prepare the UI for delivery and identify next improvements.

## Near-term Extensions

* saved sessions
* watchlist
* compare mode
* live refresh
* export/share results

---

# STRICT BUILD ORDER

1. Requirements and data contracts
2. Frontend architecture decisions
3. App shell and navigation
4. Analysis form and results layout
5. Detail and explainability views
6. API integration
7. Loading, error, and empty states
8. Testing and deployment

---

# FINAL NOTES

* Do not start with styling alone; lock the data flow first.
* The UI should reflect backend truth, not invent analytics client-side.
* Explainability matters as much as the score.
* Design for partial backend completion because the API layer is still evolving.
