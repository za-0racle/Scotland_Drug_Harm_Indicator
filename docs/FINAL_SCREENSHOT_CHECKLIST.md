# Final Screenshot Checklist

**Capture date:** 16 November 2026  
**Capture method:** Playwright + installed Microsoft Edge through the configured local FastAPI/Vite application. The acceptance test navigates the actual primary screens and saves full-page PNG captures; these are not mockups or generated illustrations.

Screenshots are saved under the ignored local test-output directory `test-results/final-screenshots/`. They are present in the current workspace but excluded by `.gitignore`; copy the required images into the dissertation/evidence package before transferring or archiving the project.

| Figure | Screen | Genuine capture | Review |
|---|---|---|---|
| 4.2 | Intelligence Overview | `../test-results/final-screenshots/overview.png` | Confirm source cutoffs and live database status are visible; do not imply current conditions. |
| 4.3 | Comparison Studio | `../test-results/final-screenshots/comparison.png` | Confirm both subjects/boundaries and the raw-count qualification are visible. |
| 4.4 | Mortality Analytics | `../test-results/final-screenshots/trends.png` | Confirm the measure/source and reporting period are labelled. |
| 4.5 | Substance Intelligence | `../test-results/final-screenshots/substance.png` | Confirm source labels and non-additive/denominator limitations are visible. |
| 4.6 | Geographic Explorer | `../test-results/final-screenshots/geography.png` | Confirm selected boundary and area; do not attribute broader-area outcomes to Greenock. |
| 4.7 | Anomaly Detection & Surveillance Signals | `../test-results/final-screenshots/anomalies.png` | Confirm research-only, non-alert wording and method context. |
| 4.8 | Forecasting Lab | `../test-results/final-screenshots/forecasting.png` | Confirm origin/target and elapsed historical forecast qualification. |
| 4.9 | Research, Data & Exports | `../test-results/final-screenshots/reports.png` | Confirm the screen is the research/reporting view, not a public publication portal. |

## Capture and acceptance checks

- [x] All eight primary destinations were navigated in the local application.
- [x] Each screen reached a terminal `ready`, `empty` or `unavailable` state before capture; unexpected errors fail the test.
- [x] Playwright recorded no browser page errors and no direct Supabase browser requests during the screen check.
- [x] The separate live database snapshot E2E case verifies national Scotland and Unknown as separate classes, page totals, next-page changes, CSV export and responsive overflow. Its application page is not one of the eight primary screenshots above.
- [x] Captures are actual local application output. No credentials or configuration files were opened for capture.
- [ ] Before dissertation insertion, inspect the selected PNG at publication size and add a neutral caption/source note. Preserve the originals and avoid cropping away necessary source, boundary or limitation labels.

## Reproduction

From the repository root, configure the local server-only Supabase publishable credential as described in [README](../README.md), start the local FastAPI/Vite services, then run:

```powershell
npx playwright test e2e/acceptance.spec.js -g "all eight sections" --reporter=list
```

The test writes the eight PNG files listed above. It must not be used to claim production deployment, accessibility certification or scientific validity.
