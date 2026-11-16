# Task 08I — Pagination consolidation feasibility review

## 1. Decision

**Recommendation: Decision A — retain the mortality and forensic frontend collectors separately.**

There is a small, recognizable overlap in page-window mechanics, but most of each loop is coupled to source-specific parsing, metadata pinning, ordering, and completion rules. A shared coordinator would need callbacks for those rules and a generic error policy, yielding little net simplification while adding an abstraction that is exercised by both sources. The current two collectors are clear, independently tested, and have no known pagination defect.

This is a read-only review. No application, API, database, baseline, source, artifact, or analytical code was modified.

## 2. Current pagination architecture

The shared [API client](../src/api/client.js) handles transport, query allow-listing, JSON/error interpretation, and the narrowly scoped `expected_collection` query parameter for both analytical routes. It deliberately leaves contract interpretation to the collectors.

The two consumers each call one source-specific collector:

- Geographic Explorer's police feed uses [`collectMortality`](../src/api/mortality-collector.js#L63), through the mortality presentation adapter.
- Substance Intelligence's forensic feed uses [`collectForensic`](../src/api/forensic-collector.js#L160), through the forensic presentation adapter.

Each collector starts at offset zero, requests a bounded page, and supplies `expected_collection` only on continuation requests. Both validate page-level metadata before adding observations and return a collection only after all pages pass validation.

The backend independently implements source-specific page slicing and continuation-token checks in the mortality and forensic adapters. It also has separate offline page-sequence verifiers. These are not frontend collector call sites; this review does not recommend changing or consolidating them.

## 3. Exact duplication inventory

The complete frontend functions span **19 lines** in the mortality collector (lines 63–81) and **47 lines** in the forensic collector (lines 160–206). The 28-line size difference is chiefly the forensic-specific category-order and category-quarter coverage logic, not missing generic pagination abstraction.

| Mechanic | Mortality | Forensic | Assessment |
|---|---|---|---|
| Initial offset, page-size guard, page loop | 4–5 lines | 5–6 lines | Similar structure; guards have the same bounds, while error messages and state differ. |
| Request path and continuation params | 1 line | 1 line | Same parameter shape (`offset`, `limit`, optional `expected_collection`); route path is source-specific. |
| Page-window checks | 1 condition line | 3 wrapped condition lines | Same core returned-count/offset/limit checks; mortality also imposes its own upper total bound, while forensic pins total to 210. |
| Metadata/version pinning | 1 long conditional plus assignments | 2 multiline conditions plus signature initialization | Not equivalent: mortality compares one normalized metadata object; forensic validates and separately pins source, artifact, measure, categories, and research metadata. |
| End, next-offset and complete-flag checks | 2–3 lines | 3 lines | Same arithmetic and expected flags; source-specific diagnostics. |
| Per-row validation and ordering | 1 source callback loop | 8+ lines including category-transition state | Fundamentally different. Mortality verifies geography-quarter identity/order; forensic additionally verifies category order and complete category-quarter coverage. |
| Append/advance/continue | 2 lines | 2 lines | Equivalent mechanics, but embedded in the collectors' distinct state and validation flows. |
| Final completeness checks | 2 lines | 5+ lines | Both reject partial results; forensic also verifies all 210 identities and all 30 quarters for every category. |

Across the loops, approximately **6–9 physical lines per implementation** are candidates for moving behind shared mechanics: request construction/continuation, end-offset arithmetic, append/advance, and generic next-offset/complete-flag checks. Several checks are only structurally similar, not identical. A literal line count overstates safely extractable behavior because the current source-specific guards and metadata validation must stay in the collectors.

There are only **two production collector consumers**—one per source. The transport is already shared in `client.js`; a coordinator would not reduce duplicated network-client logic.

## 4. Shared mechanics versus source-specific validation

### Plausibly reusable

- Start with offset zero and a bounded page size.
- Request the next page using the prior collection token.
- Check that the returned window starts at the expected offset and agrees with the declared count.
- Calculate the expected next offset and terminal-page flags.
- Append page observations in response order and advance the offset.
- Reject a collection that terminates before its declared total.

### Must remain source-specific

- Contract version, source/artifact identity, and metadata validation.
- Which metadata fields form the stable cross-page signature.
- The mortality source-version policy versus the forensic fixed reviewed-vintage pins.
- Observation and forensic category identity checks.
- Source-specific ordering, duplicate-slot, and coverage rules.
- Mortality's eight unavailable values versus forensic's observed zero and non-additive category semantics.
- The exact total and category-quarter completeness criteria.
- Error prefixes and source-specific failure explanations.
- Presentation mapping, existing export behavior, and each consumer's explicit rollback control.

In particular, a generic `total` equality or completion rule cannot establish forensic scientific completeness: all seven categories must still cover the same 30 quarters. Nor can a generic returned-count check establish mortality's geography-quarter identity/order conditions.

## 5. Decision A — retain separate collectors

**Benefits**

- Keeps each collector's token, metadata, ordering, and completeness rules visible beside its source-specific checks.
- Avoids callbacks or a generic failure factory for the relatively small shared mechanics.
- Retains separate error messages and avoids making a shared helper a failure point for both frontends.
- No migration or regression risk; existing consumer and rollback boundaries remain unchanged.

**Costs**

- A future change to the generic page-window invariant must be considered in both collectors.
- A small amount of offset and continuation code remains duplicated.

The cost is limited to two collectors and is mitigated by separate source-specific pagination tests and a shared `client.js`. No observed drift or failure currently warrants accepting the coupling of a new coordinator.

## 6. Decision B — minimal shared coordinator

A safe coordinator could own only request iteration and window advancement. Its conceptual interface would need at least:

1. `api`, route path, and validated page size;
2. a source callback that validates the response contract and returns total, token, stable-metadata signature, and source metadata;
3. a source callback to validate/consume each observation while maintaining its own identity and ordering state;
4. source-specific error construction or a fail callback; and
5. a result-mapping callback or convention for returning the validated metadata and ordered observations.

With that boundary, validators can remain technically independent. However, the collector would delegate its most error-prone control flow while still requiring substantial source-specific callbacks, state, and final completion checks. A smaller helper that only calculates next-offset invariants would require fewer callbacks, but would leave the request loop, token pinning, and collection orchestration duplicated. Neither option has a clear maintenance advantage over the current functions.

### Estimated benefit and complexity

- **Gross removable duplication:** approximately 6–9 candidate lines in each collector, or 12–18 lines moved/centralized in total; not all are strictly identical.
- **Net code reduction:** likely small or zero after adding the coordinator, source validation callbacks, error policy, and result boundary. The coordinator would also need its own tests.
- **Configuration/callbacks:** at least four source-specific inputs or callbacks, with additional handling if source-specific page errors and final completeness are included.
- **Regression burden:** generic helper tests plus both complete collector suites and both browser regression suites. A bug in the shared offset/token flow could now affect both integrations.
- **Existing behavioral test surface:** the unit suites independently cover page-size variation, token transmission/change, missing or truncated pages, gaps/overlaps, backend failure, and exact ordered complete collections. Browser tests independently cover route selection, failure without fallback, retry/navigation, rollback, and preserved exports.

The expected reduction is not proportionate to the added indirection and shared failure mode.

## 7. Evidence supporting the decision

The evidence shows the current collectors work and that source-specific checks are materially different:

- Mortality unit tests retrieve **504** observations and confirm **8 null/unavailable** values. Its failure tests cover changed tokens, source/artifact metadata, malformed windows, duplicates, truncation, and backend failure.
- Forensic unit tests retrieve **210** observations, preserve **one genuine zero**, and validate **seven categories across 30 quarters**. Its failure tests cover changed tokens, missing pages, overlap, truncation, and partial backend failure.
- Browser coverage exercises the two consumer routes independently and verifies no automatic fallback to legacy endpoints.
- Task 08H pre/post evidence reports exact response and pagination bytes, tokens, identities, frontend presentations, and CSV export equivalence. Its preservation check reports **85/85** source/research manifests, **72/72** pre-existing Task 08B–08G evidence files, and **3/3** frozen source/artifact hashes matching.
- Task 08G identified duplicated pagination mechanics as a possible later consolidation, while explicitly requiring source validators, page-completeness criteria, and identities to remain separate. Task 08H extracted integrity helpers only and did not refactor pagination.

These are preservation and regression facts, not evidence that mortality and forensic observations share the same analytical meaning.

## 8. Regression risks and preservation requirements

The primary risk in Decision B is that a coordinator may accidentally absorb source decisions into generic settings: stable metadata fields, total constraints, the treatment of empty pages, or collection-completion criteria. If the callback design instead leaves all those rules in their collectors, the abstraction's net benefit shrinks.

Any separately approved implementation must preserve the Task 08B–08H evidence and verify:

- Exactly 504 mortality observations, including the eight unavailable values.
- Exactly 210 forensic observations, the genuine zero, all seven categories, and all 30 periods.
- All observation/category identities, tokens, source/artifact provenance, order, and exact API/page response bytes.
- Source-specific failure behavior and explicit rollback controls, with no automatic legacy fallback.
- Exact existing frontend presentations and exports.
- Both consumer/browser regression suites, full backend/frontend/browser suites, production build, and the immutable evidence/manifests.

## 9. Recommendation and next implementation priority

**Retain separate frontend collectors. Do not extract a shared page coordinator now.**

The most useful next step is not pagination refactoring. Keep the existing per-source checks and use the current independent tests as maintenance guardrails. Reconsider extraction only if a third materially different contract creates another instance of this same stable page-window protocol, or if a concrete pagination defect demonstrates that maintaining the duplicate mechanics is causing drift. Any such proposal should first show a measured net reduction and a callback boundary that leaves all scientific validation independent.
