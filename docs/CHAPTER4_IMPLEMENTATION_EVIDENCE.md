# Chapter 4 — Implementation Evidence

**Evidence snapshot:** 16 November 2026  
**Use:** Dissertation implementation chapter and group demonstration. This document reports the implementation and verified evidence, not scientific validation or institutional approval.

## 1. System architecture

The active application uses a Vite-built, vanilla JavaScript frontend with Chart.js visualizations. A central HTTP client calls the FastAPI service under `/api/v1`; the browser does not connect directly to Supabase. FastAPI serves either reviewed read-only database observations or allow-listed, SHA-256-verified research artifacts. The database and frozen research vintages are shown as separate sources.

| Layer | Implementation evidence |
|---|---|
| Frontend | `src/main.js`, `src/platform/`, `src/api/client.js`; Vite and Chart.js |
| API | `backend/main.py`; FastAPI routes and bounded response envelopes |
| Database access | `backend/repositories/supabase.py`; explicit tables/columns, ordering, exact-count pages and anon/publishable-only access |
| Artifact access | `backend/repositories/artifacts.py`; allowlisted manifests and fail-closed hash/schema verification |
| Domain logic | `backend/services/platform.py`, versioned mortality/forensic adapters, and screen-specific presentation/data modules |
| Local run | [README](../README.md) and [backend README](../backend/README.md) |

The API distinguishes `ready`, `empty`, `unavailable` and `error`. Missing values remain null/unavailable and are not converted to zero. A refresh performs reads; it does not retrain a model or promote a new research vintage.

## 2. Data sources and database evidence

The Task 08M read-only re-audit observed 11 accessible table endpoints and **11,064 rows total**. The current snapshot API exposes only three reviewed source/registry/activity tables; raw RADAR narratives, `radar_alerts`, and unrestricted table selection are not exposed.

| Observed table | Rows | Purpose / evidence qualification |
|---|---:|---|
| `data_sources` | 18 | Source catalog, checksums and publisher/URL metadata |
| `geographic_areas` | 18 | Source area identifiers, labels, types and validity dates |
| `mortality_quarterly` | 36 | National quarterly suspected-death observations |
| `forensic_toxicology` | 210 | Source-reported forensic toxicology observations |
| `assist_toxicology` | 72 | Source-reported ASSIST observations and study periods |
| `naloxone_activity` | 7,024 | 16 geography-week series over 439 weeks |
| `population_estimates` | 2,025 | Area/year/sex population observations |
| `radar_intelligence` | 1,581 | RADAR source records; narrative values are not reproduced or served |
| `radar_alerts` | 0 | No visible records; empty is not proof of no official alert |
| `indicator_configurations` | 4 | Existing monitoring configuration records |
| `indicator_results` | 76 | Existing monitoring result records |

The three `database-v1` projections have explicit fields:

- `data_sources`: dataset name, publisher, URL, SHA-256, notes and source ID.
- `geographic_areas`: area code/name/type, validity dates and source dataset.
- `naloxone_activity`: reporting week, reported geography, administration count, source-reported moving average and source dataset.

The API pagination check retrieved 7,024 naloxone rows in 15 pages of 500, with exact totals, 7,024 unique geography-week keys, 439 complete weeks and 14 NHS boards. Scotland matched the 14-board sum plus Unknown for all 439 weeks. These are row-level observation and arithmetic checks, not a provider interpretation of Unknown.

Task 08M found 14 additional live first-week board moving-average values versus the local/frozen source and 14 populated `valid_to` fields absent from the local import reference. Their lineage is unresolved. The application displays the live database representation separately and does not change frozen artifacts or recompute research results. A matching source checksum alone does not establish those fields' provenance.

PostgREST returned HTTP 401 for its metadata root during Task 08M; therefore deployed SQL types, constraints, indexes, policies and grants are not claimed as verified. `radar_alerts` returned zero visible rows, so its columns remain unverified. See [the full re-audit](./TASK08M_FULL_SUPABASE_REAUDIT.md).

## 3. Backend and API implementation

The API provides:

- Health, overview, geographic/indicator registries and research-source views.
- Versioned police-mortality and forensic-collection routes with source-specific pagination, validation, provenance and explicit rollback choices.
- Historical mortality, substance, naloxone, anomaly, contextual-evidence, forecast, reporting and export routes backed by allowlisted artifacts.
- Existing live mortality and monitoring reads, plus the separate `database-v1` snapshot routes for source catalog, geographic registry and naloxone activity.
- CSV/JSON exports with bounded pages, source/contract metadata and injection-safe CSV cell handling.

Read errors, RLS-style empty results, malformed responses, unsupported resources, invalid filters, incomplete pages and unavailable/corrupted artifacts are not converted into successful-looking data. The application does not execute analytical scripts over HTTP or accept arbitrary file paths/SQL.

## 4. Frontend screen evidence

The eight primary screens are:

1. **Intelligence Overview** — source/cutoff context and independent database/artifact status.
2. **Comparison Studio** — compatible, same-source/boundary comparisons with aligned periods and bounded results.
3. **Mortality Analytics** — source-specific mortality series, filters, charts, tables and exports.
4. **Substance Intelligence** — forensic/ASSIST/treatment sources shown with their distinct units and periods.
5. **Geographic Explorer** — boundary-first selectors, rankings, profiles, coverage, comparisons and explicit unavailable-map state.
6. **Anomaly Detection & Surveillance Signals** — historical flags, sensitivity, runs, cross-source context and external-validation status.
7. **Forecasting Lab** — frozen historical forecasts and backtest evidence, labelled with elapsed origin/target periods.
8. **Research, Data & Exports** — methods, source gaps, provenance and live database snapshot pages.

Current full-page browser captures for these destinations are listed in [the final screenshot checklist](./FINAL_SCREENSHOT_CHECKLIST.md). E2E acceptance covers real API-driven navigation, selected filters, compatible health-board comparisons, export scope, empty/unavailable/error states, responsive rendering and no direct browser-to-Supabase request.

## 5. Forecasting and anomaly methodology

The application presents existing frozen analytical outputs; this sprint did not fit models, select a new forecast, revise thresholds or regenerate scientific results.

- The historical anomaly screen preserves the original prior-only robust median/MAD screen and its recorded flags.
- Conditional Gamma–Poisson, NB2-moments, seasonal and trend count-model outputs remain separate method-specific comparisons; their limits are not relabelled as equivalent to robust-screen limits.
- Stored research flags are not alerts, confirmed toxicity incidents or independent events. Internal sensitivity/model robustness is not external validation.
- The forecast screen retains the saved historical origin (2025 Q4), elapsed target (2026 Q1), point estimate, bounds and model/backtest metadata. It is not a current forecast.
- Official-alert/FOI reference data remain pending; no alert sensitivity, specificity, lead-time or prospective performance is calculated.

Earlier Phase 8 evidence reports 47 original robust flags, 40 NB2-moments flags and 44 original statistical runs. The current test suite verifies access/presentation and preservation, not the clinical validity of these methods.

## 6. Verification and preservation

On 16 November 2026:

- `npm test`: 108 passed.
- `python -m pytest analysis/tests backend/tests -q -p no:cacheprovider`: 167 passed; one existing Starlette/HTTPX deprecation warning.
- `npm run build`: passed.
- Full browser suite: final rerun and exact result are recorded in [Final Acceptance Test Results](./FINAL_ACCEPTANCE_TEST_RESULTS.md).
- Live API pagination/reconciliation: 7,024/7,024 naloxone rows, exact counts, unique keys and 439/439 weekly Scotland reconciliation.
- Production bundle scan: two configured Supabase URL/key values checked; no matches and no secret/service-role marker.
- Research preservation: the passing analysis/backend suite includes checks against the existing 85-entry source/research manifest evidence and frozen-artifact guards. No model run, artifact promotion or database write occurred.

These checks do not constitute a penetration test, exhaustive accessibility audit, production load test or scientific validation.

## 7. Figure and table references

- **Figure 4.1:** Platform architecture — derive from the system flow in section 1.
- **Figures 4.2–4.9:** Eight screen captures in [Final Screenshot Checklist](./FINAL_SCREENSHOT_CHECKLIST.md).
- **Table 4.1:** Database row counts and evidence qualifications in section 2.
- **Table 4.2:** API routes and implementation layers in section 3.
- **Table 4.3:** Screen descriptions in section 4.
- **Table 4.4:** Acceptance test outcomes in [Final Acceptance Test Results](./FINAL_ACCEPTANCE_TEST_RESULTS.md).

Insert figures from the referenced genuine local screenshots; do not redraw a capture as if it were the live application.

## 8. Limitations to state in the dissertation

This is a supervised historical research prototype, not an operational warning service. Current deployment, institutional authentication/roles, production rate limits and recovery, external/prospective validation, PHS endorsement, complete WCAG conformance, source provenance for the flagged live fields, and the full database catalog schema are not established. The project makes no unsupported Greenock attribution, map, cross-boundary peer ranking, current forecast, or no-harm/no-alert inference.
