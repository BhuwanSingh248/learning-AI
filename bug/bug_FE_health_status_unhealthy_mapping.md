# Bug FE - Health Status `unhealthy` Is Rendered as `planned`

## Summary

Frontend health normalization maps unknown subsystem statuses to `planned`.  
Backend currently returns `status: "unhealthy"` for degraded checks, so UI can show a wrong label/color.

## Impact

System status view can hide real failures:

* backend: `unhealthy`
* UI displayed: `planned`

This makes Phase 7 readiness look better than actual runtime health.

## Where

Frontend mapping logic:

* `ui_stock_agent/app/src/services/stock-agent.ts`
* function: `toSubsystemLevel`

Backend status values:

* `stock-agent/src/api/routes.py`
* `/health` check items use `"unhealthy"` in failure paths

## Reproduction

1. Start backend with one subsystem degraded (for example DB or LLM unavailable).
2. Open frontend status page.
3. Observe one or more subsystem cards showing `planned` instead of failure severity.

## Expected

`unhealthy` from backend should map to either:

* `unavailable` (preferred for hard failure), or
* `degraded` (if team policy treats it as soft failure)

## Suggested Fix

Update FE mapping switch in `toSubsystemLevel` to handle `"unhealthy"` explicitly.

Example mapping:

* `"unhealthy"` -> `"unavailable"`

## Acceptance Criteria

* Any backend check with `status: "unhealthy"` is never rendered as `planned`.
* Status badge and color reflect failure severity consistently across cards.
