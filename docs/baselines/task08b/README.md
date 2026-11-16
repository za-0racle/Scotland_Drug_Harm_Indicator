# Task 08B — Analytical baseline and schema verification

Captured 12 November 2026. This is a preservation and contract baseline for the proposed Option B analytical layer. **No adapter was implemented.** No endpoint, application source, source dataset, statistical parameter, frozen artifact, database table or policy was changed.

## Deliverables and evidence

| Deliverable | Evidence |
|---|---|
| Baseline verification report | This document and `capture-summary.json` |
| Database metadata matrix | [DATABASE_METADATA.md](DATABASE_METADATA.md), `database-verification.json` |
| Resource-by-resource API inventory | [API_CONTRACTS.md](API_CONTRACTS.md), `resource-contracts.json`, `openapi.json`, `metadata-responses.json` |
| Frozen preservation matrix | [PRESERVATION_MATRIX.md](PRESERVATION_MATRIX.md), `preservation-before.json`, `preservation-verification.json`, `manifest-verification.json` |
| Observation and numerical baseline | `identity-verification.json`, `resource-contracts.json`, `file-inventory.json`, `research-versions.json` |
| Regression baseline | [REGRESSION.md](REGRESSION.md) and test/build logs |
| Risks and unresolved gaps | Sections below and database matrix |
| Proposed first migration resource | Phase 4 `mortality_trends`, described below |

## Verification outcome

- All **18 original-source manifest checks** and **67 research-output manifest checks** match: **85/85**. These are the entries explicitly listed by those manifests, not a claim that all repository files have upstream published checksums.
- All **28 approved catalog resources** were retrieved completely through the existing production service in-process, using pages of at most 1,000 and checking stable totals. Fields, null counts, numerical fingerprints and artifact metadata are recorded per resource.
- Metadata routes and OpenAPI were additionally inspected through the existing FastAPI ASGI application. This is local contract verification, not proof that a separately deployed HTTP service matches it.
- Live read-only Supabase access verified **36 mortality observations, 4 configurations and 76 results**. The metadata endpoint returned **401**; deployed DDL, indexes and policy definitions remain unverified. Eight other expected tables are unverified, not absent.
- Current checks passed: **83 frontend tests, 19 backend tests, 35 browser tests**, plus the production build (29 modules). Commands, scope and warnings are recorded in `REGRESSION.md`; earlier Task 08 results are not substituted for this run.
- A before/after SHA-256 comparison found **293/293 protected files unchanged**, with no additions or removals in the protected set. It covers original sources, nonscratch research files and processing code, frozen legacy inputs, imports, application source and existing regression tests. Generated builds, screenshots, test scratch, dependencies and baseline documentation are outside that preservation set. See the machine-readable final check.

## What the fingerprints establish

File SHA-256 detects any byte-level change. CSV fingerprints retain original parsed strings; resource fingerprints retain ordered API/service values. Numerical projections include existing numeric fields and nominated value fields, with deterministic JSON encoding, sorted keys and SHA-256. Full response fingerprints additionally include metadata fields carried by rows. They are intentionally order-sensitive.

These checks establish a reproducible comparison point. They **do not establish scientific validity**, correct source collection, operational usefulness, causal interpretation or independent external validation. No model fit, forecast evaluation or analytical pipeline was rerun.

The generic candidate-identity projection in `resource-contracts.json` is diagnostic only. It does not include every resource's identity dimensions. Its duplicate counts must not be described as duplicate source observations. `identity-verification.json` separately checks explicit keys for the observation families, model outputs, rates and forecasts. Nested documents, metric scopes, evidence pairs and signal runs need their own identities rather than an observation key.

## Frozen research identities and definitions

The baseline preserves existing source versions/hashes, all six research manifests, model configurations and source-record provenance. `research-versions.json` records manifest contents plus selected-model/forecast identity metadata without running them. `database-verification.json` records live configuration identities/parameters and fingerprints of reviewed table projections.

- Police research observations: source hash + indicator + geography + period basis + period. Eight of 504 observations are unavailable/suppressed; present period slots must not disappear or become zero.
- Forensic, ASSIST, treatment and naloxone: source-specific indicator and sample/activity definitions remain part of identity. Similar category names do not establish equivalence.
- Enhanced/diagnostic results: observation ID + method + window. Repeated source observations across methods are legitimate. Current observation IDs are snapshot-scoped; they do not include every future source-version dimension.
- Forecast: selected naive model, origin **2025 Q4**, target **2026 Q1**, horizon **one quarter**. Backtests identify model + origin + target + horizon; execution/issuance timestamps are not historical availability dates.
- Published rates: **22** original NRS five-year age-standardised rates, Inverclyde and Scotland, windows **2010–2014 through 2020–2024**, per 100,000 using the **2013 European Standard Population**, with original 95% intervals and source cells. Rates are not recalculated or used to back-solve population.
- All **15** annual local population-rate rows retain unavailable population/rate values. Board population data are not substituted for council denominators.
- Phase 9 is hashed and inventoried for preservation only. It remains outside the approved API and screens.

## Contract migration risks

| Risk | Required treatment before migration |
|---|---|
| Model and evidence identities | Separate observations, method/window results, metric evaluation scopes, runs and cross-source pairs. Preserve source-version identity. |
| Missing values | Preserve suppressed, unavailable, insufficient-history and genuine zero states; never blanket-fill. |
| Irregular study periods | Keep ASSIST source labels/order and nullable exact dates. Exact-date filters currently exclude such records. |
| Geographic compatibility | Police divisions, councils, boards, country totals and samples remain distinct. Application IDs are not official polygon codes. |
| Category overlap | Preserve source labels, exclusions and endpoints. No lexical category merges or sums of overlapping substance involvement. |
| Published rates | Separate rate family; preserve standard population, windows, intervals, vintage and original definitions. Local/national benchmarks are not same-boundary peer rankings. |
| Signed/model-specific statistics | Do not apply nonnegative-count rules to EWMA/CUSUM statistics; preserve method, baseline, window and limits. |
| Forecast alignment | Preserve origin, target, horizon, training/evaluation scope and issuance timestamp separately. |
| Complete pagination | Exports and ordinary endpoints are bounded. Compare total/returned count and version/hash across pages; default signal-only responses are not full history. |
| Changing artifacts | Pin analytical version and checksum. Reject mixed-version page collections. Metadata-only decoration must not silently revise source meaning. |
| Heterogeneous API rows | Envelope consistency does not imply one typed observation schema; missing units cannot be guessed. |
| Registry dependencies | Registry derives from six artifact families; bootstrap failures must remain visible. No fallback geographic evidence. |
| Legacy processing/import lineage | Hard-coded historical computation paths and incompletely recorded import generation require separate reproducibility work, not execution during migration. |

## Unresolved verification gaps

1. Current deployed primary/foreign keys, unique/check constraints, indexes, full SQL types and policy expressions cannot be confirmed with the available metadata access. Successful SELECT is narrower evidence.
2. Eight expected tables have not been confirmed deployed. Proposed SQL and earlier review documents are historical/design evidence only.
3. Seven source-import URLs are blank. Historical documentation cannot supply verified publication links automatically.
4. The three legacy XLS files were not fully parsed in this baseline; their bytes are preserved. No new reader was installed.
5. No verified geometry/crosswalk, Greenock mortality series or compatible annual local denominators are integrated.
6. In-process contract verification does not prove remote deployment parity or availability. Browser checks cover the local application/preview setup.
7. Checksums prove preservation, not the validity of original denominator construction or all historical extraction decisions.

## Proposed first adapter migration

Start with **Phase 4 `mortality_trends`**, currently admitted through `/api/v1/exports?resource=mortality_trends&format=json` and relevant geographic routes. Do not start by changing `/mortality/quarterly`, which reads the separate national database projection.

This resource has 504 observations, one count measure, regular quarters, explicit provenance and two distinguishable geographic boundary types. Its eight suppressed values provide a useful missingness acceptance case. It is exercised by Mortality Analytics, Comparison Studio and Geographic Explorer, so existing regression coverage can detect changes across screens.

A future additive adapter should preserve every original value, source label, quarter, adjustment definition and provenance field; expose version-scoped identities; and preserve exact source/boundary compatibility. Acceptance requires unchanged value/identity baselines, complete pagination, explicit missingness, no unsupported rates, and the existing regression suite. No replacement of old contracts should occur as part of the first adapter step.

**Stop point:** Task 08B establishes evidence only. Implementing that adapter requires explicit approval.

## Reproducing baseline inspection

The documentation-only scripts use the existing analysis environment. `capture_baseline.py` writes only this directory but overwrites this directory's named capture files; preserve this snapshot before intentionally creating a later baseline. `verify_database.py` performs only approved table SELECTs and a read-only advertised metadata request, never writes to Supabase and never records credentials/project URLs/raw error bodies. `render_inventory.py` renders documentation and explicit identity checks. `capture_baseline.py --verify` compares the protected file set against the captured snapshot.

Test/build commands and results are recorded separately. Their generated build, browser and scratch artifacts are not research-baseline inputs. Do not run analytical pipeline entrypoints to reproduce this documentation.
