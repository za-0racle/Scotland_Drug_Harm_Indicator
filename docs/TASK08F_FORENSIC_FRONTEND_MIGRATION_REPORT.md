# Task 08F — controlled forensic frontend migration

Migrated exactly one forensic consumer: the forensic source feed in Substance Intelligence. It now uses the Task 08E versioned contract. The screen's existing presentation and export formats are retained; other screens and source families remain on their prior loaders.

## 1. Selected consumer and scope

The pre-implementation selection is recorded in [SELECTION.md](baselines/task08f/SELECTION.md). Substance Intelligence was suitable because its forensic source is selected through a single isolated loader. The migration redirects only that branch.

The Overview forensic preview still uses the legacy endpoint, as do the existing comparison and Geographic Explorer forensic sources. Browser coverage confirms the Overview request remains legacy while Substance Intelligence uses the analytical route. ASSIST and treatment also retain their legacy behavior. No other consumer was migrated.

## 2. Files created or modified

Application changes:

- `src/api/forensic-collector.js` — source-specific contract validation, identity checks, pinned pagination and complete-collection verification.
- `src/platform/forensic-adapter.js` — lossless mapping into the existing Substance Intelligence record shape.
- `src/platform/substance.js` — forensic-only route selection and explicit rollback setting.
- `src/api/client.js` — recognizes the analytical forensic response shape and permits the collection-token query parameter only on analytical routes.

Tests and evidence:

- `tests/forensic-adapter.test.js` and `e2e/forensic-migration.spec.js`.
- `docs/baselines/task08f/` — pre-migration legacy and analytical response fixtures, presentation and export captures, selection, and preservation hashes. `capture_screen_export_baseline.mjs` and the screen-export CSV/summary are additional screen-level export evidence captured without overwriting prior baselines.
- This report.

No mortality adapter or contract code, backend route, data artifact, statistical result, database policy, dependency, or unrelated frontend consumer was changed.

## 3. Collector and presentation adapter

The selected source requests `GET /api/v1/analytical/v1/forensic-toxicology`. The collector validates the contract version and exact reviewed source/artifact identities before mapping any rows. It pins the first page's collection token, sends it on continuation requests, verifies offsets, record counts, metadata consistency, ordering and uniqueness, and rejects incomplete collections. Nothing is exposed to the screen until all pages have been validated.

Observation and category IDs are independently checked using SHA-256. Ordering follows the artifact's category blocks and quarter order. The mapper preserves the original 210-row presentation order, existing row fields and metadata, and attaches the new identity to each row as a non-enumerable `analyticalIdentity`. Contract data remains available on the loaded result; established JSON and CSV records do not gain fields.

## 4. Scientific safeguards and verified definitions

The immutable Task 08B / Task 08E evidence identifies the source as Public Health Scotland's RADAR forensic source, with SHA-256 `ccba2a3158b69e38194cafb415dba8834cf080c9174721299977037c4a8bb0df`. The Phase 4 artifact is `phase4-1.0.0`, SHA-256 `6a67e3f4c964c00d49ca260955141dc7ab1d83c63fccde3711fdfeedd3ef6063`.

The source reports `Number`; the artifact unit is `detection_count` and the reporting basis is `calendar_quarter`. The verified values are nonnegative integer counts. The collection has 210 observations: seven exact source labels over 30 quarters, Q4 2018 through Q1 2026. One value is a genuine observed zero; there are no null observations in this vintage.

The exact category labels are **All Benzodiazepines**, **Prescribable Benzodiazepines**, **Street Benzodiazepines**, **Dissociatives**, **Gabapentinoids**, **Opioids**, and **Stimulants**. Categories remain source-label-only, overlapping, and non-additive. The source does not provide detailed chemical inclusion definitions, a sample/testing definition, or a denominator; the adapter preserves these as unknown/null rather than inventing them.

The screen continues to explain that detections are not confirmed causes of death or unique people, overlapping categories must not be summed, and population prevalence cannot be calculated. Existing descriptive fields are carried through, not recalculated.

## 5. Baseline equivalence

The captured Task 08F legacy response matches the immutable Task 08E ordered-response fingerprint and the Task 08B comparisons. Tests compare the mapped records and metadata to the baseline-verified legacy response—not merely to another transformation of the current analytical response.

| Invariant | Result |
|---|---|
| Completeness and ordering | All 210 observations, in original presentation order |
| Values, zero and missingness | Exact values; one zero and zero nulls preserved |
| Categories and periods | All seven exact labels and all 30 quarters |
| Measure, units and provenance | Original descriptive fields, `detection_count`, source and artifact metadata preserved |
| Chart and heatmap | Chart series/gaps and all heatmap cells match captured pre-migration results |
| Rankings and profiles | Ranking results and all seven category profiles match |
| JSON representation | `JSON.stringify` of the mapped legacy data/metadata matches the pre-migration representation |
| CSV export | Downloaded screen CSV is byte-identical to the screen-format baseline replayed from the immutable pre-migration response through the existing exporter and full screen filters: 629,860 bytes; SHA-256 `ee91fd04a1f8caf0963053cc2eb16b7f6cec576daaccccb669fc0af72e2bc1f7` |

An earlier independently captured presentation CSV with its original filter scope is also compared byte-for-byte. Substance Intelligence did not previously provide a JSON export button. No new JSON export or changed export fields were introduced; JSON equivalence here refers to the existing API/presentation record representation.

## 6. Pagination, failure handling and rollback

Collector tests cover page sizes 1, 73 and 1,000; token changes; missing or overlapping pages; duplicate identities; incomplete counts; and backend failure. Contract tests reject unsupported versions, altered source/artifact identities, invalid quarters, category definitions, units, provenance, availability, negative/nonfinite values and inconsistent null states.

The browser tests verify that an unavailable analytical endpoint leaves the source in an explicit error state, exposes no partial observations, and recovers after retry. It never falls back automatically. The rollback setting is `substanceForensicContract` in `src/platform/substance.js`: selecting `'legacy'` restores the previous forensic resource explicitly. Unit coverage confirms that rollback makes a legacy request and that a failed analytical request makes no such request.

Identity verification requires browser Web Crypto in a secure context; if unavailable, the source fails closed.

## 7. Regression results

- Focused forensic adapter tests: **10 passed**.
- Full frontend unit suite (`npm test`): **101 passed**.
- Full backend suite: **66 passed**, with one existing Starlette/httpx deprecation warning.
- Full browser suite: **40 passed** on the clean rerun.
- Focused forensic browser scenarios: **2 passed**.
- Production build (`npm run build`): **passed**.

The first full browser run had one transient initial Overview/Supabase connectivity failure while the backend suite was running concurrently. The acceptance test passed when rerun alone, and the complete browser suite then passed 40/40 without concurrent backend testing.

The existing Geographic Explorer police-feed tests passed in the full unit and browser suites; its migrated mortality feed was not changed.

## 8. Preservation verification

All **85/85** source/research manifest hashes match. The Task 08E source and artifact file hashes match the frozen baseline. The Task 08F legacy/analytical fixtures, screen-export bytes and Task 08E ordered-response fingerprint also verify against their recorded summaries.

The 153-file pre-implementation Task 08F snapshot differs only at `src/api/client.js` and `src/platform/substance.js`, the two existing application files intentionally modified for this task. The Task 08D preservation snapshot's later differences are the Task 08E backend route registration and its OpenAPI test update; the Task 08E snapshot additionally reflects these Task 08F frontend edits. No frozen source, Phase 4 artifact, or source/research manifest changed.

## 9. Known limitations

- The source supplies labels but not chemical inclusion criteria, sample/testing details, or sample denominators.
- The source publication date is unknown; the captured data cutoff is 2026-03-31. These historical data are not live surveillance.
- The client intentionally pins the reviewed source hash, artifact hash/version and 210-observation collection. A new source or artifact vintage will be unavailable until separately reviewed and the pins/baselines are updated.
- Other forensic consumers remain on the legacy resource by design; this task changes exactly one consumer.

## 10. Recommendation

Stop for review as requested. After approval, treat any next consumer as a separate controlled migration with its own selection, baseline, source-specific safeguards and export/presentation equivalence checks.
