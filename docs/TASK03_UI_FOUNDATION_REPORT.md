# Task 03: White & Gold UI foundation

Completed 10 November 2026. Local implementation only. The eight-screen analytical redesign has not begun.

## Files

| File | Change |
| --- | --- |
| `src/platform/shell.js` | New shared navigation, icons, brand, collapsible sidebar, mobile drawer and route metadata |
| `src/platform/data.js` | Primary navigation list uses the shared screen definitions |
| `src/platform/dashboard.js` | Shell integration, toolbar actions, new destination placeholders, retained legacy routes, detail-drawer keyboard handling |
| `src/platform/style.css` | Consolidated platform tokens, shell and component styling, responsive rules, focus and reduced-motion styles |
| `src/platform/charts.js` | CSS-driven series/grid/tooltip colours and wrapping, keyboard-operable HTML legends; data preparation unchanged |
| `src/platform/presentation.js` | Explains the retained shared trends workspace under Mortality Analytics |
| `tests/shell.test.js` | Primary destination and legacy route regression test |
| `e2e/shell.spec.js` | Desktop/mobile navigation, placeholders, legends, modal focus and source-drawer checks |
| `e2e/comparison.spec.js` | Updates theme expectation for the new default light palette |
| `e2e/usability.spec.js` | Accesses methodology through the new Research navigation grouping |
| `docs/TASK03_UI_FOUNDATION_REPORT.md` | This report |

The production build regenerated ignored `dist/` output. Screenshots were copied to `artifacts/task03/`. Dependency manifests were not changed by this task.

## Tokens and components

Reusable identity variables: `--white: #FFFFFF`, `--gold: #C9A227`, `--ivory: #FAF8F2`, `--champagne: #E8D9AC`, `--charcoal: #252525`, `--border: #E9E5DC`.

Additional semantic tokens cover surfaces, secondary text, accessible gold text, focus, error presentation, control borders, chart grids and five distinct analytical series colours. Shared spacing and radius tokens are available. Gold marks identity, selected navigation, tabs and the comparison action; darker gold text is used for contrast. Cards have restrained borders and no large decorative shadows.

Buttons, inputs, selects, tabs, tables, badges, modal dialogs, chart tooltips, loading, errors and unavailable states use the shared palette. Light mode is the default for users without a saved preference. The existing functional dark-mode toggle and saved preference remain supported.

## Shell and route mapping

The desktop shell has a white sidebar, brand, icons, gold selection marker, accessible collapse control, sticky toolbar, page heading/description and contextual actions. Native title tooltips and accessible names preserve navigation meaning when labels collapse. The existing source/record disclosure opens as a nonmodal right-side detail panel, above the toolbar.

| Primary entry | Route | Current content |
| --- | --- | --- |
| Intelligence Overview | `#overview` | Existing overview and historical observations |
| Comparison Studio | `#comparison` | Labelled foundation screen opening the existing comparison dialog |
| Mortality Analytics | `#trends` | Existing shared trends workspace; description explicitly states the dedicated mortality layout is pending |
| Substance Intelligence | `#substance` | Clearly labelled placeholder linking to existing source exploration; no invented observations |
| Geographic Explorer | `#geography` | Existing area exploration and case study |
| Anomaly Detection & Surveillance Signals | `#anomalies` | Existing anomaly views; related link retains `#signals` |
| Forecasting Lab | `#forecasting` | Existing saved historical projection and evaluation views |
| Research, Data & Exports | `#reports` | Existing reports/exports; related link retains `#methodology` |

Every original deep link remains recognised. Related views retain their own titles and mark their primary parent as active. Browser history and existing hash navigation remain in use.

## Preserved functionality

FastAPI integration, Supabase access architecture, analytical artifacts, filters, comparison restrictions, pagination, CSV/JSON exports and source disclosures remain in place. No backend, permission, migration, model, artifact, chart identity or compatibility changes were made.

Chart presentation still uses Task 02 preparation. Null gaps, meaningful series identities, irregular-period safeguards and bounded-coverage notices remain unchanged. Original records remain attached to chart datasets. The HTML legend wraps full series labels instead of clipping long labels on mobile, and buttons retain series visibility toggling with `aria-pressed`. It does not recalculate or combine observations.

## Responsive behaviour and accessibility

- Desktop sidebar collapses to accessible icons; tablet/mobile navigation becomes a drawer at 900px.
- The mobile drawer has an explicit close button, focus containment, inert background content, scroll locking, Escape dismissal and focus restoration.
- Toolbar actions wrap on small screens; cards and filters reflow; comparison dialogs remain within the viewport.
- Tables keep their columns and use horizontal scrolling inside their containers. Charts resize within their cards; legends wrap outside the canvas.
- Skip navigation, visible keyboard focus, labelled icon controls, current-page markers and reduced-motion rules remain available.
- Opening a record by keyboard focuses the detail close control. Enter's default activation is prevented so it cannot immediately close the newly opened panel.

## Verification

Final results:

| Command | Result |
| --- | --- |
| `npm test` | **41 passed, 0 failed** |
| `npm run build` | **Passed**, 20 modules transformed |
| `npx playwright test e2e/shell.spec.js e2e/comparison.spec.js e2e/usability.spec.js e2e/presentation.spec.js --workers=2` | **11 passed, 0 failed**, Microsoft Edge, approximately 2 minutes |
| `git diff --check` | Passed for tracked changes; existing line-ending notices only |

Browser checks exercised real existing API data, chart rendering and legend toggling, comparison CSV download, modal focus restoration, retry/error and empty states, preserved filters, source details, original deep links, new destinations, mobile overflow and reduced-width layouts. Test-only error/empty responses were intercepted within the existing regression tests; application data was not replaced with fixtures.

Seven sampled contrast pairs measured **6.0:1 to 15.3:1**. This is sampled verification, not a comprehensive accessibility certification. Desktop and mobile screenshots were visually inspected.

Earlier browser runs found two implementation defects: the toolbar covered the mobile detail close button, and Enter could immediately activate the newly focused close button. Both were corrected and passed in the final run. An interrupted initial browser run is not counted as a pass.

The final presentation test recorded approximately 73.1 seconds for its first page readiness and 0.97 seconds for one area change. These are single local observations, not performance benchmarks; startup/backend waiting remains outside this styling task.

## Screenshots

- [Desktop analytics](../artifacts/task03/desktop-analytics.png)
- [Mobile forecast and wrapping legends](../artifacts/task03/mobile-forecast.png)
- [Desktop comparison](../artifacts/task03/comparison-desktop.png)
- [Mobile comparison](../artifacts/task03/comparison-mobile.png)

## Remaining limits and approval

Comparison Studio uses the existing dialog; Substance Intelligence is a placeholder. Mortality Analytics retains the shared trends view, including its other supported measures. Dedicated screen layouts and additional analytical integrations remain for later tasks. Current chart scientific limitations are preserved, not resolved by styling. Browser checks sampled desktop and 390px mobile layouts rather than every device, assistive technology or zoom level.

No outstanding approval issue blocks this completed task. No site was published. Work stops after Task 03; the next implementation phase requires the user's approval.
