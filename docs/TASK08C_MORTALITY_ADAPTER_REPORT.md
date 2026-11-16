# Task 08C — first versioned mortality analytical adapter

Implemented an additive, source-aware contract for the existing Phase 4 `mortality_trends` resource. Existing frontend consumers, database reads, artifact exports and old routes retain their contracts. No source cleaning, database changes, model fitting, statistical recalculation, rates, totals, new storage or Phase 9 integration were introduced.

## 1. Files added or modified

Added application files:

- `backend/schemas/mortality_v1.py`: strict typed metadata, quarterly observation and pagination models, restricted to this count resource.
- `backend/services/mortality_adapter.py`: verified artifact projection, deterministic observation IDs, lossless descriptive context, pinned pagination and independent complete-collection verification.
- `backend/api/mortality_v1.py`: separate versioned read-only route.
- `backend/tests/test_mortality_adapter.py`: baseline equivalence, invalid input, identity, pagination, checksum and legacy-contract regression tests.

Modified existing application file:

- `backend/main.py`: one router import and one router registration. Existing route implementations are unchanged.

Added documentation/evidence:

- This report.
- `docs/baselines/task08c/`: regression logs, exact example response, added OpenAPI schemas, preservation verifier/results and checksums of the immutable Task 08B documentation.

Pre-existing changes to `.env.example`, root `README.md`, `docs/TASK08_GEOGRAPHY_REPORT.md` and untracked `vercel.json` were left alone. Task 08B evidence was not recaptured or overwritten.

## 2. Versioned contract specification

Contract version: **`mortality-trends/1.0.0`**.

| Structure | Contents |
|---|---|
| `source` | Original filename ID, content-hash source version, original source path/URL, publication date/status and cutoff |
| `indicator` | Suspected-death identity, explanatory definition, count unit, original period basis and reporting qualification, scientific status and existing descriptive-method metadata |
| `artifact` | Existing resource, analytical version, SHA-256, artifact path, provenance manifest, storage, execution timestamp and limitations |
| `research_metadata` | Original analysis-as-of date and data-age field |
| `observations[]` | Version-scoped observation ID, geographic scope, verified quarterly period, value, availability and existing descriptive context |
| `pagination` | Total, offset, requested limit, returned count, next offset, complete-collection flag, collection token and explicit original-row ordering |

Metadata shared by the collection appears separately rather than being repeated in every observation. The artifact's 40 original fields can be reconstructed losslessly from these structures. Existing derived values are carried as `research_context`; the adapter does not calculate them.

The explanatory `indicator.definition` is adapter documentation, not a fabricated verbatim source field. `original_reporting_qualification` preserves the artifact's original limitation text exactly. The actual source contains no independent `reporting_definition` column, so none is claimed.

The source ID remains the existing workbook filename, not an invented database foreign key. `source_version` is that source's recorded SHA-256, not an inferred publication edition number. Geographic IDs reuse existing application scope identifiers; neither official geographic codes nor polygons are introduced.

Strict models reject coercion, unknown fields, invalid quarter labels/order/dates, unsupported boundary types, negative/fractional/boolean counts, nonfinite descriptive values, inconsistent availability, incomplete provenance and inconsistent shared metadata. Provided quarter dates are validated, not generated into output. Invalid artifacts return the existing safe HTTP 503 unavailable envelope.

## 3. API route and example response

**GET `/api/v1/analytical/v1/mortality-trends`**

| Parameter | Behaviour |
|---|---|
| `offset` | Default 0; nonnegative; maximum 1,000,000; offsets beyond this collection's total are rejected |
| `limit` | Default 100; range 1–1,000 |
| `expected_collection` | SHA-256 token returned on the first page; mandatory when offset is nonzero |

No analytical filters are introduced in this first contract. Unsupported query parameters are rejected. All observations can be retrieved with `?limit=1000`, or through pinned continuation pages. POST is not supported.

The exact, real one-observation example is [example-response.json](baselines/task08c/example-response.json). The complete typed API addition is [openapi-addition.json](baselines/task08c/openapi-addition.json).

Excerpt from that response, omitting shared metadata and research context for readability:

```json
{
  "contract_version": "mortality-trends/1.0.0",
  "pagination": {
    "total": 504,
    "offset": 0,
    "limit": 1,
    "returned": 1,
    "next_offset": 1,
    "page_is_complete_collection": false,
    "collection_token": "f8dfefd52958a19e275bf1e055aa5e0b2b3f540afa6a392687c759a79373568f",
    "ordering": "original_artifact_row_order"
  },
  "observations": [{
    "observation_id": "mortality-observation:v1:56595b0527830da273e0fdc934e59f784139bd653b128cc65110de0f50bce9aa",
    "geography": {
      "geography_id": "police_division-122fb6ace418",
      "canonical_name": "A: North East",
      "original_name": "A: North East",
      "boundary_type": "police_division"
    },
    "period": {
      "year": 2017,
      "quarter": 1,
      "label": "2017 Q1",
      "ordinal": 8068,
      "period_start": "2017-01-01",
      "period_end": "2017-03-31"
    },
    "value": 18,
    "availability_status": "observed"
  }]
}
```

`/api/v1/mortality/quarterly` and the existing `mortality_trends` export remain unchanged. No current frontend screen calls the new resource.

## 4. Identity algorithm

Observation IDs are `mortality-observation:v1:` followed by full SHA-256 of deterministic UTF-8 JSON with sorted keys, compact separators, Unicode preserved and nonfinite values forbidden.

Identity input contains:

1. Contract version.
2. Exact source ID and source-content SHA-256.
3. Complete indicator definition, including unit, reporting basis and original qualification.
4. Exact original/canonical geographic scope, boundary type and application geographic ID.
5. Validated year/quarter, period label, ordinal and original dates.

Observation values and computed research statistics are not identity dimensions. Changing source bytes, definition, boundary or quarter changes identity. A corrected value within a source version retains slot identity but changes the collection token and artifact checksum. This is deliberately a version-scoped identity, not a universal cross-vintage linkage or official geographic identifier. Contract/definition changes may require new IDs; no automatic equivalence across versions is asserted. Hashes are integrity mechanisms, not signatures or scientific validation.

## 5. Missingness handling

All **504** slots are retained, including **eight** `value=null` observations with `availability_status=missing_or_suppressed`. The source does not establish a separate reason for every unavailable value, so the combined status is preserved exactly.

An observed value must be a nonnegative integer. Missing/unavailable status requires null; observed status requires a value. Genuine zero is accepted and retained, proven with a clearly synthetic validation fixture. The actual baseline has no observed zero mortality values; none were inserted. Missing descriptive references remain null independently of the observed count. National totals remain separate from their constituent divisions.

## 6. Baseline equivalence results

The tests reconstruct the original records entirely from the new contract, then compare them to immutable Task 08B evidence. They do not merely compare two transformations of the current input.

| Comparison | Evidence |
|---|---|
| All 504 slots, original values/nulls, periods, source/geography labels, provenance and descriptive fields | Exact ordered response fingerprint from `task08b/resource-contracts.json` |
| Every existing numerical field | Original numerical-projection fingerprint |
| Original 40-field CSV records | Original string-record fingerprint from `task08b/file-inventory.json` |
| Source/indicator/geography/reporting-basis/period identities | Original identity fingerprint from `task08b/identity-verification.json` |
| Per-field null counts, including all eight unavailable counts | Exact original null-count mapping |
| Artifact version, SHA-256, path, timestamp, manifest and limitations | Exact original metadata comparison |
| Existing export and old API definitions | Old export fingerprint and every pre-existing OpenAPI path definition unchanged |

Existing artifact identity remains `phase4-1.0.0`, SHA-256 `efab0ed13958aba94b647ace3a771dfef2605e58ec47c8de4d1cd1bf92f3be75`. Source SHA-256 remains `587a5d47061f93872b5922dbfe724607a86fe59ee0a6ebe488859b87395cdddf`.

## 7. Pagination verification

Original artifact row order is preserved. Each scope's quarterly ordering is validated. No sort, aggregation or imputation changes the sequence.

The collection token hashes the complete normalized content: contract, source, indicator, artifact metadata, research metadata and all observations. It is independent of page size and offset. A continuation without a token, or with a changed token, returns **409**, instructing the caller to discard pages and restart. Invalid bounds/parameters return **422**.

`collect_pages` independently verifies complete collections and rejects mixed versions, metadata changes, gaps, overlap, duplicate identities, no-progress pages, surplus terminal pages, incomplete totals and altered content. It verifies each observation ID and the final full-content token. It is independently testable and is not wired into existing frontend consumers.

Tests cover page sizes **1, 73 and 1,000**, complete retrieval of all 504 records, the eight unavailable values, stale-token rejection and changed content even when an artificial test repository claims the same artifact identity. No second persistence/cache system is introduced; each request uses the existing checksum-validating artifact repository.

## 8. Test and build outcomes

Current-run evidence is under `docs/baselines/task08c/`.

| Check | Final outcome | Evidence |
|---|---|---|
| Backend suite | **49 passed, 0 failed** (19 existing + 30 adapter cases), 236.11 seconds | `backend-tests.txt` |
| Frontend suite | **83 passed, 0 failed** | `frontend-tests.txt` |
| Full browser suite | **35 passed, 0 failed**, 3.5 minutes | `browser-tests.txt` |
| Production build | **Passed**, 29 modules | `build.txt` |
| Frozen/source manifest checks | **85/85 matched** | `preservation-verification.json` |
| Task 08B evidence preservation | **26/26 files unchanged** | `preservation-verification.json` |

The focused adapter suite also passed 30 cases before the full run. Backend tests report one existing Starlette/httpx TestClient deprecation warning; no dependency was changed to suppress it. Tests cover the new strict route and old endpoint schemas, while the browser suite verifies existing screens continue using their old contracts.

Commands:

```powershell
.\analysis\.venv\Scripts\python.exe -B -m pytest backend/tests -q -p no:cacheprovider
npm test
npm run build
$env:E2E_LOCAL_PORT='55173'
npx playwright test --config playwright.overview.config.js
.\analysis\.venv\Scripts\python.exe -B docs/baselines/task08c/verify_preservation.py
```

Node/build/browser commands use the process access required by the existing Windows environment. The browser run uses the existing production-preview configuration and isolated local proxy port. No dependencies were installed or changed. ASGI tests exercise the new route directly; browser tests exercise unchanged existing frontend consumers. These are local regression checks, not proof of remote deployment parity or scientific external validation.

## 9. Protected-file preservation

The verifier reads Task 08B evidence without writing into its directory. Results are in [preservation-verification.json](baselines/task08c/preservation-verification.json).

- **292/293 existing protected files unchanged**.
- The one existing protected application file changed is the authorised two-line router integration in `backend/main.py`.
- **Four new application/test files**, listed separately above; no new research outputs.
- **26/26 Task 08B evidence files unchanged**, including its historical preservation result.
- **85/85 source/research manifest entries still match**.
- No original sources, frozen research outputs, processing/model code, frontend source/tests, database/schema/policy files or dependency files changed.

Generated builds, ignored screenshots, bytecode and test scratch are not counted as frozen research modifications. Pre-existing user changes are not attributed to this task. File preservation establishes integrity, not scientific correctness.

## 10. Known limitations

- Only the Phase 4 police count resource is adapted; no NRS, toxicology, naloxone, model-statistic, forecast, published-rate or Phase 9 family is migrated.
- Frozen publication vintage and legacy ten-day adjustment qualifications remain in force; the contract does not establish current conditions, resident-only incidence or confirmed registered deaths.
- Application scope IDs are not official boundary codes; divisions are not councils, boards or Greenock. No denominator or geometry is supplied.
- Missing/suppressed reasons remain combined because the source does not provide a verified split.
- The first contract exposes complete history with pagination, without geography/date filters. No current frontend consumer uses it.
- Existing artifact loader caching/integrity behaviour is reused. Collection tokens detect mixed content across requests; they do not make the backing filesystem transactional or establish upstream scientific accuracy.
- Deployed database metadata gaps from Task 08B are unchanged; this adapter does not require or inspect the database.

## 11. Recommended next migration step

After explicit approval, pilot one existing mortality consumer against this versioned contract through a shared client collector while preserving a rollback path to its current endpoint. Verify the same value/identity/null baselines and screen behaviour before considering another resource family. Do not infer cross-source compatibility from a common envelope.

Task 08C stops at this independent backend adapter. No frontend migration or subsequent analytical screen is authorised by this report.
