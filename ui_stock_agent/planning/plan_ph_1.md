# PHASE 1 - REQUIREMENTS & PRODUCT SCOPE

---

## Objective

Define the MVP UI scope before implementation so the frontend reflects backend truth and still leaves room for richer explainability later.

---

## Main User

Primary user for MVP:

* developer validating the backend recommendation pipeline

Secondary users:

* analyst reviewing ranked suggestions after the backend is stable
* learner exploring why one symbol was marked bullish, bearish, or neutral

Why this choice:

* the current backend contract is still narrow, so the first release should optimize for observability, speed, and clear recovery states instead of advanced portfolio workflows

---

## MVP Jobs

The MVP UI must let the user:

* input one or more stock symbols
* choose a lookback window in days
* run analysis with one primary action
* compare ranked suggestions quickly
* inspect one symbol in detail
* understand when the backend is unavailable, incomplete, or still loading

---

## MVP Screens

Minimum screens for the first usable release:

* dashboard
  * symbol entry
  * lookback selection
  * run analysis action
  * compact system snapshot
* results state
  * ranked suggestion cards or table
  * score, decision, and reason visible without extra clicks
* stock detail view
  * one-symbol summary
  * reason text
  * placeholders for richer explainability fields as backend contracts expand
* system status view
  * API reachability
  * active environment configuration
  * recovery guidance when the backend cannot be reached

---

## Mandatory UI States

The UI must explicitly handle:

* empty state before a request is submitted
* loading state during analysis
* success state with ranked results
* partial failure when only some requested symbols return usable results
* full failure when the request cannot be completed
* no-data response when the backend returns no suggestions

---

## Current Data Contract

Available from the current backend `/suggest` endpoint:

* request
  * `symbols: string[]`
  * `lookback_days: number`
* response per suggestion
  * `symbol`
  * `score`
  * `decision`
  * `reason`

Desired detail-view data for future backend phases:

* momentum
* sentiment score
* event score
* recent news
* corporate actions

MVP rule:

* the UI should not invent analytical fields client-side; anything beyond the current contract must be labeled as planned or unavailable

---

## Success Criteria

The MVP is successful when:

* a user can submit symbols in under one minute
* results are easy to compare on the first screen
* the reason behind each decision is visible
* failures are understandable and recoverable
* the UI remains usable on desktop and mobile widths

---

## Phase 1 Checklist

* [x] user identified
* [x] jobs identified
* [x] screens listed
* [x] states listed
* [x] success criteria written
