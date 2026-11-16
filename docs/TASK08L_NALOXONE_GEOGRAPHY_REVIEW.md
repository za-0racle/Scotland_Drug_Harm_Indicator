# Task 08L — Naloxone geography review

**Database inspection timestamp:** 2026-11-14 09:30:36 UTC  
**Scope:** Read-only review of the current `naloxone_activity` REST projection, available source documentation, and the unchanged frozen Phase 4 naloxone source/artifact. No database mutation, source substitution, or recalculation was performed.

## 1. Current database table status

The existing publishable/anon connection can issue:

- `HEAD /rest/v1/naloxone_activity?select=*` → HTTP 200, `Content-Range: */0`.
- `GET /rest/v1/naloxone_activity?select=*&limit=1` → HTTP 200, JSON `[]`.

No database rows or columns were returned. The PostgREST OpenAPI root returns HTTP 401, and the project's approved `SupabaseRepository` does not include this table. Therefore:

| Requested database fact | Result |
|---|---|
| Scotland-labelled row count | **Unverified**; no rows visible |
| Unknown-labelled row count | **Unverified**; no rows visible |
| Per-health-board counts | **Unverified**; no rows visible |
| Database columns, IDs, dates, measures, values | **Unverified**; schema not exposed |
| Whether the physical table is empty, filtered by RLS, or otherwise unavailable | **Unverified** |

An empty PostgREST response is not evidence that the underlying relation contains no data. No guessed column names or unapproved role were used to force access.

## 2. Frozen Phase 4 source evidence (not the live table)

The unchanged source file is `datasets/Group3_Item2_Data/radar_sas_naloxone_weekly_by_board.csv`; the existing Phase 4 output is `analysis/phase4/outputs/naloxone_weekly.csv`. The source SHA-256 is `6f653b7b12c92e92175f09a2fb358ddb110991314a5b6e7489cf414c5f680235`; the output SHA-256 is `23e8c54fc42fd13c772c4fdb11268acbdb62b0562c0598ce49b035a8de7bec70`. Both match the Phase 4 run manifest. These local files are presented only as a frozen prior source vintage; they are not represented as a query of `naloxone_activity`.

The frozen output contains **7,024 records**: 16 geographies × 439 Monday-start weeks, 2018-01-01 through 2026-05-25. All incident counts are present. It contains genuine zeros; they must not be changed to null or treated as missing.

| Frozen source label | Records | Zero-valued weeks | Total over frozen weeks | Latest reported week/value |
|---|---:|---:|---:|---|
| NHS Ayrshire & Arran | 439 | 0 | 3,604 | 2026-05-25 / 3 |
| NHS Borders | 439 | 120 | 553 | 2026-05-25 / 0 |
| NHS Dumfries & Galloway | 439 | 60 | 997 | 2026-05-25 / 1 |
| NHS Fife | 439 | 6 | 2,161 | 2026-05-25 / 4 |
| NHS Forth Valley | 439 | 8 | 2,579 | 2026-05-25 / 4 |
| NHS Grampian | 439 | 1 | 3,067 | 2026-05-25 / 6 |
| NHS Greater Glasgow & Clyde | 439 | 0 | 11,832 | 2026-05-25 / 15 |
| NHS Highland | 439 | 20 | 1,632 | 2026-05-25 / 0 |
| NHS Lanarkshire | 439 | 0 | 4,492 | 2026-05-25 / 11 |
| NHS Lothian | 439 | 0 | 5,457 | 2026-05-25 / 11 |
| NHS Orkney | 439 | 399 | 48 | 2026-05-25 / 0 |
| NHS Shetland | 439 | 401 | 43 | 2026-05-25 / 0 |
| NHS Tayside | 439 | 0 | 3,285 | 2026-05-25 / 4 |
| NHS Western Isles | 439 | 377 | 84 | 2026-05-25 / 0 |
| Scotland | 439 | 0 | 40,037 | 2026-05-25 / 59 |
| Unknown | 439 | 298 | 203 | 2026-05-25 / 0 |

There are no duplicate `(geography, week)` keys or null `observed_value` fields in this frozen output. These are source/artifact-level facts, not current database-table facts. The 32 missing values reported by Phase 4 refer to source moving-average fields, not missing incident counts.

## 3. Scotland and Unknown semantics

The current [PHS RADAR dashboard](https://scotland.shinyapps.io/phs-drugs-radar-dashboard/) was fetched read-only. Its release page states that the dashboard reports Scotland-level data, with NHS Board-level selection, and that SAS supplied the naloxone data. It warns that observed changes may reflect service configuration or data-quality/completeness changes. This supports retaining a separately labelled Scotland series as a published national-level indicator and retaining health boards as their own scope; it does not provide a technical definition of the `Unknown` row or the national roll-up formula.

In the frozen Phase 4 source, the Scotland weekly value equals the sum of the 14 board values **plus** the Unknown value in all 439 matched weeks. In 298 of those weeks, Unknown is zero and Scotland also equals the board-only sum; in the other 141 weeks, Scotland exceeds the board sum by the Unknown value. This exact arithmetic pattern is useful reconciliation evidence but does **not**, by itself, establish how SAS/PHS assigns or classifies records, whether Unknown is formally unallocated activity, or whether the current database table follows the same definition/vintage.

Consequently:

- Scotland can be retained as a distinct country/national aggregate for presentation, consistent with PHS's documented national-level series.
- Unknown should remain separately labelled and must not be relabelled as a board, distributed across boards, or silently included in a board-level ranking.
- The source-provided “Unknown” label is consistent with unassigned geography, but the precise operational meaning (“unallocated activity”) remains **unverified** without source technical documentation or authoritative provider confirmation.
- The observed arithmetic relation may be reported as a frozen-vintage check, not promoted to a universal aggregation rule or used to rebuild totals.
- Board comparisons must use only the 14 board series. Scotland and Unknown are excluded from board-peer comparison; values at different geographic levels are not added by the application.

## 4. Removal-option assessment

| Option | Assessment | Decision |
|---|---|---|
| **A. Retain all records; exclude Scotland/Unknown from board comparisons** | Scientifically safe as a minimum, preserving labels and preventing mixed-level comparisons. It does not expose Scotland as a separate national-level series. | Acceptable safeguard, but less informative than B for displaying the documented national series. |
| **B. Retain Scotland as national aggregate and Unknown separately** | Aligns with PHS's description of Scotland-level and NHS Board-level views, preserves every source row, and keeps Unknown outside board comparisons. The exact Unknown assignment and roll-up method remain qualified as unverified. | **Recommended presentation model**, subject to keeping source labels and definitions visible. It requires no database changes. |
| **C. Delete only verified erroneous duplicates/invalid imports** | No current database rows/IDs are visible, and the frozen source has no duplicate geography-week keys. No duplicate or invalid import is verified. | No deletion candidates identified; do not issue DELETE. |

### Deletion preview

- **Records selected for deletion:** 0.
- **Affected identifiers:** none identified. Current role returned no rows and the frozen source schema has no database identifiers.
- **Downstream dependencies:** no deletion impact, because no deletion is proposed. The frozen Phase 4/5 source/artifacts and Geographic Explorer rely on the local source/artifact path, not this table.

This is not a claim that the physical database contains zero records; it is a zero-candidate preview under evidence available to the authorized read scope.

## 5. Downstream use

The Phase 4 pipeline reads `radar_sas_naloxone_weekly_by_board.csv`, computes descriptive summaries, and emits the frozen weekly and week-start-month artifacts. Phase 5 consumes the Phase 4 artifact for saved anomaly outputs. The backend artifact repository exposes that frozen artifact through `/naloxone/activity`; the three-table Supabase repository does not read `naloxone_activity`. The Geography Explorer consumes the artifact route and preserves actual geographic labels and weekly values.

No existing calculation is shown to consume the updated database relation. The database table's lineage relative to the source file, output vintage, metric, timestamps and identifiers is not available, so equality or divergence cannot be assessed.

## 6. Required evidence before revisiting the decision

Obtain an authorized table schema and a safe aggregate/row export containing stable IDs, geography labels/IDs, dates, measures, values, missingness and source/version fields. Also obtain the provider's definition of Unknown and Scotland roll-up, including whether national values include unallocated records and how revisions are handled. Then compare with the frozen source by stable key and source vintage. Until these are available, retain the frozen outputs and do not delete, merge, or recalculate.
