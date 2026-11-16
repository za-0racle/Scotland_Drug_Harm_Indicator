# Task 08M — Full Supabase re-audit

**Completed:** 2026-11-14 10:16 UTC
**Access:** Existing configured publishable/anon credential; read-only PostgREST `SELECT`. Credentials, URLs, narrative contents, and individual records are omitted.

## Executive result

All 11 requested table endpoints returned HTTP 200. Complete retrieval used pages of 500 rows with `Prefer: count=exact`; each returned row count reached the server-reported total. No table was treated as complete based on a single default-size response.

The current total is **11,064 rows**, equal to the supplied prior total. All 11 table counts match the supplied counts. This confirms counts, not that every database row is unchanged. Current live observations also match the available row-level import files except for the specific metadata differences documented below. The three tables with an immutable Task 08B database snapshot retain their exact prior fingerprints.

The live naloxone table contains the same 7,024 geography-week observations and administration values as both the local import and frozen Phase 4 output. For all 439 weeks, the Scotland value equals the sum of the 14 boards plus Unknown. The database does, however, contain a populated moving-average value for 14 first-week board rows where the local import and frozen artifact are missing.

**No model or frozen artifact needs recalculation based on changed administration values:** none were found. Do not silently adopt the 14 different moving-average values or overwrite the frozen source/artifact. Resolve their provenance first if the live table is intended to supersede the frozen source. Scotland and Unknown should be retained as separate series and excluded from board-to-board comparisons; there is no verified basis for deleting either.

## 1. Access and completeness

- All 11 requested table reads returned HTTP 200 under the existing role.
- Exact PostgREST counts matched the number retrieved for every table.
- The largest relation, `naloxone_activity`, was retrieved over multiple 500-row pages; `population_estimates` and `radar_intelligence` were likewise fully paginated.
- The PostgREST OpenAPI root still returns HTTP 401. Thus SQL types, declared constraints, indexes, policies and grants are not verified from catalog metadata.
- `radar_alerts` returned an exact count of zero. Since it returned no rows, `select=*` exposed no column names; its live schema remains unverified. This is an accessible zero-row result, not an inaccessible table.
- The allow-listed application repository still reads only `mortality_quarterly`, `indicator_configurations` and `indicator_results`. No direct application consumer of the other eight tables was found in the backend/frontend source search.

## 2. All-table counts and comparison

| Table | Current rows | Prior supplied rows | Difference | Current status |
|---|---:|---:|---:|---|
| `data_sources` | 18 | 18 | 0 | Readable |
| `geographic_areas` | 18 | 18 | 0 | Readable |
| `mortality_quarterly` | 36 | 36 | 0 | Readable; Task 08B fingerprint matches |
| `forensic_toxicology` | 210 | 210 | 0 | Readable |
| `assist_toxicology` | 72 | 72 | 0 | Readable |
| `naloxone_activity` | 7,024 | 7,024 | 0 | Readable; fully paginated |
| `population_estimates` | 2,025 | 2,025 | 0 | Readable |
| `radar_intelligence` | 1,581 | 1,581 | 0 | Readable; narrative values not reproduced |
| `radar_alerts` | 0 | 0 | 0 | Readable; no rows |
| `indicator_configurations` | 4 | 4 | 0 | Readable; Task 08B fingerprint matches |
| `indicator_results` | 76 | 76 | 0 | Readable; Task 08B fingerprint matches |
| **Total** | **11,064** | **11,064** | **0** | **Counts match** |

### Returned fields and reporting coverage

Column names below are the fields actually returned by `select=*` when rows were present. They do not establish declared SQL types.

| Table | Returned columns | Date/period coverage |
|---|---|---|
| `data_sources` | `dataset_name, notes, publisher, source_id, source_sha256, source_url` | No date field |
| `geographic_areas` | `area_code, area_name, area_type, source_dataset, valid_from, valid_to` | `valid_from`: 2014-04-01–2019-04-01; `valid_to`: 2018-02-01–2020-03-31 |
| `mortality_quarterly` | `year, quarter, suspected_deaths, source_id` | 2017–2025; quarters 1–4 |
| `forensic_toxicology` | `drug_name, measure, observation_id, reporting_quarter, source_id, value` | Q1 2019–Q4 2025 |
| `assist_toxicology` | `assist_period, chart_label, drug_name, observation_id, percentage, source_id` | 12 source periods: Q4 May–Aug 2023 through Q15 Feb–May 2026 |
| `naloxone_activity` | `administrations, moving_average, reported_board, source_dataset, week_beginning` | 439 weeks, 2018-01-01–2026-05-25 |
| `population_estimates` | `area_code, population_all_ages, sex, source_dataset, year` | 1981–2025 |
| `radar_intelligence` | `appearance, area, primary_drugs, reason_for_report, region, report_code, report_period, source_dataset, summary` | 16 source-reported periods, QR1 (1 Jul–23 Sep 2022) through QR9 (5 Jul–4 Oct 2024) |
| `radar_alerts` | No columns returned because no rows were returned | No rows |
| `indicator_configurations` | `baseline_description, configuration_id, configuration_label, cusum_h_sigma, cusum_k_sigma, indicator_name, lambda_value, limit_multiplier, lower_limit, method, notes, rolling_window_quarters, upper_limit` | Not applicable |
| `indicator_results` | `computation_reference, configuration_id, cusum_negative, cusum_positive, lower_limit, observation_quarter, observation_year, result_id, signal_flag, statistic_value, upper_limit` | 2019–2025; quarters 1–4 |

### Geographic coverage

- `geographic_areas`: 18 area codes representing 14 distinct area names; one observed area type.
- `mortality_quarterly`, `forensic_toxicology` and `assist_toxicology`: no geographic column was returned, so geography cannot be derived from these row projections.
- `naloxone_activity`: 14 NHS boards plus separate `Scotland` and `Unknown` labels.
- `population_estimates`: 15 area codes and three sex categories.
- `radar_intelligence`: 74 distinct `area` labels and 8 `region` labels. Narrative contents and individual labels are not reproduced.
- `data_sources`, `radar_alerts` and the indicator configuration/result tables: no geographic coverage can be determined from the returned rows/schema.

## 3. Missing values, zeros and duplicates

Duplicate checks used the observed natural keys listed below; these checks do not prove deployed uniqueness constraints. There were no duplicate full rows in the returned nonempty tables.

| Table | Checked key | Duplicate key rows | Missing values and notable zeros |
|---|---|---:|---|
| `data_sources` | `source_id` | 0 | No null or blank fields |
| `geographic_areas` | `area_code` | 0 | No null or blank fields in the live result |
| `mortality_quarterly` | `(year, quarter)` | 0 | No nulls or zeros; suspected deaths range 222–413 |
| `forensic_toxicology` | `observation_id` | 0 | No nulls; one observed zero; values range 0–489 |
| `assist_toxicology` | `observation_id` | 0 | No nulls or zeros; percentages range 10.5960264900662–87.5 |
| `naloxone_activity` | `(reported_board, week_beginning)` | 0 | `moving_average`: 18 nulls; `administrations`: no nulls and 1,690 genuine zeros |
| `population_estimates` | `(area_code, year, sex)` | 0 | No nulls or zeros; population range 9,357–5,545,500 |
| `radar_intelligence` | `report_code` | 0 | No nulls or blank fields; narrative values are intentionally not reproduced |
| `radar_alerts` | No key test possible | 0 rows | Empty result |
| `indicator_configurations` | `configuration_id` | 0 | Nulls: `cusum_h_sigma` 3, `cusum_k_sigma` 3, `lambda_value` 1, `limit_multiplier` 1, `lower_limit` 4, `rolling_window_quarters` 1, `upper_limit` 4 |
| `indicator_results` | `(configuration_id, observation_year, observation_quarter)` and `result_id` | 0 | `cusum_negative` and `cusum_positive`: 72 nulls each; four zero negative-CUSUM and four zero lower-limit values |

## 4. Naloxone geography and source comparison

The observed geography/date/value fields are `reported_board`, `week_beginning` and `administrations`. There are 16 labels: 14 NHS boards, `Scotland`, and `Unknown`, each with 439 weekly records. There are 439 unique weeks and no duplicate geography-week keys.

| Geography | Records |
|---|---:|
| NHS Ayrshire & Arran | 439 |
| NHS Borders | 439 |
| NHS Dumfries & Galloway | 439 |
| NHS Fife | 439 |
| NHS Forth Valley | 439 |
| NHS Grampian | 439 |
| NHS Greater Glasgow & Clyde | 439 |
| NHS Highland | 439 |
| NHS Lanarkshire | 439 |
| NHS Lothian | 439 |
| NHS Orkney | 439 |
| NHS Shetland | 439 |
| NHS Tayside | 439 |
| NHS Western Isles | 439 |
| Scotland | 439 |
| Unknown | 439 |

### Row-level reconciliation

- All **7,024** database `(week_beginning, reported_board)` keys match the local import and frozen Phase 4 artifact; there are no database-only or comparison-only keys.
- All **7,024** `administrations` values exactly match both the local import and frozen artifact.
- `administrations` has 0 nulls and 1,690 zeros. These zeros remain observations, not missing values.
- For all **439/439** weeks with all 14 boards, Scotland equals the 14-board sum plus Unknown; maximum difference is zero.
- Scotland equals the board-only sum in **298/439** weeks and differs in **141/439**; the maximum absolute difference is 7. The observed relation does not justify omitting Unknown from a national total.

### Moving-average discrepancy

The live database has 18 null `moving_average` values, compared with 32 missing values in the local import and frozen artifact. The 14 differences are all **non-null in the live table but missing in both references**, one for each of the 14 health boards on **2018-01-01**. No other `moving_average` numeric differences were found among matched non-null values.

The live table’s `source_dataset` label identifies the same source file. In `data_sources`, that source is `source_id=14`, and its SHA-256 matches the Phase 4 source manifest. The matching source checksum does not explain why the live table has 14 populated first-week moving averages absent from the source snapshot. Treat this as a source-field discrepancy requiring provenance clarification, not as evidence to alter the frozen source or output.

## 5. Comparison with available earlier row-level evidence

### Immutable Task 08B database projections

The current ordered projections were independently fingerprinted using the Task 08B canonical ordered-JSON method. All match exactly:

| Projection | Current rows | Current SHA-256 | Task 08B comparison |
|---|---:|---|---|
| `mortality_quarterly` | 36 | `f3c6e921e8ba533fae9347b76c33d788b49cbc019547c9f1b42d81a892c4f14d` | Exact match |
| `indicator_configurations` | 4 | `871cb7a34e94daf47de8941b36eda71bea1af5c6fd25b998970058c1b4dab326` | Exact match |
| `indicator_results` | 76 | `8808f8da097dd86c1919715f966a120a711af6ff339b21fbb3a598a6162ecefd` | Exact match |

### Local import-file comparisons

The repository does not contain a prior complete 11-table database row snapshot. Available `group3_*_import.csv` files were compared by source/natural keys; they are source/import references, not proof of what the database contained at the previous audit timestamp.

| Table | Comparison result against available local import |
|---|---|
| `data_sources` | All 18 dataset names match; all 18 `source_sha256` values match. Seven `source_url` fields are now populated where the import file was blank. |
| `geographic_areas` | All 18 area codes match. Fourteen `valid_to` fields are populated in the database where the import file was missing them; no reverse missingness transition. |
| `forensic_toxicology` | All 210 keyed records and common fields match. |
| `assist_toxicology` | All 72 keyed records and common fields match. |
| `naloxone_activity` | All 7,024 keys and administration values match; the 14 moving-average differences are described above. |
| `population_estimates` | All 2,025 keyed records and common fields match. |
| `radar_intelligence` | All 1,581 keyed records and common fields match. |

The only available source IDs directly associated with the analytical source rows are mortality `12`, forensic `16`, ASSIST `15`, and naloxone `14`. The Phase 4 naloxone manifest source hash and the current `data_sources` hash match. Source hashes for the 18 data-source records match the import file; the seven source-URL additions are metadata changes, not observed source-checksum changes.

For `geographic_areas` and `naloxone_activity`, the local import comparison proves a difference from those files, but no timestamped prior database row snapshot exists to establish when the database fields changed. Do not describe those as observed changes since the prior audit without that snapshot.

## 6. Recalculation assessment

| Output or dependency | Finding | Decision |
|---|---|---|
| Database-backed mortality and monitoring projections | Their three Task 08B fingerprints remain exact. | No recalculation required. |
| Forensic, ASSIST, population and RADAR research inputs | Their current rows match the corresponding local import files. No changed input values were found in those comparisons. | No recalculation indicated. This does not substitute for a prior full database snapshot. |
| Naloxone weekly administration series | All observations and values match the frozen Phase 4 artifact exactly. No changed week, geography or administration value was found. | No model recalculation required from the observed administration series. |
| Naloxone source-reported moving average | 14 first-week board values are populated in the DB but missing in the frozen source/artifact. Phase 4 stores this source field and its missingness as metadata; it is not the `administrations` measure. | Do not overwrite or rebuild from the DB until the 14 values’ provenance is established. A newly approved versioned artifact could require metadata/quality-report differences; this is not evidence that the existing anomaly/model outputs need recalculation. |
| Geographic validity dates | 14 `valid_to` fields are populated in DB but missing in the local import. Repository search found no current direct application consumer of `geographic_areas`. | No existing analysis recalculation indicated. Verify boundary-date provenance before future temporal joins or geographic filtering use these rows. |
| Source URLs | Seven metadata fields differ from the import; source checksums are unchanged. | No analytical recalculation indicated. |
| Scotland/Unknown handling | The aggregate identity is exactly consistent with all 439 weeks when Unknown is included. | Preserve source rows and labels; do not aggregate into board peer comparisons. |

Phase 4 and Phase 5 continue to use their versioned local source/artifact inputs. This re-audit did not run models, regenerate outputs or change frozen data. If the owner intends the live database’s 14 additional moving-average values or 14 geographic end dates to supersede existing evidence, first obtain source lineage and definitions, then authorize any new versioned analysis separately.

## 7. Recommendation for Scotland and Unknown

**Retain Scotland as a separate national series and retain Unknown as its own source-labelled series; exclude both from NHS-board-to-board comparisons. Do not delete either category.**

All records are unique on the observed geography-week key and match the frozen source’s geography/week coverage and administration values. Scotland equals the 14-board total plus Unknown for every week. The relation supports preserving all source categories; it does not establish a general policy to combine geographies or reinterpret Unknown beyond its source label.

## 8. Blockers and actions requiring user/provider evidence

1. Clarify why 14 live naloxone `moving_average` values for 2018-01-01 are populated while both the local source and frozen artifact mark them missing. Provide the authoritative source/version or import transformation; do not infer or repair them.
2. Confirm the provenance of the 14 populated `geographic_areas.valid_to` fields before those fields are used in temporal boundary logic.
3. If an exact audit of database row changes since the prior timestamp is required for all 11 tables, provide a timestamped earlier row snapshot for the eight tables beyond the three preserved Task 08B projections. The local import CSVs are useful references but are not earlier database snapshots.
4. `radar_alerts` currently has zero visible rows; an authorized schema/DDL export is needed to verify its columns and constraints. The PostgREST metadata root remains HTTP 401.
5. Deployed SQL constraints, policies and grants remain unverified. No policy change or broader credential was attempted.

No database write, deletion, policy change, model run, frozen-source overwrite or application edit was performed.
