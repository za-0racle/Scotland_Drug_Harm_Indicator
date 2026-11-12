# Task 04: Intelligence Overview

Completed locally on 11 November 2026. Only the Intelligence Overview analytical screen was redesigned. Tasks 02 and 03 remain in place; no backend, database policy, statistical model, frozen artifact or dependency was changed.

## Files

| File | Purpose |
| --- | --- |
| `src/platform/overview.js` | Overview cards, source disclosures, year controls, accessible heatmap, previews and research navigation |
| `src/platform/overview-data.js` | Pure KPI/heatmap preparation, source compatibility checks, forecast labels and independent API error handling |
| `src/platform/dashboard.js` | Mounts the overview within the existing shell and retains the shared mortality chart, observations table and verification panel |
| `src/platform/style.css` | Scoped overview layouts, KPI/card styling and sequential heatmap colours |
| `tests/overview.test.js` | Six new focused unit tests |
| `e2e/overview.spec.js` | Three new browser tests, including desktop/tablet/mobile screenshot capture |
| `playwright.overview.config.js` | Reuses the existing test setup on ports 4173 and 8000, leaving development port 5173 untouched |
| `docs/TASK04_OVERVIEW_REPORT.md` | This report |
| `artifacts/task04/` | Final desktop, tablet and mobile screenshots |

The production build regenerated ignored `dist/` output.

## Components and sources

| Section | Existing API | Interpretation |
| --- | --- | --- |
| Research scope and KPIs | `/overview` | Latest national suspected-death quarter, latest complete annual total and descriptive change, mortality reporting coverage, artifact-backed source families |
| Quarterly mortality line | Mortality response embedded in `/overview` | Uses the unchanged Task 02 chart preparation; original observations and metadata retained |
| Year-by-quarter heatmap | Same mortality response | Semantic HTML table with exact counts; missing records and null values are unavailable, not zero |
| Geographic highlight | `/geography/inverclyde` | Inverclyde council registered deaths and existing published five-year age-standardised rate comparison; no invented map or Greenock outcome |
| Substance preview | `/toxicology/forensic?limit=1000` | Latest verified period in the complete returned broad-category forensic dataset; categories remain separate and overlapping |
| Statistical monitoring | `/anomalies?limit=1&signals_only=true`, `/overview`, `/validation/status` | Verified total historical robust flags and saved runs, with external validation and official-alert distinctions |
| Forecast preview | `/forecasting/results` | Existing saved one-quarter naïve projection; actual origin, target and interval method displayed |
| Coverage and navigation | `/overview` | Resource-specific frozen cutoffs and provenance, with existing hash links to analytical views |

No new API endpoints were added. Data are retrieved through the existing central API client. Resource failures are isolated with settled promises; a failed forecast does not erase mortality or geography, and unavailable mortality does not become zero or hide an independently available forecast.

## Scientific and interaction safeguards

- Every KPI has source context and either its reporting period or an explanation of resource-specific cutoffs. Source-family counts are explicitly not independent-source counts.
- Annual mortality totals require four observed quarters. Reporting coverage and annual cards refer to the full returned mortality history, independently of the selected chart years.
- The year controls apply to the line, heatmap and exact observations table. Invalid year order is explained. All-available-years reset works.
- The heatmap retains original records, inserts only missing display slots, displays zero as zero and uses a labelled sequential count scale. Gold intensity is not a risk threshold or signal classification.
- The mortality line retains Task 02 observation identities and null gaps. Source labels and the existing keyboard-operable wrapping legend remain available.
- Suspected Police Scotland deaths and NRS registered drug misuse deaths remain separate. Published five-year rates are distinguished from unavailable annual council crude rates.
- Forensic counts are not prevalence or mutually exclusive shares. Incomplete responses or mixed definitions withhold the latest-period preview. Individual-substance rankings are explicitly unavailable through the current API.
- Statistical flags and runs are retrospective, correlated research observations, not independent incidents or confirmed public-health alerts. FOI and external-validation status remain visible.
- The saved forecast is labelled with its 2025 Q4 origin and elapsed 2026 Q1 target. The Gaussian one-step random-walk interval methodology and clipped lower bound come from the saved API record. No model is regenerated.
- Every major analytical section includes contextual source information and a disclosure containing the available original records, manifest paths, hashes, dates and definitions. Missing metadata are not invented.
- White/gold tokens, distinct chart-series colours, shell, mobile drawer, focus handling, filters, comparison dialog, existing exports and original routes are preserved.

## Verification

- `npm test`: **47 passed, 0 failed**.
- `npm run build`: **passed**, 22 modules transformed.
- `npx playwright test --config playwright.overview.config.js e2e/overview.spec.js e2e/shell.spec.js e2e/comparison.spec.js e2e/usability.spec.js e2e/presentation.spec.js --workers=2`: **14 passed, 0 failed**.
- The three overview browser tests were subsequently rerun with reduced-motion, top-of-page screenshot capture: **3 passed, 0 failed**. The settled desktop chart and shell capture were visually inspected before copying the screenshots.
- Browser checks used Microsoft Edge and the existing local FastAPI application. They covered KPI mapping, mortality year controls, exact table rows, source disclosures, forecast labelling, isolated mortality/forecast failures, navigation, comparison download and modal focus, existing filters, chart legend toggling, and mobile overflow.
- Six new unit tests cover KPI/source mapping, absent quarters/years, null versus zero, unavailable states, complete forensic coverage and compatible definitions, forecast context and independent API failures.
- Layouts were checked at **1440px desktop, 900px tablet and 390px mobile**. Screenshots use reduced motion and start at the top of the page to avoid capturing an intermediate chart animation or a scrolled sticky toolbar.
- The existing presentation test's seven sampled contrast ratios remained approximately **6.0:1–15.3:1**. Its warmed-page sample was 1.66 seconds and one area change was 1.00 seconds; first cold browser tests were slower. These are single local observations, not performance guarantees or a complete accessibility certification.
- `git diff --check` passed for tracked changes, with existing line-ending notices only.

The browser failure tests intercept responses only inside the test harness. No application observations or research artifacts were replaced with fixtures.

## Screenshots

- [Desktop overview](../artifacts/task04/overview-desktop.png)
- [Tablet overview](../artifacts/task04/overview-tablet.png)
- [Mobile overview](../artifacts/task04/overview-mobile.png)

## Port 5173 explanation

The reported startup error means a process already held port 5173. The project's deliberate `--strictPort` setting prevents Vite from silently choosing another port. The earlier Playwright configuration also launched a Vite server on 5173, so overlapping tests/development could produce this error. No listener was present during the Task 04 diagnostic checks; no process was killed.

The `.venv` prompt does not cause this Node/Vite error. Dependency re-optimisation after a Vite configuration change is normal. If it recurs, reuse the existing server at `http://localhost:5173`, or stop that server in its original terminal with Ctrl+C before running `npm run dev` again. The Task 04 test configuration uses 4173 and does not reserve 5173. The original full-suite configuration remains unchanged.

## Remaining limits

The source data are frozen historical vintages. Independent source periods and populations are not harmonised. Council annual crude-rate denominators, Greenock outcomes, verified map geometry, operational alert validation and individual-substance API exposure remain unavailable. The source-series count describes resource families, and category/area observations must not be added into independent events.

The overview loads its independent resources concurrently but waits for settlement before final rendering; slow API calls can delay completion. No startup/performance optimisation or backend caching change was introduced. The new year selection is local to the national mortality line, heatmap and table; the other previews retain their own source periods. The other seven analytical screens were not redesigned.

No outstanding permission or approval issue blocks this completed task. Nothing was deployed. Work stops after Task 04, awaiting approval for any next phase.
