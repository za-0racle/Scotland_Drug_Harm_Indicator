# Task 08D — controlled frontend adapter migration

Migrated exactly one consumer: **Geographic Explorer's police-mortality source feed**. Existing screens, source values, chart preparation, rendering and export formats are preserved. No backend contract, research artifact, database permission, model or Phase 9 integration changed.

## 1. Selected consumer and justification

The selection was documented before implementation in [SELECTION.md](baselines/task08d/SELECTION.md). `geographicSource(api, 'police', registry)` is a sufficiently isolated integration point with existing unit/browser coverage. It feeds Geographic Explorer's police history, rankings, profile and coverage, all within that one screen.

Inspection identified the legacy `completeMortality` helper as the shared source loader for Mortality Analytics, Comparison Studio's police source and previously Geographic Explorer. Only the Geographic Explorer branch now calls the new collector. Overview retains its database quarterly endpoint. Existing geographic peer comparisons retain their same-boundary endpoint and compatibility logic. Generic source exploration, other source families and legacy/prototype code are not migrated.

The Task 08A audit was supplied in the conversation; its findings about heterogeneous contracts and repeated adaptation motivated this isolated change. Task 08B and Task 08C evidence remains immutable.

## 2. Files added or modified

New application/test files:

- `src/api/mortality-collector.js`: complete versioned retrieval, strict source-specific client validation and deterministic identity checks.
- `src/platform/mortality-adapter.js`: separate lossless mapping into the existing presentation model.
- `tests/mortality-adapter.test.js`: eight focused test groups for retrieval, baseline mapping, missingness, export/visualisation compatibility, rollback and failures.
- `e2e/mortality-adapter.spec.js`: three browser scenarios for the real migrated route, exact exports, mobile keyboard behaviour, failure/retry and consumer/lifecycle isolation.

Existing application files changed:

- `src/api/client.js`: a narrowly scoped response-shape branch for the analytical mortality route and continuation-token query support. Legacy envelope validation remains unchanged.
- `src/platform/geography-data.js`: isolated police-source selection and explicit rollback constant/override.

Added this report and `docs/baselines/task08d/` evidence. No chart renderer, screen markup, CSS, shared mortality loader, Comparison Studio module or backend implementation changed. Pre-existing changes from earlier tasks were left alone.

## 3. Shared collector architecture

```text
existing API transport
  → /analytical/v1/mortality-trends (pinned complete retrieval)
  → validated source-aware collection
  → mortalityPresentation (lossless mapping)
  → Geographic Explorer's existing validation, filters, charts and exports
```

The collector defaults to 100 records per page, so the current 504-slot collection uses six requests. Every continuation includes the first response's `collection_token` as `expected_collection`. It verifies declared ordering, exact expected offset, requested limit, returned-array length, total, next offset and completeness flags. No-progress, overlapping, duplicate or truncated collections are rejected. Nothing is returned to the consumer until retrieval and validation finish.

Source, indicator, research and artifact metadata must remain identical across pages, including source SHA-256, artifact SHA-256 and analytical version. Tokens are validated and pinned as opaque server-generated collection identities; the browser does not recompute the server's full-content Python JSON token. Observation identities and application geographic IDs are independently recomputed with Web Crypto SHA-256. This distinction avoids incorrectly treating JavaScript/Python floating-number JSON formatting as interchangeable.

No second storage system, chart selector, statistical calculation or additional resource adapter was introduced.

## 4. Contract validation behaviour

The collector admits only `mortality-trends/1.0.0`, `suspected_deaths`, count units, the original legacy ten-day-adjusted calendar-quarter basis and country/police-division boundaries. It validates exact required field sets, source dates/provenance, artifact identity, quarter labels/ordering/provided dates, nonnegative integer counts and count/availability consistency.

Metadata mismatches, unsupported versions, malformed identities, invalid boundaries, duplicate slots and nonfinite descriptive values cause an error. Missing or suppressed values remain null. The combined source status `missing_or_suppressed` is retained without inventing separate reasons. Source labels, publication qualifications, existing descriptive context and source cutoff remain unchanged.

The mapping preserves the original 40 fields and existing API geographic decoration, including original property order for existing JSON/CSV exports. New observation IDs, contract/source versions and explicit availability are retained in the collection and through each row's non-enumerable `analyticalIdentity` property. They are not inserted as new fields into previously published export records. Original `source_sha256`, `quality_status` and reporting qualification remain ordinary presentation fields as before.

Web Crypto requires a secure browser context. If unavailable, the source fails explicitly; there is no weaker validation or automatic legacy fallback.

## 5. Baseline equivalence results

Fixtures under `docs/baselines/task08d/` were captured read-only from the unchanged backend. Before saving, the legacy response was checked against the immutable Task 08B ordered response fingerprint and exact artifact metadata. `fixture-verification.json` records that baseline fingerprint and fixture file hashes. The original CSV SHA-256 is independently checked by the frontend test.

The mapped frontend records are compared field-for-field against that baseline-verified legacy fixture, not only against another client transformation of the same contract.

| Invariant | Result |
|---|---|
| Eligible source slots | All **504**, in original artifact order |
| Numerical values and all record fields | Equal to baseline-verified legacy records |
| Unavailable observations | All **eight** retained as null with original status |
| Genuine zero semantics | Synthetic zero fixture retained; baseline itself has no observed zero police values |
| Geography and periods | Original labels, API IDs, boundaries, year/quarter, ordinal and provided dates preserved |
| Source/artifact provenance | Original metadata and source fields preserved |
| Rankings/profiles | Existing functions produce equivalent results |
| Chart periods/gaps | Existing `prepareChart` output matches the legacy records, including unavailable values |

The selected Argyll and West Dunbartonshire series contains one of the eight unavailable values; the other unavailable observations remain in their actual source areas. No unavailable value is assigned to a different geography.

These are preservation/equivalence checks, not independent scientific validation of the original observations or analytical methods.

## 6. User-facing behaviour comparison

Controls, labels, source definitions, ranking eligibility, zero-based charts, missing-data gaps, area profiles, same-boundary comparisons, coverage search and export buttons retain their existing behaviour. The police history is now loaded through the versioned endpoint, with no partial history exposed while it loads.

The browser tests verify 13 police peers, reporting-period changes, all 36 selected-area quarters, mobile containment, profile Escape/focus restoration, refresh and navigation away during delayed requests. Existing screen lifecycle checks prevent late Geographic Explorer results from replacing Mortality Analytics.

An initial new browser assertion checked width immediately after changing viewport size, before Chart.js completed its existing resize lifecycle. The assertion now polls for settled layout and uses reduced motion. No layout code changed. Its final focused run passed all three scenarios.

## 7. Export equivalence results

- Unit tests compare CSV strings and formatted JSON strings exactly for the same selected-area records, metadata and filters.
- The browser downloads real police history JSON and compares all 36 records against the baseline-verified legacy area series.
- The browser downloads CSV and compares it byte-for-byte as UTF-8 text against `mortalityCsv` applied to those same legacy records and export metadata.
- Current API pagination and visible table pagination do not limit eligible export history.
- New identity sidecars do not change the exported `original_record` field or historical metadata structure. No identity/source information from the original export is removed.

## 8. Failure and rollback tests

Tested failure cases include backend unavailability, unsupported version, required metadata missing, invalid provenance, changed source version/artifact version/token, offset/next/count mismatch, partial retrieval, repeated identities/slots, invalid quarters/boundaries and invalid count/availability combinations. A selected failed police source has no summary/history export and shows its explicit error; independent registered evidence remains usable.

Rollback is explicit: change `geographicPoliceContract` in `src/platform/geography-data.js` from `'v1'` to `'legacy'`, rebuild and rerun regression checks. Tests also exercise the explicit `policeContract:'legacy'` loader override. No UI flag or automatic retry against the old endpoint was added.

Unit and browser tests confirm invalid analytical responses do **not** trigger the old mortality export. Mortality Analytics still calls its old export normally. Refresh retries the currently selected implementation, not a fallback.

## 9. Full regression outcomes

Current-run logs are under `docs/baselines/task08d/`.

| Check | Final result | Evidence |
|---|---|---|
| Full frontend suite | **91 passed, 0 failed** | `frontend-tests.txt` |
| Full backend suite | **49 passed, 0 failed**, 209.00 seconds | `backend-tests.txt` |
| Full browser suite | **38 passed, 0 failed**, 3.3 minutes | `browser-tests.txt` |
| Focused migration browser suite | **3 passed**, final focused run | `browser-focused-final.txt` |
| Production build | **Passed**, 31 modules | `build.txt` |
| Source/research manifest verification | **85/85 matched** | `preservation-verification.json` |
| Prior-task evidence and adapter preservation | **42/42 unchanged** | `preservation-verification.json` |

The existing backend TestClient dependency deprecation warning remains; no dependency was changed to suppress it. The full browser run includes all previous 35 cases and the three new migration cases. A mobile police screenshot was captured at `test-results/task08d-police-mobile.png`; existing screenshot checks also ran. Generated screenshots are not frozen research artifacts.

Commands:

```powershell
npm test
npm run build
.\analysis\.venv\Scripts\python.exe -B -m pytest backend/tests -q -p no:cacheprovider
$env:E2E_LOCAL_PORT='55173'
npx playwright test --config playwright.overview.config.js
.\analysis\.venv\Scripts\python.exe -B docs/baselines/task08d/verify_preservation.py
```

No dependencies were installed. Existing Windows process access was used for Node/build/browser commands. Local browser/ASGI checks do not establish remote deployment parity, comprehensive accessibility certification or external scientific validation.

## 10. Preservation verification

See [preservation-verification.json](baselines/task08d/preservation-verification.json).

- **85/85** original source/research manifest checks match.
- **42** prior-task evidence/adapter files match their start-of-task hashes, including all Task 08B/08C baseline documents and the versioned backend implementation/tests.
- Relative to Task 08B's 293-file snapshot, **290** files remain unchanged. The three differences are the already-authorised Task 08C `backend/main.py` integration and this task's two frontend integration files. The backend integration itself is unchanged during Task 08D.
- No source datasets, frozen research artifacts, model/processing files, database/schema/policy files or dependency files changed.
- Build output, browser screenshots, bytecode and test scratch are excluded from frozen research comparisons.

## 11. Remaining limitations

- Only Geographic Explorer's police feed is migrated. Other screens and geographic peer-comparison retrieval retain legacy endpoints intentionally.
- The browser pins the server's full-content token and verifies identities/metadata/pagination; it does not independently reproduce Python's full floating-number content encoding. Server artifact validation and baseline equivalence remain separate safeguards.
- New analytical identities are retained in memory rather than added to old export formats. Exporting the new contract itself would require a separately approved format change.
- Runtime validation cannot establish source collection accuracy, prospective warning validity, compatible denominators or official geographic geometry.
- The registry still depends on existing source families. The new collector does not supply fallback geography or infer outcomes for Greenock.
- Additional source families have different reporting and missingness contracts; this implementation is not a generic cross-source merger.

## 12. Recommendation

The controlled migration demonstrates that one shared collector and a small lossless mapper can preserve existing presentation behaviour. Review Task 08D before authorising another consumer or resource family. No additional family is declared ready solely because this police contract passes; its source-specific contract and independent baseline must be reviewed first.

Work stops after Task 08D. No further migration or analytical screen was started.
