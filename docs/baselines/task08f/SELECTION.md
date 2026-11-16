# Task 08F — consumer selection and pre-migration scope

Recorded before implementing the frontend adapter or changing any consumer.

## Selected consumer

Migrate only the **Forensic toxicology** source option in the existing **Substance Intelligence** screen. Its isolated loader is `mountSubstance` in `src/platform/substance.js`, which delegates to `completeSubstances(api, source)` in `src/platform/substance-data.js`. The source selector already exposes forensic, ASSIST, treatment and explicitly pending contextual sources through a shared screen; the forensic branch can be redirected by a source-specific contract selector without changing its sibling branches.

## Scope and preservation

- Forensic source requests only move from `/toxicology/forensic` to `/analytical/v1/forensic-toxicology`.
- The existing Substance Intelligence selection, filters, charts, heatmap, ranking, category profiles, comparisons, table and CSV export remain the presentation surface.
- ASSIST, treatment, overview, comparison studio, Geographic Explorer, Mortality Analytics and other screens retain their existing legacy API behavior.
- No shared endpoint fallback is permitted. An explicit forensic-only configuration may choose `v1` or `legacy`; an analytical request failure never retries the legacy endpoint.
- Preserve the exact Task 08B legacy API response and Task 08E source/artifact identities, all source labels, values, category/quarter distinctions, null/zero states, descriptive fields, provenance and existing export bytes.
- No changes to the backend contract, source/artifact data, calculations, database, dependencies or Phase 9.

## Integration boundary

Only the selected screen's forensic loader will consume the new collector/mapping adapter. `completeSubstances` continues to handle existing source families and remains available to other callers. The task stops after this single consumer is migrated and verified.
