# Task 08H — Shared integrity primitives

## 1. Outcome

Task 08H extracted only the genuinely source-neutral integrity helpers shared by the police mortality and forensic toxicology pipelines. Source-specific validators, schemas, identities, pagination, presentation adapters, route behavior, and rollback switches remain separate.

Pre-change and post-change evidence matches for both contracts. The exact analytical responses, collection tokens, canonical payloads, observation/category identities, page sequences, frontend presentations, and established CSV exports were preserved. No Task 08I work was started.

## 2. Helpers and import relationships

### Backend

Added [analytical_integrity.py](../backend/services/analytical_integrity.py):

- `fingerprint(value)` retains Python's original `json.dumps` settings: sorted object keys, direct Unicode (`ensure_ascii=False`), compact separators, and rejection of non-finite numbers. The serialized string is UTF-8 encoded and SHA-256 is returned as lowercase hexadecimal.
- `relative_path(path)` retains the original provenance-path acceptance and `ValueError` behavior.

The mortality and forensic backend adapters now import these helpers from the neutral module, rather than forensic importing them from the mortality adapter. Existing mortality-module helper imports remain compatible; a focused test verifies those names still refer to the same functions.

### Frontend

Added [analytical-integrity.js](../src/api/analytical-integrity.js):

- `stableJson(value)` retains recursive sorted-key serialization.
- `sha256Canonical(value)` hashes the UTF-8 bytes of `stableJson(value)`.
- `sha256Text(value)` hashes UTF-8 text bytes.
- `sha256Bytes(value)` hashes the supplied `Uint8Array` bytes without text conversion.

The three hash paths remain distinct and Web Crypto remains fail-closed. Raw hashing rejects values outside its explicit text/byte input types. The mortality collector continues to re-export `stableJson` for compatibility; the forensic collector now imports it from the neutral module.

### Serialization semantics remain runtime-specific

Python and JavaScript canonical serialization were verified independently and are deliberately not treated as interchangeable. Both sort object keys and encode Unicode directly as UTF-8. Their number formatting remains the language's original behavior: Python preserves distinctions such as `1` versus `1.0`, `-0.0`, and `1e-07`; JavaScript JSON-number formatting emits `1`, `0`, and `1e-7` for corresponding values. The shared `{ "a": 1, "b": 2 }` test vector hashes to `43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777` in each runtime.

The previous Python failure was isolated to an incorrect expected digest in the newly added edge-case test. Direct evaluation with the unchanged Python serializer produced `9c60901103a20f1b621c74c159467255ada2f0bb237323de81293767ee91b1c8`; the test vector was corrected, not an immutable baseline or analytical fingerprint.

The existing relative-path rules are also retained, including acceptance of `''`, `a/./b`, and `a//b`, and rejection of absolute paths, backslashes, colons, `..` path components, and non-strings.

## 3. Files added or modified

### Application and test files

- Added `backend/services/analytical_integrity.py`.
- Added `src/api/analytical-integrity.js`.
- Updated `backend/services/mortality_adapter.py` and `backend/services/forensic_adapter.py` to use the neutral Python helpers.
- Updated `src/api/mortality-collector.js` and `src/api/forensic-collector.js` to use the neutral JavaScript helpers, retaining the mortality `stableJson` re-export.
- Added `backend/tests/test_analytical_integrity.py` and `tests/analytical-integrity.test.js`.

### New Task 08H evidence under `docs/baselines/task08h/`

- `capture-summary.json`
- `capture_frontend_baseline.mjs`
- `capture_integrity_baseline.py`
- `capture_mortality_export.mjs`
- `capture_prior_evidence.py`
- `forensic-canonical-payload.json`
- `forensic-identities.json`
- `forensic-pages-73.jsonl`
- `forensic-response-1000.json`
- `frontend-baseline-summary.json`
- `mortality-canonical-payload.json`
- `mortality-export-summary.json`
- `mortality-identities.json`
- `mortality-legacy-export.csv`
- `mortality-pages-73.jsonl`
- `mortality-response-1000.json`
- `prior-evidence-before.json`
- `verification-summary.json`
- `verify_frontend_integrity.mjs`
- `verify_integrity_equivalence.py`

Also added this report at `docs/TASK08H_SHARED_INTEGRITY_REPORT.md`.

## 4. Independent pre-change and post-change equivalence

Pre-change live response bytes, serialized token payloads, identity lists, and limit-73 page sequences were captured separately in Task 08H evidence. Post-change verification compared the running API against those captures and the independent Task 08D/08F immutable fixtures.

| Contract | Observations | Null / zero states | Categories | Response bytes SHA-256 | Collection token | Pages at limit 73 |
|---|---:|---|---:|---|---|---:|
| Police mortality | 504 | 8 nulls | N/A | `d009d6e923f6f2665045af2d52f24f44dcc794cd20baab6c2217f0eb384796e7` | `f8dfefd52958a19e275bf1e055aa5e0b2b3f540afa6a392687c759a79373568f` | 7 |
| Forensic toxicology | 210 | 0 nulls; 1 genuine zero | 7 category identities | `523115258783c0fff72d9a75d4f8a813c69dcd60739feb3364374b780bf25d7b` | `e195aa5753ca3b6c047109eab9ea83b39554a185fb968748771df96b442c3722` | 3 |

Both post-change routes matched their captured complete response bytes and canonical payload bytes. All 504 mortality and 210 forensic observation identities matched in original order; all seven forensic category identities matched. The complete paginated response sequences also matched byte-for-byte, with unchanged offsets, returned counts, tokens, and page totals.

The frozen source/artifact hashes agree with prior evidence: forensic source `ccba2a3158b69e38194cafb415dba8834cf080c9174721299977037c4a8bb0df`, forensic artifact `6a67e3f4c964c00d49ca260955141dc7ab1d83c63fccde3711fdfeedd3ef6063`, and mortality artifact `efab0ed13958aba94b647ace3a771dfef2605e58ec47c8de4d1cd1bf92f3be75`.

## 5. Frontend and export equivalence

The independent frontend verification used the immutable Task 08D and Task 08F response fixtures and legacy records. Mortality and forensic presentation records and metadata matched their prior values. The 8 mortality nulls, the single forensic zero, all identities, and all seven forensic category identities were preserved.

Both established CSV exports matched byte-for-byte:

- Mortality selected-area CSV: SHA-256 `ebb982939b748578caec331bd3edf3849e8e0867202e594c4b86d69deb655174`.
- Forensic Substance Intelligence CSV: SHA-256 `ee91fd04a1f8caf0963053cc2eb16b7f6cec576daaccccb669fc0af72e2bc1f7` (629,860 bytes), also matching the immutable Task 08F screen export.

Frontend adapter tests additionally cover the established selected-area JSON and CSV exports. No row shape, export field, value, or consumer behavior was changed.

## 6. Validation results

- Focused Python integrity and adapter tests: **64 passed**.
- Full backend suite: **83 passed**, with one Starlette/httpx deprecation warning from the test client.
- Focused JavaScript integrity and adapter tests: **23 passed**.
- Full frontend unit suite: **106 passed**.
- Full Playwright browser suite: **40 passed**.
- Production build (`npm run build`): **passed**.
- Post-change API/evidence verifier: exact response, fixture, canonical payload, collection token, identity, category identity, and pagination comparisons passed for both contracts.
- Post-change frontend verifier: presentation, identity, null/zero, and both CSV checks passed.
- Source/research manifest verification: **85/85 passed**.
- Task 08B–08G preservation snapshot: **72/72 files matched**.
- Frozen source/artifact checks: **3/3 matched**.

The test client emitted the noted deprecation warning; no test failed. The initial local attempt to run Python tests lacked `pytest` and the backend requirements in the active interpreter. The existing test runner and `backend/requirements.txt` dependencies were installed into the user Python environment, without changing project manifests.

## 7. Preservation and scope

No pagination logic was refactored. No API route, response schema, analytical contract, identity algorithm, data source, artifact, database, model, dependency manifest, or frontend consumer was changed. No Task 08B–08G baseline was overwritten. All 85 source/research manifest hashes and the prior 72-file evidence snapshot passed after extraction.

The report itself is new Task 08H documentation and is not included in the pre-existing Task 08B–08G snapshot. The verification script was run in read-only mode after report creation, so the captured Task 08H verification evidence was not overwritten.

## 8. Remaining duplication and recommendation

Pagination orchestration, page-window validation, metadata pinning, domain completeness checks, provenance chains, identity generation, and presentation mapping remain source-specific and unchanged. This task does not establish that their semantics are sufficiently identical for extraction.

The limited integrity extraction resolves the cross-source utility ownership concern identified in Task 08G. Do not proceed to pagination consolidation as part of this task. If separately approved, prototype only the invariant transport/window mechanics with both source validators and completion criteria left outside the shared helper; require the full dual-contract regression and preservation checks again.

## 9. Limitations

- Python and JavaScript canonical number representations differ by design; the helpers preserve each runtime's existing bytes rather than defining a cross-language canonical-number standard.
- Python's relative-path helper preserves prior syntax exactly, including some unusual accepted relative forms. Tightening those rules would be a behavior change and is out of scope.
- Browser hashing still requires Web Crypto; it fails closed where unavailable.
- Passing equivalence and preservation checks demonstrates software compatibility with the captured evidence, not independent validation of source data or statistical methodology.
