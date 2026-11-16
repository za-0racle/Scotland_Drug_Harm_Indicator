# Task 08L — Recalculation impact matrix

**Assessment timestamp:** 2026-11-14 09:30:36 UTC  
**Scope:** Impact of the reported Supabase update, based on currently visible read-only database projections, existing source lineage, and frozen Phase 4/5 manifests. No recalculation or artifact modification was performed.

## 1. Summary decision

No existing calculation is demonstrated to require recalculation from the database update:

- The three accessible database projections (`mortality_quarterly`, `indicator_configurations`, `indicator_results`) exactly match the prior Task 08B ordered projection fingerprints and row counts.
- The `naloxone_activity` table returns no rows visible to the current role; its schema and lineage remain unverified. No relation between that table and frozen source data can be proven.
- The Phase 4 naloxone source file and artifact still match their existing source and output manifest hashes. Phase 4 and Phase 5 read those local files; they do not query `naloxone_activity`.

Do not regenerate, overwrite, or republish any frozen output. Await source verification and separate approval before planning a rerun.

## 2. Detailed impact matrix

| Layer / calculation | Current dependency | Evidence of database change | Impact classification | Recommendation |
|---|---|---|---|---|
| **Overview mortality KPIs / live quarterly feed** | Reads `mortality_quarterly` through the backend overview and DB route; uses complete returned years only. | 36 rows and fingerprint `f3c6e921…c4f14d` match Task 08B exactly. | **No change required** | No recalculation. Current values and missingness are unchanged in the accessible projection. |
| **Database monitoring configuration display** | Reads `indicator_configurations`; provides labels/parameters for stored result views. | 4 rows and fingerprint `871cb7a3…b4dab326` match Task 08B exactly. | **No change required** | No result recomputation. Display remains unchanged. |
| **Database monitoring results / historical flags** | Reads `indicator_results` and joins configuration labels; displayed results are stored database rows. | 76 rows and fingerprint `8808f8da…162ecefd` match Task 08B exactly; one signal; IDs 1–4 resolve to the accessible configurations. | **No change required** | No recalculation indicated. This is a stored-result display, not a live compute path. |
| **Frozen Phase 4 naloxone descriptive summaries** | Reads frozen local SAS source CSV; emits 7,024-row `naloxone_weekly.csv` and 1,616-row week-start-month artifact. | Source SHA `6f653b7b…5c680235` and artifact SHA `23e8c54f…e7bec70` still match their Phase 4 manifest. Live DB rows are not visible. | **Recalculation blocked pending source verification** if the new database data are intended to supersede or correct the source vintage; otherwise **No change required** to current frozen result. | Preserve frozen source/output. Verify lineage, dates, measures, geography and revisions before any approved new run. |
| **Phase 5 naloxone anomaly indicators** | Consumes the Phase 4 `naloxone_weekly` artifact; fixed, recorded model/configuration and output manifests. | No Phase 4 input hash change. No proven link from `naloxone_activity` to its input. | **Recalculation blocked pending source verification** only if a verified source-vintage correction is authorized; otherwise **No change required**. | Do not rerun or overwrite Phase 5. Any changed input requires a new, separately approved output location and complete manifest/baseline review. |
| **Other Phase 4 source summaries** | Use their respective frozen raw sources and manifests, not the database tables inspected. | The current live database comparison supplies no evidence those local source files changed. | **No change required** based on this database update alone. | Maintain existing artifacts; separate source evidence is required for any proposed refresh. |
| **Other anomaly/sensitivity/model outputs** | Consume saved Phase 4/5 data and frozen research inputs; no `naloxone_activity` database dependency identified. | No changed input artifact proven. | **No change required** based on current evidence; **Recalculation blocked pending source verification** if the update is asserted to be a new input vintage. | Preserve all model outputs; do not trigger exploratory recalculation. |
| **Historical forecast models and predictions** | Consume frozen local mortality histories/model outputs, with origin 2025 Q4 and target 2026 Q1 in the saved forecast. | Accessible `mortality_quarterly` projection matches prior snapshot; no verified new forecast input or approved current target. | **No change required** | Do not treat database refresh as authority to issue a current forecast or retrain. |
| **Geographic comparisons / rankings** | Artifact-backed series with boundary/source compatibility rules; naloxone is sourced from the frozen Phase 4 artifact. | No live `naloxone_activity` rows visible; no changed accessible DB rows. | **No change required** for current implementation; **Recalculation blocked pending source verification** if a new naloxone vintage is approved. | Keep Scotland, Unknown and health-board scopes separate. |
| **Exports and presentation adapters** | Render/API exports from accessible stored DB rows or checksum-verified frozen artifacts. | DB projections match prior fingerprints; local artifact hashes match manifests. | **No change required** | No export/schema/presentation changes. If source rows are later approved, compare exact export behavior in a separate task. |
| **Unverified database relations** | Eight expected PostgREST names return no visible rows; schemas/catalog metadata unavailable. | No reliable prior row-level snapshot, schema, or current content to compare. | **Recalculation blocked pending source verification** | Do not interpret invisibility as empty/deleted or use it to trigger recalculation. Request an authorized schema and source-linked export. |

## 3. Database-backed dashboards versus frozen analyses

The three readable tables serve a distinct database-backed monitoring view:

- `mortality_quarterly` supplies live-visible national quarterly counts for Overview.
- `indicator_configurations` supplies stored model labels and settings.
- `indicator_results` supplies the stored result series and associated labels.

These records currently match the prior audit exactly; the user-facing values need no change on present evidence. The Phase 4 naloxone chart and geographic series instead use a local, SHA-256-verified artifact. Phase 4 and Phase 5 manifests explicitly record local source/code/output hashes and no database input. A Supabase change, without a verified source link or changed local source, does not alter those immutable calculations.

The stored `indicator_results` values should not be recalculated unless the upstream mortality input and intended algorithm/configuration are both verified and an authorized run is approved. No current evidence satisfies that condition.

## 4. Controlled recalculation plan — conditional only

There is **no currently authorized recalculation plan**. If the owner later verifies that newly visible database rows represent a new/corrected SAS source vintage and requests recalculation, a separate approval should require, in order:

1. Obtain the source's schema, stable observation identifiers, geography/date/measure semantics, source/version/cutoff, and official Unknown/national roll-up documentation via authorized read-only access.
2. Compare the database projection with the retained original source file using stable keys; classify inserts, updates, deletes, duplicates and null/zero changes without modifying the source or existing baseline.
3. Determine whether the data are the same published source, an independently curated table, or a new release. Resolve overlap with board, Scotland and Unknown series from provider documentation, not totals alone.
4. Define and approve the precise calculations affected. Keep full-series and national/Unknown exclusion rules explicit; preserve original nulls and genuine zero values.
5. Run only to a new versioned scratch/output directory; never overwrite Phase 4/5 outputs. Produce a new source/artifact manifest and independent comparison report.
6. Review numerical differences, methodological assumptions, consumer/export impact and regression/preservation tests before any artifact promotion or UI change.

If those prerequisites cannot be met, the correct status remains **blocked pending source verification** and the current frozen evidence remains the only approved output.
