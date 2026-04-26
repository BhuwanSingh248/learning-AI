# Bug 7.6 - `/health` Endpoint Is Not Fully End-to-End

## Summary

`GET /health` currently reports subsystem readiness mostly from object existence and static assumptions, not true runtime checks across critical dependencies.

## Why This Matters

UI status panels and monitoring can show "healthy" even when parts of the real pipeline are degraded or unavailable.

## Current Behavior

Observed in `stock-agent/src/api/routes.py`:

* checks API object presence
* checks FAISS index object state
* does not verify live DB path from health route
* does not verify retrieval execution path
* does not verify LLM availability path

## Expected Behavior

`/health` should reflect actual readiness with meaningful degradation states:

* DB reachable
* embedding layer initialized and usable
* vector index operational
* retrieval path executable
* reasoning/LLM reachable (or clearly marked degraded)

## Suggested Fix

Implement deeper health probes per subsystem and return:

* `healthy` when all critical probes pass
* `degraded` when non-critical probes fail
* `unavailable` when critical probes fail

## Acceptance Criteria

* `/health` response changes based on real probe outcomes
* failures in DB/retrieval/reasoning are reflected in checks
* status is reliable enough for UI system-status display
