# Bug FE - Prediction Confidence Scale Mismatch Risk

## Summary

Frontend currently assumes `prediction.confidence` is on a `0..1` scale and formats it as percent.

If backend returns `0..100` values, UI clamps to `100%`, causing incorrect confidence display.

## Impact

Prediction cards can show wrong confidence values, reducing trust in recommendation quality.

## Where

* `ui_stock_agent/app/src/features/analysis/components/phase7-side-by-side-panel.tsx`
* helper: `formatPercent`

## Reproduction

1. Backend returns `prediction.confidence: 82` (percent scale).
2. Open dashboard and run analysis.
3. UI shows `100%` instead of `82%`.

## Expected

UI should support both scales safely:

* if value <= 1, treat as ratio and convert to percent
* if value > 1 and <= 100, treat as percent directly

## Suggested Fix

Update FE formatter with scale detection and keep rendering stable for both contracts.

## Current Status

Fixed in frontend normalization:

* `ui_stock_agent/app/src/services/stock-agent.ts`
* `normalizePredictionMeta` now accepts both:
  * ratio scale (`0..1`)
  * percent scale (`0..100`) and converts to ratio for UI rendering

## Acceptance Criteria

* `0.82` renders as `82%`
* `82` renders as `82%`
* out-of-range values fail gracefully (fallback display)
