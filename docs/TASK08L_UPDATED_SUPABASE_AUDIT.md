# Task 08L — Updated Supabase data audit

**Inspection timestamp:** 2026-11-14 09:30:36 UTC  
**Mode:** Read-only Supabase REST/PostgREST inspection using the already configured publishable/anon access. No database or application changes were made. Secrets, project URL, raw error bodies, and row-level personal/sensitive data are not included.

## 1. Executive summary

The live Supabase check is **not a full database catalog audit**. The current credential can still read the same three reviewed projections as the previous Task 08B snapshot. Their counts, ordered-value fingerprints, and candidate keys match the 2026-11-12 snapshot exactly:

| Table | Current rows | Previous rows | Ordered projection fingerprint | Comparison |
|---|---:|---:|---|---|
| `mortality_quarterly` | 36 | 36 | `f3c6e921e8ba533fae9347b76c33d788b49cbc019547c9f1b42d81a892c4f14d` | Exact match |
| `indicator_configurations` | 4 | 4 | `871cb7a34e94daf47de8941b36eda71bea1af5c6fd25b998970058c1b4dab326` | Exact match |
| `indicator_results` | 76 | 76 | `8808f8da097dd86c1919715f966a120a711af6ff339b21fbb3a598a6162ecefd` | Exact match |

These are **116 accessible rows**, not a new total for all database tables. The cited previous “11,064-row” audit was not found in the repository; the available Task 08B snapshot documents 11 expected table names but only three queried projections and their 116 rows. Therefore 11,064 cannot be confirmed or reconciled from available prior evidence.

Read-only `HEAD`/`GET` probes of the 11 expected names returned HTTP 200, but eight names—including `naloxone_activity`—reported `Content-Range: */0`; `naloxone_activity?select=*&limit=1` returned an empty JSON array. This means **zero rows are visible to the current role in that request**, not that the physical table is empty, the table is absent, or that its schema is known. The PostgREST OpenAPI root still returns HTTP 401. Per the task restriction, those eight tables are treated as **unverified**, not empty.

The frozen Phase 4 naloxone source remains a separate, checksum-verified local artifact. Its 7,024 records form 16 weekly series (14 health boards, Scotland, Unknown), with 439 weeks per series from 2018-01-01 through 2026-05-25. This does not establish that the database table shares the same records or source vintage.

**No deletion or recalculation is supported by current evidence.** The three accessible database projections are byte-for-byte-equivalent at the ordered JSON fingerprint level to the previous snapshot. Existing Phase 4/5 naloxone calculations use the frozen Phase 4 artifact and its source file, not `naloxone_activity`; neither was modified. Do not overwrite or regenerate frozen outputs based solely on a database update whose rows and provenance are not visible.

## 2. Scope, access method, and limits

The inspection used `SupabaseRepository` for the established, allow-listed reads of the three reviewed tables, plus read-only HTTP `HEAD`/`GET` requests to the 11 names listed in the Task 08B metadata matrix. The existing anon/publishable credential was not printed or changed. No SQL write, policy change, migration, or direct database-catalog bypass was attempted.

### Current 11-name visibility result

| Expected name from Task 08B | Current `HEAD` / row visibility | Current accessible columns or status |
|---|---|---|
| `data_sources` | HTTP 200, `*/0` | No rows visible; schema/physical contents unverified |
| `mortality_quarterly` | HTTP 200, 36 rows | `year, quarter, suspected_deaths` via the reviewed reader |
| `forensic_toxicology` | HTTP 200, `*/0` | No rows visible; schema/physical contents unverified |
| `assist_toxicology` | HTTP 200, `*/0` | No rows visible; schema/physical contents unverified |
| `radar_intelligence` | HTTP 200, `*/0` | No rows visible; no narratives read; schema/physical contents unverified |
| `radar_alerts` | HTTP 200, `*/0` | No rows visible; schema/physical contents unverified |
| `naloxone_activity` | HTTP 200, `*/0`; sample GET returns `[]` | No rows visible; columns and physical contents unverified |
| `population_estimates` | HTTP 200, `*/0` | No rows visible; schema/physical contents unverified |
| `geographic_areas` | HTTP 200, `*/0` | No rows visible; schema/physical contents unverified |
| `indicator_configurations` | HTTP 200, 4 rows | 13 reviewed fields listed below |
| `indicator_results` | HTTP 200, 76 rows | 11 reviewed fields listed below |

The root PostgREST metadata/OpenAPI endpoint returned **401**. A successful empty select does not distinguish an empty relation from row-level policy filtering, and does not provide table DDL. It is not valid to call these eight relations empty or deleted. Their columns, keys, constraints, joins, and policies remain unverified.

### Reviewed projections and current checks

- `mortality_quarterly`: `year, quarter, suspected_deaths`. Years 2017–2025; quarter 1–4; no nulls or zero values; numeric values 222–413; `(year, quarter)` candidate key has zero duplicates.
- `indicator_configurations`: `configuration_id, indicator_name, configuration_label, method, baseline_description, rolling_window_quarters, lambda_value, limit_multiplier, lower_limit, upper_limit, cusum_k_sigma, cusum_h_sigma, notes`. Four rows; nullable fields retain the same pattern and values as the prior evidence; configuration ID has zero duplicates.
- `indicator_results`: `result_id, configuration_id, observation_year, observation_quarter, statistic_value, lower_limit, upper_limit, signal_flag, cusum_positive, cusum_negative, computation_reference`. 76 rows, 2019–2025; 72 nulls in each CUSUM component; four zero lower-limit values and four zero negative-CUSUM values; one `signal_flag=true`; `(configuration_id, observation_year, observation_quarter)` has zero duplicates.

Observed types, nulls and candidate-key checks describe returned JSON only. They do not prove SQL column types, declared constraints, primary keys, foreign keys, indexes or policy definitions. The previous Task 08B evidence likewise marks deployed DDL and policies unverified.

## 3. Reconciliation with previous audit evidence

The available immutable comparison is `docs/baselines/task08b/database-verification.json`, captured at `2026-11-12T12:08:54.575837Z`. Current checks used the same ordered projections and canonical JSON fingerprint method as that capture:

- All three row counts match.
- All three ordered projection fingerprints match exactly.
- Candidate keys have zero duplicates in the current observed projections.
- Current `indicator_results` still references configuration IDs 1–4 and contains one stored signal.
- Current `naloxone_activity` returns no visible records under the tested role; Task 08B had already marked that relation unverified and had not queried its rows.

The Task 08B snapshot is not the previous “11,064 rows” report. No reliable baseline file, table breakdown, or query definition for 11,064 was found. Consequently no claim is made that the total increased, decreased, or represents all physical database records.

## 4. Data change, duplicate, missingness and referential-integrity findings

- **Changes in the three readable tables:** none detected in the reviewed ordered projections since the Task 08B snapshot.
- **Changes in the other eight expected tables:** unverified. No row snapshots or authorized schemas are available for comparison.
- **Duplicates:** no duplicates in the three observed candidate keys. This is not a declaration that these combinations are deployed unique constraints.
- **Missingness/zeros:** the readable projections have the null and zero states listed above. These states match prior evidence; zeros are preserved as values, not missing rows.
- **Referential integrity:** result configuration IDs 1–4 resolve to the four observed configuration rows. This checks the current returned projection only; it does not inspect or prove a deployed foreign-key constraint. No joins or checks could be made for unverified tables.
- **Supabase catalog/security metadata:** unverified; metadata root returns 401. No permissions were broadened or bypassed.

## 5. Frozen research data and downstream use

The Phase 4 naloxone source `datasets/Group3_Item2_Data/radar_sas_naloxone_weekly_by_board.csv` still matches its source hash in the Phase 4 manifest:

`6f653b7b12c92e92175f09a2fb358ddb110991314a5b6e7489cf414c5f680235`

The frozen `analysis/phase4/outputs/naloxone_weekly.csv` has 7,024 rows and SHA-256:

`23e8c54fc42fd13c772c4fdb11268acbdb62b0562c0598ce49b035a8de7bec70`

That hash matches the Phase 4 manifest. The Phase 4 and Phase 5 pipelines identify local source/artifact files and manifests as inputs. The UI/API's `naloxone/activity` research route reads the Phase 4 artifact. The live `naloxone_activity` table is not in the frontend or backend Supabase repository's three-table allowlist and is not an input to those analyses.

This inspection did not access any row-level RADAR intelligence or other unreviewed content. It did not compare the frozen local source to the unavailable current table.

## 6. Status and recommended next step

**Current status:** three approved read projections are unchanged; eight other names have no rows visible and remain unverified; no deletion, update, recalculation, or artifact promotion is proposed.

To complete the requested all-table comparison, obtain an already-authorized schema/row-count export or DBA-provided read-only access for the eight currently unverified relations, plus the prior 11,064-row audit artifact and its query scope. Keep row-level `radar_intelligence` content out of the audit unless separately approved and demonstrably necessary.

No recalculation is authorized by this audit. Any subsequent plan should first verify the updated source's lineage, geographic semantics, measure definition, date coverage, row identities, and revision history, then propose a separate controlled change for review.
