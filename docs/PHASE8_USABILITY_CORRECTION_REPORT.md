# Phase 8 usability correction

## Pre-change audit (recorded before implementation)

- Overview headlines describe database row counts and unexplained flags/runs, not mortality or its observation period. Its default table displays storage records.
- Geography and Trends share eight controls; model and substance controls remain visible when irrelevant. Comparison appears before users request a comparison. Blank area/indicator defaults produce an unavailable view on first visit.
- Anomalies show category and comparison controls with no useful role; sensitivity/zero/adequacy views have controls that are ignored or cannot match the resource shape.
- Signals metadata/database tabs show filters that their requests ignore. Runs/evidence need different scopes and supported methods; those dependencies are not explained.
- Forecasting appropriately avoids implying a new current prediction, but origin/target and uncertainty need plain-language interpretation. No arbitrary model/origin selector is warranted when a view has only one supported value.
- Parent changes reset all dependent selections without retaining valid ones; global state carries incompatible choices between sections. No shared reset or consistent advanced-filter disclosure exists.
- Raw nested objects are stringified in table cells, and selected rows open JSON rather than readable detail. Provenance paths appear in the default content.
- There are no modal dialogs. Existing native details panels can meet this need with inline disclosure; adding a modal would add unnecessary focus/background complexity. Technical JSON should remain opt-in inside a titled verification panel.
- Tables use internal field names and technical IDs. Charts have a generic title and do not consistently explain source, geography, period or units.

Planned correction: preserve APIs/results and eight sections; use a shared context-aware inline filter controller, meaningful source-backed defaults, a common reset, More filters disclosure, readable detail/technical layers and mortality-focused overview derived only from live approved observations. Preserve exact exported records. No research or database changes.

## Implementation and verification

### Presentation and overview

The existing Vite/vanilla JavaScript, FastAPI, Chart.js and Supabase architecture is retained. All eight sections and existing API contracts remain. No backend calculation, schema, RLS, input, saved research output or dissertation was changed.

Overview now uses the live approved mortality envelope returned within `/overview`: latest complete annual suspected-death total, change from the preceding complete year, latest observed quarter and observation cutoff. Four distinct valid quarters are required for a total; missing/non-numeric observations prevent a complete-year result. No current-year estimate, imputation, rate or registered-death substitution is made. With the actual response: 2025 total **1,146**, annual change **+7.61%**, 2025 Q4 **248**, cutoff **2025 Q4**. If the database is unavailable, these values are unavailable; frozen artifacts are not silently substituted.

The historical national line chart leads the overview; source records are collapsed under Explore, with provenance under Verify. Each section begins with a plain-language explanation. Field/indicator/method names are translated for presentation without changing original IDs or exported values. Tables show at most seven priority fields; the complete record is still accessible. Nested objects display readable supporting disclosures instead of JSON cells. Metadata/methodology/report sections use readable structured details. Forecast origin/target, historical-only status and uncertainty remain explicit. Charts show measure, geography, source period, unit and source attribution; missing values remain null.

### Shared filter system

New `src/platform/filters.js` owns the existing controls rather than copying dependency logic per section:

- Geographic scope, reporting area and measure are the primary controls. Year range and applicable research-method/comparison/category controls sit in one native **More filters** disclosure.
- Geographic Explorer and Trends start with a supported Scotland suspected-death series. Anomalies and runs start with all supported observations so original full research summaries remain discoverable. Each workspace retains its own selections on navigation.
- All 13 police divisions, 14 health boards, Inverclyde council and the explicit Greenock-unavailable entry remain reachable. No boundary mapping is invented.
- Parent changes reload actual indicator metadata, retain still-valid measure selections and clear invalid area/category/comparison/method selections. Options are ordered by readable labels. Dependent controls are disabled during metadata loading and have explicit unavailable/error states.
- Comparison is shown only in the comparison view. Options require a different area, the same boundary type and the selected indicator in verified metadata. The API's existing compatibility checks remain authoritative.
- Model options use successful stored evaluation metadata rather than implying every model is available for every source. Cross-source evidence only offers its implemented method families. Sensitivity, zero-count review and metadata/database views hide inapplicable controls.
- ASSIST unequal study periods hide calendar-year controls, with a source-specific explanation; source ordinals preserve Q4-to-Q15 ordering rather than lexical Q10-before-Q4 ordering. No calendar dates are inferred.
- A one-to-one substance category is consolidated into its measure selection; the separate category control appears only if metadata supplies multiple meaningful categories. There is no duplicated substance-versus-indicator choice for the same data.
- Forecasting does not show a spurious model/origin dropdown when the projection has one available model/origin. Existing historical observations, candidate scores and backtest tabs remain available. Metadata-only views avoid unnecessary indicator-option fetches; advanced sections collapse consistently on workspace changes.
- Hidden panels do not send stale scope filters. Advanced selections that remain active are counted in the disclosure title. **Reset filters** restores that workspace's supported defaults and closes advanced options.
- Changes apply immediately, as explained beside the controls. No draft state or Apply/Cancel modal was introduced; such buttons would imply an unimplemented staging step.

### Details, keyboard behaviour and auditability

No modal dialog existed or was added. Native inline details are appropriate for this information hierarchy: they do not trap focus or disable the background. Verify has a clear title and Close details control; Escape closes the focused disclosure and restores focus to its summary. Row details open with Enter; closing does not clear filters. Technical record and provenance JSON remain behind separate collapsed disclosures, with original precision and export contracts preserved. Readable nested source/method details are generated on expansion rather than flooding initial content.

### Files changed

New: `src/platform/filters.js`, `src/platform/presentation.js`, `tests/usability.test.js`, `e2e/usability.spec.js`, this report.

Updated: `src/platform/dashboard.js`, `src/platform/data.js`, `src/platform/charts.js`, `src/platform/style.css`, existing `e2e/acceptance.spec.js`, `e2e/dashboard.spec.js`, `e2e/presentation.spec.js`, and `playwright.config.js`. Existing browser assertions retain network/filter/value/error coverage while following the renamed labels and advanced disclosure. No backend source or dependency change.

### Before/after evidence

Local screenshots are under ignored `analysis/test_scratch.local/usability/`:

- `before-overview.png`: technical row-count headlines and default source records.
- `before-filters.png`: eight simultaneous controls and blank initial reporting-area view.
- `after-overview.png`: mortality findings, historical chart and readable Verify details (opened to demonstrate provenance; it is closed by default).
- `after-filters.png`: meaningful national default and shared essential/advanced layout.
- `after-mobile.png`: responsive readable methodology view.

No secret-bearing settings are captured. These are real local-browser captures, not design mockups.

### Executed verification

```powershell
.\analysis\.venv\Scripts\python.exe -m pytest analysis/tests backend/tests -q -p no:cacheprovider
npm test
npm run test:e2e
npm run build
git diff --check
```

- Python: **99 passed in 343.13 seconds**, one existing Starlette/HTTPX deprecation warning. Existing analytical reproduction/leakage/geographic/source-compatibility tests remain unchanged.
- JavaScript: **29 passed**, including complete-year aggregation, missing/zero handling, unavailable prior-year comparisons and source-defined study ordinal ordering. Existing API/security/ordering/forecast/monitoring tests remain.
- Final browser suite: **16 passed in 1.6 minutes**, including five new usability tests. New tests cover first-time overview interpretation, context-aware controls, retained dependent selections, reset, exact model counts, Escape/close/focus behaviour, opt-in JSON, historical forecast labels and mobile layout. Existing actual FastAPI, live-data, geographic coverage, failure and export checks remain.
- Build: **passed**: 16 modules, JavaScript 234.01 kB (80.99 kB gzip), CSS 10.57 kB (3.03 kB gzip).
- Preservation/security/whitespace: **passed**: 85 protected earlier-phase hashes and all Phase 6 input/code/output hashes match; final bundle/whitespace checks passed.

An initial iterative browser run failed an assertion that previously expected a ready overview during a database outage. The assertion now checks the explicit error/unavailable state, preserving the no-fallback requirement. Another run exceeded the old 15-second initial-bootstrap assertion during cold start while reproduction tests were active. Metadata-only pages now avoid unnecessary indicator-option requests, and browser waiting is aligned with the existing bounded 60-second API timeout. This is not a claim that cold startup latency has been eliminated. Final results above are from reruns after corrections.

### Scientific and accessibility assessment

Displayed descriptions remain separate from observed values, exploratory statistical flags, forecasts and official communications. Existing 47 original flags, 44 original runs, model-specific results and the Inverclyde registered-death/rate context are preserved. No Greenock outcome, population rate, current forecast, risk score or official alert was invented. FOI validation remains pending; no external-warning metric was computed.

Keyboard skip/focus, Enter-to-inspect, native summary controls, Escape closing, focus return, mobile overflow, equivalent chart tables and sampled contrast checks are exercised by the browser suite. No external participant study, full screen-reader audit or accessibility certification is claimed. Inline disclosures intentionally allow normal background interaction because they are not modal dialogs.

Remaining issues: first-access artifact latency; inherently technical research methods still need specialist interpretation; large records remain detailed when explicitly expanded; a complete institutional accessibility/user study and the scientific/governance gates from prior reports remain outstanding. No deployment or operational-warning readiness is implied.

Stop for research-team review; no publication or deployment.
