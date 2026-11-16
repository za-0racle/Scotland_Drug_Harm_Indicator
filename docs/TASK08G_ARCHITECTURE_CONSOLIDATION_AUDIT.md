# Task 08G — analytical adapter consolidation audit

**Scope:** Read-only comparison of the Task 08C/08D police mortality pipeline and the Task 08E/08F forensic pipeline. No application, API, database, frozen evidence, or analytical code was changed.

## 1. Executive summary

Both pipelines correctly keep their source contracts and presentation adapters separate. There is real duplication in complete-page retrieval, page-window checks, metadata pinning, and route query/error handling. A few primitive integrity helpers are already shared, but currently cross-imported from the mortality-specific adapter modules.

The audit recommends **Option B, narrowly scoped**: if approved as a later task, move genuinely source-neutral integrity helpers to neutral modules and consider one pagination coordinator for the common page-window/token mechanics. Keep each source's schema, metadata checks, observation and category identity, ordering/completeness rules, value/availability constraints, and presentation mapper independent. This is a maintainability opportunity, not a reason to create a universal analytical adapter.

No confirmed user-visible correctness defect was found in the reviewed implementations. A repeatable version-pin maintenance burden and cross-source imports from mortality modules are confirmed coupling concerns. The Task 08F initial Supabase/browser failure was not reproducible in the recorded isolated and clean full-suite reruns; its cause remains unresolved.

## 2. Current architecture

### Police mortality

`GET /api/v1/analytical/v1/mortality-trends` is implemented by [mortality_v1.py](../backend/api/mortality_v1.py). It asks [MortalityAdapter](../backend/services/mortality_adapter.py) to load and validate the existing Phase 4 artifact, then returns the mortality-specific schema in [mortality_v1.py](../backend/schemas/mortality_v1.py).

On the frontend, [mortality-collector.js](../src/api/mortality-collector.js) validates and retrieves the complete analytical collection. [mortality-adapter.js](../src/platform/mortality-adapter.js) maps it into Geographic Explorer's existing rows. Only the police branch in [geography-data.js](../src/platform/geography-data.js) selects this route. The separate explicit rollback is source-scoped.

### Forensic toxicology

`GET /api/v1/analytical/v1/forensic-toxicology` is implemented by [forensic_v1.py](../backend/api/forensic_v1.py). [ForensicAdapter](../backend/services/forensic_adapter.py) verifies the Phase 4 artifact against its source and manifest, then constructs the forensic-specific schema in [forensic_v1.py](../backend/schemas/forensic_v1.py).

On the frontend, [forensic-collector.js](../src/api/forensic-collector.js) validates and retrieves the full collection. [forensic-adapter.js](../src/platform/forensic-adapter.js) maps to the Substance Intelligence row shape. Only the forensic feed in [substance.js](../src/platform/substance.js) selects the analytical endpoint; its explicit rollback does not affect other sources.

The shared [API client](../src/api/client.js) provides transport, JSON/error handling, and an allow-listed analytical query parameter. It does not interpret source observations.

## 3. Duplication inventory and consolidation value

| Responsibility | Existing implementation | Assessment and estimated benefit |
|---|---|---|
| Page retrieval and token pinning | Both browser collectors initialize offset/token/total, request pages, pass `expected_collection`, verify declared counts/next offsets/completeness, pin metadata and reject partial collections. Backend `page()` methods independently slice a freshly validated collection and check the continuation token. | Genuine overlap in mechanics. A small page coordinator could remove roughly 15–30 lines per browser collector and reduce drift in generic offset/window checks. It must not own source-specific page validation or completion criteria. |
| Page-completeness verification | Backend `collect_pages()` and `collect_forensic_pages()` independently verify offsets, returned lengths, next offsets, completion flags, mixed-page metadata and duplicate IDs. They are exercised by respective backend tests, not called from the route path. Browser collectors also perform their own online completeness checks. | Similar purpose, not identical semantics: forensic adds category-quarter coverage and both verifiers recompute different content shapes. Share only generic page-window primitives; retain separate final verifiers. |
| Hashing and canonical serialization | Backend forensic already imports `fingerprint()` and `relative_path()` from the mortality service module. Frontend forensic imports `stableJson()` from the mortality collector but has its own Web Crypto `digest()` and `rawDigest()`. | Exact low-level reuse already exists but creates misleading mortality-to-forensic dependencies. A neutral integrity utility is a clear, small cleanup. Estimated benefit is low (roughly 10–20 duplicated lines across both runtimes) but reduces coupling. `rawDigest()` is not interchangeable with canonical-object hashing. |
| Observation identity | Mortality identity uses contract, source ID/hash, indicator definition, geography and quarter; it does not include artifact identity or value. Forensic identity uses contract, complete source identity, artifact version/hash, measure, category definition, indicator, geography and quarter; it also excludes value. | Not duplicate logic in the substitutable sense. The dimensions are scientifically and contractually different. Do not share an identity schema or generator. |
| Metadata and row validation | Both validate exact field sets, source/artifact provenance, dates, units, reporting periods, availability, finite descriptive context and metadata consistency. Forensic additionally validates manifest/raw-source parity, exact categories and full category-quarter coverage; mortality validates police geographic scopes and legacy quarter qualification. | Repeated validation scaffolding, but source-specific predicates dominate and should remain separate. A broad validation framework would add indirection without safely eliminating the domain logic. |
| Error handling | Both routes reject extra query parameters and translate source-specific collection conflicts to HTTP 409 and invalid pagination to 422. Both use the existing artifact error path for unavailable verified artifacts. The browser API client handles transport/schema errors once; collectors provide source-specific validation messages. | Route boilerplate is nearly identical and small (about 5–10 lines potentially shared). Keep route definitions and error classes source-specific unless another contract makes the shared helper worthwhile. |
| Provenance preservation | Mortality relies on the existing repository's artifact verification; forensic additionally hashes its raw source, manifest entry and artifact output and checks source-to-artifact rows. Both expose source/artifact provenance in their own schemas and mapped rows. | Same goal, materially different evidence chain. Do not unify the provenance validator. |
| Presentation mapping | Both mappers enforce complete collections, reconstruct the legacy record shape and attach non-enumerable analytical identity. Their source fields, category representation and row layout differ. | The pattern is similar; the mappings are not losslessly interchangeable. Keep separate. Consolidating might save little while obscuring field semantics. |
| Baseline equivalence tests | Each backend and frontend suite compares against independent Task 08B evidence and preserves source-specific counts, fields, exports and ordering. | Shared test helpers may reduce fixture boilerplate later; the scientific assertions must stay independent. No reduction in required baseline evidence is justified. |
| Rollback | Explicit source-level contract selectors exist for Geographic Explorer police and Substance Intelligence forensic. Failures do not automatically fall back. | Same safety pattern, but each switch belongs at its isolated consumer boundary. A shared global switch risks changing unrelated consumers. |
| Artifact/version pins | Mortality frontend validates source identity shape and page-to-page stability. Forensic frontend deliberately pins reviewed source hash, artifact hash/version/execution vintage, category list and 210-observation scope. Backend validates source/artifact integrity dynamically for both, with extra raw-source checks for forensic. | Different release policies, not accidental mismatch. Forensic pin upkeep is a real maintenance task on a new vintage; relaxing it is not a safe consolidation. |

These are order-of-magnitude source-line estimates, not measured performance or a promise of net code reduction. Tests, source-specific validation and documentation will remain even if shared plumbing is extracted.

## 4. Source-specific scientific rules that must remain separate

### Police mortality

- The measure is provisional originally suspected drug deaths, not NRS registered drug misuse deaths or population-adjusted risk.
- It has 504 source slots and eight unavailable/null observations. Null remains unavailable; no value is imputed.
- Boundaries include country and Police Scotland divisions. Division observations are not councils and cannot be substituted or summed into a different scope.
- Reporting is quarterly with the source's legacy ten-day timing adjustment and original qualifications.
- A slot identity is scoped to source version, indicator, geographic scope and quarter. The value is not part of identity; the collection token captures changed content.
- The immutable Task 08B and Task 08C/08D evidence records the original ordering, values, unavailable states and exports.

### Forensic toxicology

- The measure is source-reported `Number`, represented as `detection_count` per calendar quarter; the verified vintage contains nonnegative integer values.
- It contains 210 observations: seven source categories over 30 quarters, Q4 2018–Q1 2026, including one genuine observed zero and no nulls in this vintage.
- The exact categories include All Benzodiazepines, Prescribable Benzodiazepines and Street Benzodiazepines. They overlap; they are not mutually exclusive and must not be summed as unique deaths or people.
- Category definitions are source-label-only; the source does not establish detailed chemical inclusion definitions.
- The testing/sample definition and denominator are unknown/not supplied. Detection counts do not estimate population prevalence or establish cause of death.
- Forensic observation identity intentionally includes artifact version/hash, full measure definition and category definition. Category identity is separately source-versioned.
- The immutable Task 08B and Task 08E/08F evidence preserves the source/artifact fingerprints, category/quarter slots, zero state and legacy outputs.

These rules live in the source-specific schemas, adapters and test assertions. A common abstraction must not convert categories, units, boundaries, null semantics or identity dimensions into generic defaults.

## 5. Confirmed defects versus maintainability opportunities

### Confirmed defects

No confirmed functional or scientific defect was found in the reviewed two-pipeline implementation. The backend and frontend collectors both reject incomplete or mixed collections; the source-specific tests exercise their identity, provenance, period, availability and pagination failures.

### Confirmed maintainability concerns

1. **Cross-source utility ownership:** forensic code imports generic `fingerprint` and `relative_path` from `backend.services.mortality_adapter`; its browser collector imports `stableJson` from `src/api/mortality-collector.js`. These are generic primitives owned by a source-specific module. This works today but means changing or relocating the mortality module can break forensic code.
2. **Duplicated pagination orchestration:** both browser collectors independently implement the page loop, token pinning, offset/count/next-page checks, metadata stability checks and final completeness check. Similar logic in backend page verifiers can drift. The checks are not fully identical, so consolidation should be limited to invariant mechanics.
3. **Reviewed-vintage client pins:** forensic's exact artifact hash, source hash, execution timestamp, categories and total are repeated as constants in the browser validator. This is deliberately fail-closed, but any reviewed source vintage change requires coordinated code, baseline and test updates. Do not replace these with acceptance of any syntactically valid hash.
4. **Per-request artifact validation cost:** each backend page request rebuilds/validates the full source collection before slicing. This provides a current token and catches changes between pages, but repeats source/artifact reads and hashing for a multi-page retrieval. It is an unmeasured cost, not a demonstrated performance defect. Any future cache/verified-snapshot design would need freshness and token semantics review.
5. **Small duplicated route shell:** route parameter allow-listing and conflict/pagination exception mapping are nearly identical. The volume is small and the error types/source behavior differ, so a shared wrapper may cost more complexity than it saves.

### Not defects by themselves

- Separate schemas and validation branches are necessary, not redundant architecture.
- Different source/artifact pin policies reflect the reviewed-vintage migration scope, not evidence that mortality should adopt forensic pins or vice versa.
- Reconstructing the existing frontend row shape is required for lossless compatibility; the mappings should not be collapsed solely because both return legacy-like rows.
- The shared `client.js` analytical-route branch is narrowly allow-listed and does not perform universal schema validation; each collector remains responsible for its typed contract.

## 6. Consolidation options

| Option | Effort | Scientific integrity | Regression risk | Maintainability | Dissertation relevance |
|---|---|---|---|---|---|
| **A — Retain separate implementations** | Lowest now; future duplicated fixes remain | Highest visibility of source differences | Lowest immediate risk | Current cross-imports and page-loop duplication remain | Strongly defensible if the dissertation prioritizes auditable, source-specific adapters over abstraction |
| **B — Extract limited shared infrastructure** | Low-to-moderate; shared utility and tests plus carefully bounded pagination helper | High if validators, schemas, identities and presentation mappings remain separate | Moderate; common plumbing affects both pipelines and needs dual-source regression coverage | Improves ownership and reduces mechanical drift without hiding domain rules | Recommended: demonstrates deliberate reuse while retaining heterogeneous data semantics |
| **C — Universal analytical adapter** | High; likely requires common schema, plugin/strategy model and broad migrations | Highest risk of flattening source meanings and availability rules | High across both current adapters and consumers | May appear simpler initially, but source-specific switches and extension hooks likely proliferate | Poor fit: weakens the central research argument that source definitions and limitations must remain explicit |

## 7. Recommended approach

Choose **Option B, bounded to mechanical integrity plumbing**, after approval. Do not refactor as part of this audit.

Suggested implementation scope:

1. Add neutral backend and frontend integrity modules for canonical JSON hashing, raw-byte/text hashing where explicitly requested, and safe relative-path validation. Move the current shared implementations there without changing serialization, encodings, error behavior or resulting tokens/IDs. Keep raw-name geographic ID hashing explicit at its source call site.
2. If a dual-pipeline test design demonstrates value, add a small complete-page retrieval coordinator for common mechanics: expected offset, limit, returned length, continuation token consistency, stable shared-metadata callback, next offset and complete flag. Each caller must retain its own schema parser, response metadata signature, row identity validation, order rules, coverage checks, and error type.
3. Leave the backend `collect_pages` and `collect_forensic_pages` domain completeness checks separate, or factor only a tiny page-window predicate if that is clearer after a prototype. Do not move category-quarter verification or mortality identity rules into the shared layer.
4. Keep route functions, Pydantic response models, source validators, presentation adapters, rollback selectors and fixed reviewed-vintage pins separate.
5. Require byte-for-byte unchanged route responses and legacy exports; no API version or response shape changes.

Estimated implementation size: a few dozen lines moved/removed, plus utility and equivalence tests. A larger abstraction should be rejected unless a third genuinely different source contract demonstrates repeated demand.

## 8. Proposed implementation boundaries

**Safe to consider sharing**

- Canonical deterministic object serialization/hash implementation, preserving current Python and JavaScript encodings.
- A generic relative-path validator only if its accepted syntax remains identical.
- Mechanical page-window checks and a token-pinned request loop, parameterized by source-specific parsing/validation rather than a universal response model.
- Test helpers for asserting common pagination invariants, while source-specific fixture expectations remain explicit.

**Must remain source-specific**

- Contract/schema types and version strings.
- Accepted source and artifact identity/vintage policy.
- Measurement definition, unit, value type and null/zero interpretation.
- Source provenance verification chain.
- Geographic boundaries and sample/geography definitions.
- Category identity and overlap/additivity metadata.
- Quarter rules, ordering and complete-coverage criteria.
- Observation identity inputs.
- Descriptive metadata requirements and presentation-field mapping.
- User-facing limitations, rollback decision and source-specific unavailable errors.

## 9. Regression and preservation requirements for any future change

Before and after any approved consolidation:

- Preserve the immutable Task 08B evidence and all Task 08C–08F baselines; do not overwrite or regenerate them as the expected result.
- Verify all 85 source/research manifest hashes.
- Run backend unit tests and frontend unit tests for both adapters, plus full browser tests and the production build.
- Prove exact 504 mortality slot/order/value/null equivalence, including all eight unavailable observations and independent police export behavior.
- Prove exact 210 forensic slot/order/value/zero equivalence, seven labels, 30 quarters, original source/artifact hashes and byte-identical Substance Intelligence export.
- Exercise token changes, gaps, overlaps, duplicates, partial pages, metadata changes, invalid identities, invalid values and unavailable sources for both contracts.
- Verify existing legacy endpoints and export paths, Overview's forensic legacy consumer, ASSIST/treatment sources, and unrelated consumers remain unchanged.
- Confirm each explicit rollback still selects only its intended source and no failure triggers automatic fallback.
- Compare complete API JSON and export bytes, not visual similarity alone.

Passing tests would establish compatibility/preservation, not validate the underlying scientific methods or source truth.

## 10. Dissertation implications

Limited reuse can support a clear methods claim: common software mechanics are reused, while analytical contracts preserve the provenance, units, missingness, scope and non-additivity rules specific to each source. That distinction is especially important when comparing a suspected-death series with forensic detection categories.

A universal adapter would make the implementation appear more generic but would obscure the fact that the datasets do not share an observation definition. The separate adapters currently provide an auditable trail from frozen artifact to versioned contract to compatible presentation. The dissertation should describe any shared utilities as implementation-level infrastructure, not as evidence that the measures are statistically comparable.

## 11. Environmental reliability review and unresolved risks

Task 08F records an initial full-browser run in which the first all-sections acceptance scenario reached a Supabase read error on Overview. The isolated acceptance test later passed, followed by a clean full browser rerun with **40/40 passing**; the same report records backend tests passing separately. This establishes that the failure was not reproduced in those reruns.

The available evidence does **not** contain a durable request trace, Supabase response code/body, timing record or infrastructure log sufficient to establish whether the original event was a transient network/service issue, backend contention, or another cause. Classify it as **unresolved and not reproducible from current evidence**, not as a confirmed application defect. No network configuration, credential, permission or database change is recommended by this audit.

Other unresolved risks include future forensic vintage updates requiring reviewed pin/baseline changes, repeated full artifact verification per page without measured latency data, and the possibility that a shared pagination helper could accidentally under-validate one domain if it absorbs source-specific completeness rules.

## 12. Next task proposal

After review, authorize a narrowly scoped **08H shared integrity primitives prototype**: move canonical fingerprint/path helpers to neutral modules, preserve all outputs exactly, and add cross-contract tests. Treat pagination extraction as a separate optional follow-up after the prototype proves source-specific validators can remain outside the shared helper. No universal adapter, API changes, data changes or consumer migrations should be included.
