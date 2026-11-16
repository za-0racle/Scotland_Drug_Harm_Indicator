# Task 08B — API contract inventory

Captured from the existing application, not a proposed replacement contract. `resource-contracts.json` contains every returned field, null count, complete-result fingerprint, artifact version and SHA-256. `openapi.json` records every route and query schema. No endpoint response was changed.

## Retrieval and response rules

- Verification uses production `PlatformService.query` in-process for all 28 catalog resources. Metadata routes and OpenAPI were additionally checked through ASGI GETs. This does not establish availability of a separately deployed API.
- All-resource capture sets `signals_only=false`; `/anomalies` defaults to signals only. Enhanced HTTP selection requires a verified method, so its 31,512-row baseline is the union of methods or the enhanced export.
- Common filters: `geography_id`, `boundary_type`, `indicator`, `category`, `model`, `compare_to`, `start_year`, `end_year`, `start_date`, `end_date`, `offset`, `limit`, `signals_only`. Exact constraints/defaults are in OpenAPI. Some fields apply only to particular resources; do not assume every filter is meaningful for every row shape.
- Pagination: offset 0 by default, limit 100 by default, maximum 1,000; offset maximum 1,000,000. Exports are paginated too. Capture requested 1,000 and verified returned count against stable totals.
- Envelope: `state, kind, data, total, offset, limit, metadata, message`. Empty matches are not zero harm or no official alerts. Null values remain distinct from zeros.
- Artifact metadata: resource, storage, analytical version, execution timestamp, artifact SHA-256, source path, provenance manifest and limitations. Individual source publication/cutoff/definition fields vary by resource.
- Exact-date filters exclude records lacking exact dates; they do not invent ASSIST dates. Geography identifiers identify scopes, not verified polygons.

## Approved artifact resources

| Resource | Existing endpoint/access | Complete records / pages | Version | Unit / period / geography |
|---|---|---:|---|---|
| `mortality_trends` | `/api/v1/exports?resource=mortality_trends&format=json` | 504 / 1 | phase4-1.0.0 | unit="count"; period_basis="calendar_quarter_legacy_10_day_adjustment"; boundary_type="country", "police_division" |
| `forensic` | `/api/v1/toxicology/forensic`<br>`/api/v1/exports?resource=forensic&format=json` | 210 / 1 | phase4-1.0.0 | unit="detection_count"; period_basis="calendar_quarter"; boundary_type="national_testing_sample" |
| `assist` | `/api/v1/toxicology/assist`<br>`/api/v1/exports?resource=assist&format=json` | 72 / 1 | phase4-1.0.0 | unit="percent"; period_basis="source_study_period_not_calendar_quarter"; boundary_type="study_sample" |
| `treatment` | `/api/v1/toxicology/treatment`<br>`/api/v1/exports?resource=treatment&format=json` | 140 / 1 | phase4-1.0.0 | unit="detection_count"; period_basis="calendar_month"; boundary_type="health_board" |
| `naloxone` | `/api/v1/naloxone/activity`<br>`/api/v1/exports?resource=naloxone&format=json` | 7,024 / 8 | phase4-1.0.0 | unit="incident_count"; period_basis="week_beginning_monday"; boundary_type="country", "health_board", "unknown" |
| `anomalies` | `/api/v1/anomalies?signals_only=false`<br>`/api/v1/exports?resource=anomalies&format=json` | 8,034 / 9 | phase5-1.0.0 | unit="count", "detection_count", "incident_count", "percent"; period_basis="calendar_month", "calendar_quarter", "calendar_quarter_legacy_10_day_adjustment", "source_study_period_not_calendar_quarter", "week_beginning_monday"; boundary_type="country", "health_board", "national_testing_sample", "police_division", "study_sample", "unknown" |
| `sensitivity` | `/api/v1/anomalies/sensitivity`<br>`/api/v1/exports?resource=sensitivity&format=json` | 7,878 / 8 | phase5-1.0.0 | period_basis="calendar_month", "calendar_quarter", "calendar_quarter_legacy_10_day_adjustment", "week_beginning_monday"; boundary_type="country", "health_board", "national_testing_sample", "police_division", "unknown" |
| `enhanced` | `/api/v1/anomalies?model=<verified-method>&signals_only=false`<br>`/api/v1/exports?resource=enhanced&format=json` | 31,512 / 32 | phase5c-1.0.0 | period_basis="calendar_month", "calendar_quarter", "calendar_quarter_legacy_10_day_adjustment", "week_beginning_monday"; boundary_type="country", "health_board", "national_testing_sample", "police_division", "unknown" |
| `diagnostics` | `/api/v1/anomalies/diagnostics`<br>`/api/v1/exports?resource=diagnostics&format=json` | 16,032 / 17 | phase5c-1.0.0 | period_basis="calendar_month", "calendar_quarter", "calendar_quarter_legacy_10_day_adjustment", "week_beginning_monday"; boundary_type="country", "health_board", "national_testing_sample", "police_division", "unknown" |
| `model_metrics` | `/api/v1/anomalies/models`<br>`/api/v1/exports?resource=model_metrics&format=json` | 336 / 1 | phase5c-1.0.0 | boundary_type="country", "health_board", "national_testing_sample", "police_division", "unknown" |
| `runs` | `/api/v1/anomalies/runs`<br>`/api/v1/exports?resource=runs&format=json` | 392 / 1 | phase5c-1.0.0 | period_basis="calendar_month", "calendar_quarter", "calendar_quarter_legacy_10_day_adjustment", "week_beginning_monday"; boundary_type="country", "health_board", "national_testing_sample", "police_division", "unknown" |
| `evidence` | `/api/v1/evidence/cross-source`<br>`/api/v1/exports?resource=evidence&format=json` | 4,512 / 5 | phase5c-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |
| `candidates` | Internal catalog/service only; no direct public route or admitted export | 2,256 / 3 | phase5c-1.0.0 | boundary_type="unknown" |
| `zero_baseline` | `/api/v1/anomalies/zero-baseline`<br>`/api/v1/exports?resource=zero_baseline&format=json` | 6 / 1 | phase5c-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |
| `summary` | Internal catalog/service only; no direct public route or admitted export | 1 / 1 | phase5c-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |
| `registry` | `/api/v1/sources` | 6 / 1 | phase5c-1.0.0 | period_basis="calendar_month", "calendar_quarter", "calendar_quarter_legacy_10_day_adjustment", "source_study_period_not_calendar_quarter", "week_beginning_monday" |
| `gaps` | `/api/v1/sources/gaps`<br>`/api/v1/exports?resource=gaps&format=json` | 10 / 1 | phase5c-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |
| `annual` | `/api/v1/mortality/annual`<br>`/api/v1/exports?resource=annual&format=json` | 30 / 1 | phase6-1.0.0 | unit="deaths"; period_basis="calendar_year_of_registration"; boundary_type="council", "country" |
| `geographic_trends` | Internal catalog/service only; no direct public route or admitted export | 15 / 1 | phase6-1.0.0 | unit="deaths"; period_basis="calendar_year_of_registration"; boundary_type="council" |
| `comparisons` | `/api/v1/exports?resource=comparisons&format=json` | 15 / 1 | phase6-1.0.0 | period_basis="calendar_year_of_registration" |
| `rates` | `/api/v1/exports?resource=rates&format=json` | 22 / 1 | phase6-1.0.0 | unit="published_age_standardised_deaths_per_100000"; period_basis="five_year_registration_period"; boundary_type="council", "country" |
| `rate_comparisons` | `/api/v1/geography/comparisons`<br>`/api/v1/exports?resource=rate_comparisons&format=json` | 11 / 1 | phase6-1.0.0 | unit="published_age_standardised_deaths_per_100000" |
| `case_study` | `/api/v1/geography/inverclyde` | 1 / 1 | phase6-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |
| `geographic_findings` | Internal catalog/service only; no direct public route or admitted export | 1 / 1 | phase6-1.0.0 | boundary_type="council" |
| `forecast` | `/api/v1/forecasting/results`<br>`/api/v1/exports?resource=forecast&format=json` | 1 / 1 | phase2-1.0.0 | boundary_type="country" |
| `forecast_models` | `/api/v1/forecasting/models`<br>`/api/v1/exports?resource=forecast_models&format=json` | 4 / 1 | phase2-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |
| `backtest` | `/api/v1/forecasting/backtest`<br>`/api/v1/exports?resource=backtest&format=json` | 48 / 1 | phase2-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |
| `forecast_observations` | `/api/v1/forecasting/observations`<br>`/api/v1/exports?resource=forecast_observations&format=json` | 36 / 1 | phase2-1.0.0 | Not explicit at top level; inspect nested/source-specific definition |

## Exact response fields and provenance

### mortality_trends

- Artifact: `analysis/phase4/outputs/mortality_quarterly.csv`
- SHA-256: `efab0ed13958aba94b647ace3a771dfef2605e58ec47c8de4d1cd1bf92f3be75`
- Returned fields: `analysis_as_of, boundary_type, calculation_method, comparison_status, data_age_days, direction, geography, geography_id, historical_reference_mean, indicator_id, limitations, name, observed_value, ordinal, percentage_point_change, period, period_basis, period_change, period_change_pct, period_end, period_start, previous_value, publication_date, publication_lag_days, publication_status, quality_status, quarter, reference_change_pct, reference_periods, rolling_average, rolling_periods, scientific_status, share_of_national_pct, source_data_cutoff, source_geography, source_id, source_path, source_sha256, source_url, unit, year, year_change_pct, year_comparison_basis, year_reference_value`
- Definition/model values: `{"unit": ["\"count\""], "period_basis": ["\"calendar_quarter_legacy_10_day_adjustment\""], "boundary_type": ["\"country\"", "\"police_division\""]}`
- Source scope and availability: `{"geography": ["\"A: North East\"", "\"C: Forth Valley\"", "\"D: Tayside\"", "\"E: Edinburgh City\"", "\"G: Greater Glasgow\"", "\"J: The Lothians & Scottish Borders\"", "\"K: Renfrewshire and Inverclyde\"", "\"L: Argyll & West Dunbartonshire\"", "\"N: Highlands & Islands\"", "\"P: Fife\"", "\"Q: Lanarkshire\"", "\"Scotland national total\"", "\"U: Ayrshire\"", "\"V: Dumfries & Galloway\""], "source_id": ["\"police_suspected_drug_deaths_Jan2017-Dec2025.xlsx\""], "indicator_id": ["\"suspected_deaths\""], "quality_status": ["\"missing_or_suppressed\"", "\"observed\""], "publication_date": ["\"2026-03-17\""], "source_data_cutoff": ["\"2025-12-31\""]}`

### forensic

- Artifact: `analysis/phase4/outputs/forensic_counts.csv`
- SHA-256: `6a67e3f4c964c00d49ca260955141dc7ab1d83c63fccde3711fdfeedd3ef6063`
- Returned fields: `analysis_as_of, boundary_type, calculation_method, comparison_status, data_age_days, direction, geography, geography_id, historical_reference_mean, indicator_id, limitations, name, observed_value, ordinal, percentage_point_change, period, period_basis, period_change, period_change_pct, period_end, period_start, previous_value, publication_date, publication_lag_days, publication_status, quality_status, reference_change_pct, reference_periods, rolling_average, rolling_periods, scientific_status, source_data_cutoff, source_geography, source_id, source_path, source_sha256, source_url, unit, within_source_period_dense_rank, year_change_pct, year_comparison_basis, year_reference_value`
- Definition/model values: `{"unit": ["\"detection_count\""], "period_basis": ["\"calendar_quarter\""], "boundary_type": ["\"national_testing_sample\""]}`
- Source scope and availability: `{"geography": ["\"Scotland forensic testing sample\""], "source_id": ["\"radar_toxicology_forensic_2018-2026.csv\""], "indicator_id": ["\"forensic:All Benzodiazepines\"", "\"forensic:Dissociatives\"", "\"forensic:Gabapentinoids\"", "\"forensic:Opioids\"", "\"forensic:Prescribable Benzodiazepines\"", "\"forensic:Stimulants\"", "\"forensic:Street Benzodiazepines\""], "quality_status": ["\"observed\""], "publication_date": ["null"], "source_data_cutoff": ["\"2026-03-31\""]}`

### assist

- Artifact: `analysis/phase4/outputs/assist_percentages.csv`
- SHA-256: `3985a2f7abe34068a4535c5d9a2598c266c5e39a8446f8dff2fe4bfd90544cc0`
- Returned fields: `analysis_as_of, boundary_type, calculation_method, comparison_status, data_age_days, direction, geography, geography_id, historical_reference_mean, indicator_id, limitations, name, observed_value, ordinal, percentage_point_change, period, period_basis, period_change, period_change_pct, period_end, period_start, previous_value, publication_date, publication_lag_days, publication_status, quality_status, quality_status_detail, reference_change_pct, reference_periods, rolling_average, rolling_periods, scientific_status, source_data_cutoff, source_geography, source_id, source_path, source_sha256, source_url, study_period, unit, within_source_period_dense_rank, year_change_pct, year_comparison_basis, year_reference_value`
- Definition/model values: `{"unit": ["\"percent\""], "period_basis": ["\"source_study_period_not_calendar_quarter\""], "boundary_type": ["\"study_sample\""]}`
- Source scope and availability: `{"geography": ["\"ASSIST participating emergency-department sample\""], "source_id": ["\"radar_toxicology_assist.csv\""], "indicator_id": ["\"assist:Benzodiazepine\"", "\"assist:Cannabinoid\"", "\"assist:Gabapentin/Pregabalin\"", "\"assist:Opioid\"", "\"assist:Other\"", "\"assist:Stimulant\""], "quality_status": ["\"observed\""], "publication_date": ["null"], "source_data_cutoff": ["\"Q15 Feb26- May26\""]}`

### treatment

- Artifact: `analysis/phase4/outputs/treatment_counts.csv`
- SHA-256: `8ddf44fc8bb5dc5569fca13aa6e877f3bd0e45c61993e68864c0f789639c0a48`
- Returned fields: `analysis_as_of, boundary_type, calculation_method, comparison_status, data_age_days, direction, geography, geography_id, historical_reference_mean, indicator_id, limitations, name, observed_value, ordinal, percentage_point_change, period, period_basis, period_change, period_change_pct, period_end, period_start, previous_value, publication_date, publication_lag_days, publication_status, quality_status, reference_change_pct, reference_periods, rolling_average, rolling_periods, sample_type, scientific_status, source_data_cutoff, source_geography, source_id, source_path, source_sha256, source_url, unit, within_source_period_dense_rank, year_change_pct, year_comparison_basis, year_reference_value`
- Definition/model values: `{"unit": ["\"detection_count\""], "period_basis": ["\"calendar_month\""], "boundary_type": ["\"health_board\""]}`
- Source scope and availability: `{"geography": ["\"NHS Greater Glasgow and Clyde\""], "source_id": ["\"radar_toxicology_treatment_glasgow.csv\""], "indicator_id": ["\"treatment:Benzodiazepines\"", "\"treatment:Dissociatives\"", "\"treatment:Gabapentinoids\"", "\"treatment:Opioids (excluding treatment opioids)\"", "\"treatment:Stimulants\""], "quality_status": ["\"observed\""], "publication_date": ["null"], "source_data_cutoff": ["\"2026-03-31\""]}`

### naloxone

- Artifact: `analysis/phase4/outputs/naloxone_weekly.csv`
- SHA-256: `23e8c54fc42fd13c772c4fdb11268acbdb62b0562c0598ce49b035a8de7bec70`
- Returned fields: `analysis_as_of, boundary_type, calculation_method, comparison_status, data_age_days, direction, geography, geography_id, historical_reference_mean, indicator_id, limitations, name, observed_value, ordinal, percentage_point_change, period, period_basis, period_change, period_change_pct, period_end, period_start, previous_value, publication_date, publication_lag_days, publication_status, quality_status, quality_status_detail, reference_change_pct, reference_periods, reported_moving_average, rolling_average, rolling_periods, scientific_status, source_data_cutoff, source_geography, source_id, source_path, source_sha256, source_url, unit, year_change_pct, year_comparison_basis, year_reference_value`
- Definition/model values: `{"unit": ["\"incident_count\""], "period_basis": ["\"week_beginning_monday\""], "boundary_type": ["\"country\"", "\"health_board\"", "\"unknown\""]}`
- Source scope and availability: `{"geography": ["\"NHS Ayrshire & Arran\"", "\"NHS Borders\"", "\"NHS Dumfries & Galloway\"", "\"NHS Fife\"", "\"NHS Forth Valley\"", "\"NHS Grampian\"", "\"NHS Greater Glasgow & Clyde\"", "\"NHS Highland\"", "\"NHS Lanarkshire\"", "\"NHS Lothian\"", "\"NHS Orkney\"", "\"NHS Shetland\"", "\"NHS Tayside\"", "\"NHS Western Isles\"", "\"Scotland\"", "\"Unknown\""], "source_id": ["\"radar_sas_naloxone_weekly_by_board.csv\""], "indicator_id": ["\"ambulance_naloxone_activity\""], "quality_status": ["\"observed\""], "publication_date": ["null"], "source_data_cutoff": ["\"2026-05-31\""]}`

### anomalies

- Artifact: `analysis/phase5/outputs/anomaly_results.csv`
- SHA-256: `8ffff732a4f734c658d9edab95ebc4612e70bb98c8f5a40c8b167532d55e7372`
- Returned fields: `analysis_as_of, baseline_estimate, baseline_mad, boundary_type, classification, data_age_days, dataset, evidence_domain, expected_reference_observations, geography, geography_id, indicator_id, limitations, lower_threshold, method, name, observed_value, ordinal, period, period_basis, period_end, period_start, publication_date, publication_lag_days, publication_status, quality_status, quality_status_detail, reason, reference_completeness, reference_end, reference_observations, reference_start, robust_score, scale, scale_floor_active, signal_direction, source_data_cutoff, source_geography, source_id, source_path, source_sha256, source_url, substance_category, temporal_status, threshold, unit, upper_threshold, window`
- Definition/model values: `{"unit": ["\"count\"", "\"detection_count\"", "\"incident_count\"", "\"percent\""], "period_basis": ["\"calendar_month\"", "\"calendar_quarter\"", "\"calendar_quarter_legacy_10_day_adjustment\"", "\"source_study_period_not_calendar_quarter\"", "\"week_beginning_monday\""], "boundary_type": ["\"country\"", "\"health_board\"", "\"national_testing_sample\"", "\"police_division\"", "\"study_sample\"", "\"unknown\""], "method": ["\"not_estimated\"", "\"prior_complete_window_median_MAD_count_floor\""], "window": ["104", "16", "18", "null"]}`
- Source scope and availability: `{"geography": ["\"A: North East\"", "\"ASSIST participating emergency-department sample\"", "\"C: Forth Valley\"", "\"D: Tayside\"", "\"E: Edinburgh City\"", "\"G: Greater Glasgow\"", "\"J: The Lothians & Scottish Borders\"", "\"K: Renfrewshire and Inverclyde\"", "\"L: Argyll & West Dunbartonshire\"", "\"N: Highlands & Islands\"", "\"NHS Ayrshire & Arran\"", "\"NHS Borders\"", "\"NHS Dumfries & Galloway\"", "\"NHS Fife\"", "\"NHS Forth Valley\"", "\"NHS Grampian\"", "\"NHS Greater Glasgow & Clyde\"", "\"NHS Greater Glasgow and Clyde\"", "\"NHS Highland\"", "\"NHS Lanarkshire\"", "\"NHS Lothian\"", "\"NHS Orkney\"", "\"NHS Shetland\"", "\"NHS Tayside\"", "\"NHS Western Isles\"", "\"P: Fife\"", "\"Q: Lanarkshire\"", "\"Scotland forensic testing sample\"", "\"Scotland national total\"", "\"Scotland\"", "\"U: Ayrshire\"", "\"Unknown\"", "\"V: Dumfries & Galloway\""], "source_id": ["\"police_suspected_drug_deaths_Jan2017-Dec2025.xlsx\"", "\"quarterly_input_table.json\"", "\"radar_sas_naloxone_weekly_by_board.csv\"", "\"radar_toxicology_assist.csv\"", "\"radar_toxicology_forensic_2018-2026.csv\"", "\"radar_toxicology_treatment_glasgow.csv\""], "indicator_id": ["\"ambulance_naloxone_activity\"", "\"assist:Benzodiazepine\"", "\"assist:Cannabinoid\"", "\"assist:Gabapentin/Pregabalin\"", "\"assist:Opioid\"", "\"assist:Other\"", "\"assist:Stimulant\"", "\"forensic:All Benzodiazepines\"", "\"forensic:Dissociatives\"", "\"forensic:Gabapentinoids\"", "\"forensic:Opioids\"", "\"forensic:Prescribable Benzodiazepines\"", "\"forensic:Stimulants\"", "\"forensic:Street Benzodiazepines\"", "\"frozen_forensic_share:All Benzodiazepines\"", "\"frozen_forensic_share:Dissociatives\"", "\"frozen_forensic_share:Gabapentinoids\"", "\"frozen_forensic_share:Opioids\"", "\"frozen_forensic_share:Prescribable Benzodiazepines\"", "\"frozen_forensic_share:Stimulants\"", "\"frozen_forensic_share:Street Benzodiazepines\"", "\"suspected_deaths\"", "\"treatment:Benzodiazepines\"", "\"treatment:Dissociatives\"", "\"treatment:Gabapentinoids\"", "\"treatment:Opioids (excluding treatment opioids)\"", "\"treatment:Stimulants\""], "substance_category": ["\"All Benzodiazepines\"", "\"Benzodiazepine\"", "\"Benzodiazepines\"", "\"Cannabinoid\"", "\"Dissociatives\"", "\"Gabapentin/Pregabalin\"", "\"Gabapentinoids\"", "\"Opioid\"", "\"Opioids (excluding treatment opioids)\"", "\"Opioids\"", "\"Other\"", "\"Prescribable Benzodiazepines\"", "\"Stimulant\"", "\"Stimulants\"", "\"Street Benzodiazepines\"", "null"], "quality_status": ["\"missing_or_suppressed\"", "\"observed\""], "publication_date": ["\"2026-03-17\"", "null"], "source_data_cutoff": ["\"2024-12-31\"", "\"2025-12-31\"", "\"2026-03-31\"", "\"2026-05-31\"", "\"Q15 Feb26- May26\""]}`

### sensitivity

- Artifact: `analysis/phase5/outputs/sensitivity_results.csv`
- SHA-256: `50ebdf1a727d3db9ebce04edfb591aa35851e186d2a434b2db69892296213a64`
- Returned fields: `attempted_choices, boundary_type, dataset, eligible_choices, geography, geography_id, indicator_id, missing_or_short_window_choices, name, period, period_basis, primary_classification, primary_direction, signal_choices, signal_fraction, source_geography, stability`
- Definition/model values: `{"period_basis": ["\"calendar_month\"", "\"calendar_quarter\"", "\"calendar_quarter_legacy_10_day_adjustment\"", "\"week_beginning_monday\""], "boundary_type": ["\"country\"", "\"health_board\"", "\"national_testing_sample\"", "\"police_division\"", "\"unknown\""]}`
- Source scope and availability: `{"geography": ["\"A: North East\"", "\"C: Forth Valley\"", "\"D: Tayside\"", "\"E: Edinburgh City\"", "\"G: Greater Glasgow\"", "\"J: The Lothians & Scottish Borders\"", "\"K: Renfrewshire and Inverclyde\"", "\"L: Argyll & West Dunbartonshire\"", "\"N: Highlands & Islands\"", "\"NHS Ayrshire & Arran\"", "\"NHS Borders\"", "\"NHS Dumfries & Galloway\"", "\"NHS Fife\"", "\"NHS Forth Valley\"", "\"NHS Grampian\"", "\"NHS Greater Glasgow & Clyde\"", "\"NHS Greater Glasgow and Clyde\"", "\"NHS Highland\"", "\"NHS Lanarkshire\"", "\"NHS Lothian\"", "\"NHS Orkney\"", "\"NHS Shetland\"", "\"NHS Tayside\"", "\"NHS Western Isles\"", "\"P: Fife\"", "\"Q: Lanarkshire\"", "\"Scotland forensic testing sample\"", "\"Scotland national total\"", "\"Scotland\"", "\"U: Ayrshire\"", "\"Unknown\"", "\"V: Dumfries & Galloway\""], "indicator_id": ["\"ambulance_naloxone_activity\"", "\"forensic:All Benzodiazepines\"", "\"forensic:Dissociatives\"", "\"forensic:Gabapentinoids\"", "\"forensic:Opioids\"", "\"forensic:Prescribable Benzodiazepines\"", "\"forensic:Stimulants\"", "\"forensic:Street Benzodiazepines\"", "\"suspected_deaths\"", "\"treatment:Benzodiazepines\"", "\"treatment:Dissociatives\"", "\"treatment:Gabapentinoids\"", "\"treatment:Opioids (excluding treatment opioids)\"", "\"treatment:Stimulants\""]}`

### enhanced

- Artifact: `analysis/phase5c/outputs/enhanced_model_results.csv`
- SHA-256: `c091d460dd8a9c49753323491755f292adbb1ffb1bb49ba2dbddef6d80590359`
- Returned fields: `boundary_type, covered95, covered99, dataset, diagnostic_interpretation, direction, dispersion, error, geography, geography_id, half_window_mean_change, indicator_id, interpretation, interval_score95, lag1_correlation, linear_slope, lower95, lower99, mean, method, name, negative_log_score, notes, observation_id, observed_value, ordinal, period, period_basis, poisson_expected_zero, predicted, reference_end, reference_start, seasonal_lag_correlation, signal, source_geography, source_path, source_sha256, status, upper95, upper99, variance, window, zero_fraction`
- Definition/model values: `{"period_basis": ["\"calendar_month\"", "\"calendar_quarter\"", "\"calendar_quarter_legacy_10_day_adjustment\"", "\"week_beginning_monday\""], "boundary_type": ["\"country\"", "\"health_board\"", "\"national_testing_sample\"", "\"police_division\"", "\"unknown\""], "method": ["\"gamma_poisson\"", "\"nb2_moments\"", "\"seasonal_gamma_poisson\"", "\"trend_poisson\""], "window": ["104", "16", "18", "208"]}`
- Source scope and availability: `{"geography": ["\"A: North East\"", "\"C: Forth Valley\"", "\"D: Tayside\"", "\"E: Edinburgh City\"", "\"G: Greater Glasgow\"", "\"J: The Lothians & Scottish Borders\"", "\"K: Renfrewshire and Inverclyde\"", "\"L: Argyll & West Dunbartonshire\"", "\"N: Highlands & Islands\"", "\"NHS Ayrshire & Arran\"", "\"NHS Borders\"", "\"NHS Dumfries & Galloway\"", "\"NHS Fife\"", "\"NHS Forth Valley\"", "\"NHS Grampian\"", "\"NHS Greater Glasgow & Clyde\"", "\"NHS Greater Glasgow and Clyde\"", "\"NHS Highland\"", "\"NHS Lanarkshire\"", "\"NHS Lothian\"", "\"NHS Orkney\"", "\"NHS Shetland\"", "\"NHS Tayside\"", "\"NHS Western Isles\"", "\"P: Fife\"", "\"Q: Lanarkshire\"", "\"Scotland forensic testing sample\"", "\"Scotland national total\"", "\"Scotland\"", "\"U: Ayrshire\"", "\"Unknown\"", "\"V: Dumfries & Galloway\""], "indicator_id": ["\"ambulance_naloxone_activity\"", "\"forensic:All Benzodiazepines\"", "\"forensic:Dissociatives\"", "\"forensic:Gabapentinoids\"", "\"forensic:Opioids\"", "\"forensic:Prescribable Benzodiazepines\"", "\"forensic:Stimulants\"", "\"forensic:Street Benzodiazepines\"", "\"suspected_deaths\"", "\"treatment:Benzodiazepines\"", "\"treatment:Dissociatives\"", "\"treatment:Gabapentinoids\"", "\"treatment:Opioids (excluding treatment opioids)\"", "\"treatment:Stimulants\""], "status": ["\"insufficient_data\"", "\"not_applicable\"", "\"ok\"", "\"unavailable_observation\""]}`

### diagnostics

- Artifact: `analysis/phase5c/outputs/statistical_diagnostics.csv`
- SHA-256: `bc6c8398799e0bd3a399080ae7f37b2c4b61724e885b0014b1cc91f868ac201e`
- Returned fields: `boundary_type, covered95, covered99, dataset, diagnostic_interpretation, direction, dispersion, error, geography, geography_id, half_window_mean_change, indicator_id, interpretation, interval_score95, lag1_correlation, linear_slope, lower95, lower99, mean, method, name, negative_log_score, notes, observation_id, observed_value, ordinal, period, period_basis, poisson_expected_zero, predicted, reference_end, reference_start, seasonal_lag_correlation, signal, source_geography, source_path, source_sha256, status, upper95, upper99, variance, window, zero_fraction`
- Definition/model values: `{"period_basis": ["\"calendar_month\"", "\"calendar_quarter\"", "\"calendar_quarter_legacy_10_day_adjustment\"", "\"week_beginning_monday\""], "boundary_type": ["\"country\"", "\"health_board\"", "\"national_testing_sample\"", "\"police_division\"", "\"unknown\""], "method": ["\"gamma_poisson\"", "\"nb2_moments\"", "\"seasonal_gamma_poisson\"", "\"trend_poisson\""], "window": ["104", "16", "18", "208"]}`
- Source scope and availability: `{"status": ["\"insufficient_data\"", "\"ok\""]}`

### model_metrics

- Artifact: `analysis/phase5c/outputs/model_evaluation_metrics.csv`
- SHA-256: `00d167a93bfe9add0c72b3c7d5981aea1603f79fb44a5d04ed067c334a7e8dee`
- Returned fields: `available_origins, boundary_type, common_participants, coverage95, coverage99, dataset, evaluated, evaluation_scope, geography, geography_id, indicator_id, mae, mean_interval_score95, mean_negative_log_score, mean_width95, method, name, rmse, selection, signal_frequency99, signals99, source_geography`
- Definition/model values: `{"boundary_type": ["\"country\"", "\"health_board\"", "\"national_testing_sample\"", "\"police_division\"", "\"unknown\""], "method": ["\"gamma_poisson\"", "\"nb2_moments\"", "\"seasonal_gamma_poisson\"", "\"trend_poisson\""]}`
- Source scope and availability: `{"geography": ["\"A: North East\"", "\"C: Forth Valley\"", "\"D: Tayside\"", "\"E: Edinburgh City\"", "\"G: Greater Glasgow\"", "\"J: The Lothians & Scottish Borders\"", "\"K: Renfrewshire and Inverclyde\"", "\"L: Argyll & West Dunbartonshire\"", "\"N: Highlands & Islands\"", "\"NHS Ayrshire & Arran\"", "\"NHS Borders\"", "\"NHS Dumfries & Galloway\"", "\"NHS Fife\"", "\"NHS Forth Valley\"", "\"NHS Grampian\"", "\"NHS Greater Glasgow & Clyde\"", "\"NHS Greater Glasgow and Clyde\"", "\"NHS Highland\"", "\"NHS Lanarkshire\"", "\"NHS Lothian\"", "\"NHS Orkney\"", "\"NHS Shetland\"", "\"NHS Tayside\"", "\"NHS Western Isles\"", "\"P: Fife\"", "\"Q: Lanarkshire\"", "\"Scotland forensic testing sample\"", "\"Scotland national total\"", "\"Scotland\"", "\"U: Ayrshire\"", "\"Unknown\"", "\"V: Dumfries & Galloway\""], "indicator_id": ["\"ambulance_naloxone_activity\"", "\"forensic:All Benzodiazepines\"", "\"forensic:Dissociatives\"", "\"forensic:Gabapentinoids\"", "\"forensic:Opioids\"", "\"forensic:Prescribable Benzodiazepines\"", "\"forensic:Stimulants\"", "\"forensic:Street Benzodiazepines\"", "\"suspected_deaths\"", "\"treatment:Benzodiazepines\"", "\"treatment:Dissociatives\"", "\"treatment:Gabapentinoids\"", "\"treatment:Opioids (excluding treatment opioids)\"", "\"treatment:Stimulants\""]}`

### runs

- Artifact: `analysis/phase5c/outputs/signal_runs.json`
- SHA-256: `8b7b38df6639437c6eaeab428178361a58a54a67a4cad4eff2553ad50701aba9`
- Returned fields: `boundary_type, classification, configuration, dataset, deviation_unit, direction, duration_periods, end, geography, geography_id, indicator_id, method, name, observation_ids, peak_deviation, peak_period, period_basis, scientific_status, source_geography, start`
- Definition/model values: `{"period_basis": ["\"calendar_month\"", "\"calendar_quarter\"", "\"calendar_quarter_legacy_10_day_adjustment\"", "\"week_beginning_monday\""], "boundary_type": ["\"country\"", "\"health_board\"", "\"national_testing_sample\"", "\"police_division\"", "\"unknown\""], "method": ["\"gamma_poisson\"", "\"nb2_moments\"", "\"phase5_robust\"", "\"seasonal_gamma_poisson\"", "\"trend_poisson\""]}`
- Source scope and availability: `{"geography": ["\"A: North East\"", "\"C: Forth Valley\"", "\"D: Tayside\"", "\"E: Edinburgh City\"", "\"G: Greater Glasgow\"", "\"K: Renfrewshire and Inverclyde\"", "\"NHS Ayrshire & Arran\"", "\"NHS Borders\"", "\"NHS Dumfries & Galloway\"", "\"NHS Fife\"", "\"NHS Forth Valley\"", "\"NHS Grampian\"", "\"NHS Greater Glasgow & Clyde\"", "\"NHS Greater Glasgow and Clyde\"", "\"NHS Highland\"", "\"NHS Lanarkshire\"", "\"NHS Lothian\"", "\"NHS Orkney\"", "\"NHS Shetland\"", "\"NHS Tayside\"", "\"NHS Western Isles\"", "\"Scotland forensic testing sample\"", "\"Scotland national total\"", "\"Scotland\"", "\"U: Ayrshire\"", "\"Unknown\"", "\"V: Dumfries & Galloway\""], "indicator_id": ["\"ambulance_naloxone_activity\"", "\"forensic:All Benzodiazepines\"", "\"forensic:Dissociatives\"", "\"forensic:Gabapentinoids\"", "\"forensic:Opioids\"", "\"forensic:Prescribable Benzodiazepines\"", "\"forensic:Stimulants\"", "\"forensic:Street Benzodiazepines\"", "\"suspected_deaths\"", "\"treatment:Benzodiazepines\"", "\"treatment:Dissociatives\"", "\"treatment:Gabapentinoids\"", "\"treatment:Opioids (excluding treatment opioids)\"", "\"treatment:Stimulants\""]}`

### evidence

- Artifact: `analysis/phase5c/outputs/cross_source_evidence.json`
- SHA-256: `09c3465a7fc09c6fb2b51b4be162b4ca4413b7f1b3e5596a93c20f450e422012`
- Returned fields: `classification, comparison_id, compatibility, current_threat, left_state, limitation, method, observation_ids, period, related_geography_ids, retrospective_only, right_state`
- Definition/model values: `{"method": ["\"nb2_moments\"", "\"phase5_robust\""]}`
- Source scope and availability: `{}`

### candidates

- Artifact: `analysis/phase5c/outputs/cross_source_candidates.json`
- SHA-256: `bf9b5d7d835251e6f5087469a86a5758e6ab7b9e66a78a3bdc08d0421517197d`
- Returned fields: `boundary_type, comparison_id, geography, geography_id, historical_availability, independence, left_dataset, left_geography, left_indicator, left_observation_id, left_period, left_state, measurement, name, reason, right_dataset, right_geography, right_indicator, right_observation_id, right_period, right_state, shared_cases, source_geography, status, substance, temporal`
- Definition/model values: `{"boundary_type": ["\"unknown\""]}`
- Source scope and availability: `{"geography": ["\"exact\"", "\"incompatible\"", "\"national_sample_context_only\"", "\"unresolved\""], "status": ["\"compatible_contextual_evidence\"", "\"incompatible\"", "\"unresolved_mapping\""]}`

### zero_baseline

- Artifact: `analysis/phase5c/outputs/zero_baseline_review.json`
- SHA-256: `43b78b5f3619ae9f0703524c369fd9ea67059cb5b689095865aa0aa45c84e809`
- Returned fields: `geographic_interpretation, models, observation_id, observed, period, phase5_bounds, phase5_median`
- Definition/model values: `{}`
- Source scope and availability: `{}`

### summary

- Artifact: `analysis/phase5c/outputs/summary.json`
- SHA-256: `2e3143ced65ebb25ccc71b144706ab8d76654e43f8bb666bd7a62af08fc7e459`
- Returned fields: `compatibility, cross_source_candidates, evidence_by_method, foi, future_forecasts, interpretation, model_signals, model_statuses, observations, original_primary_flags, original_runs, sustained_original_runs`
- Definition/model values: `{}`
- Source scope and availability: `{}`

### registry

- Artifact: `analysis/phase5c/outputs/source_compatibility_registry.json`
- SHA-256: `21ce312452895895f9baffbc840af8c4510362ec62605ea8b17fdd28f93e037a`
- Returned fields: `boundary_rule, completeness, dataset, denominator, first_period, geographic_scope_metadata, geographies, indicator_definitions, last_period, limitations, period_basis, possible_dependence, publication_date, reporting_lag, source_data_cutoff, source_id, source_path, source_population, source_sha256, source_url, substances, units`
- Definition/model values: `{"period_basis": ["\"calendar_month\"", "\"calendar_quarter\"", "\"calendar_quarter_legacy_10_day_adjustment\"", "\"source_study_period_not_calendar_quarter\"", "\"week_beginning_monday\""]}`
- Source scope and availability: `{"source_id": ["\"police_suspected_drug_deaths_Jan2017-Dec2025.xlsx\"", "\"quarterly_input_table.json\"", "\"radar_sas_naloxone_weekly_by_board.csv\"", "\"radar_toxicology_assist.csv\"", "\"radar_toxicology_forensic_2018-2026.csv\"", "\"radar_toxicology_treatment_glasgow.csv\""], "source_population": ["\"ASSIST participating emergency-department sample\"", "\"NHS Greater Glasgow and Clyde\"", "\"Scotland forensic testing sample\"", "\"Separate national and regional operational aggregates\""], "publication_date": ["\"2026-03-17\"", "null"], "source_data_cutoff": ["\"2024-12-31\"", "\"2025-12-31\"", "\"2026-03-31\"", "\"2026-05-31\"", "\"Q15 Feb26- May26\""]}`

### gaps

- Artifact: `analysis/phase5c/outputs/source_gap_register.json`
- SHA-256: `ce51b69980f2ebe8330db79d77b649eb324c6cfe25272a29498ecc454f3af8a5`
- Returned fields: `affected_analysis, available_workaround, gap, interpretation_consequence, potential_official_source, status`
- Definition/model values: `{}`
- Source scope and availability: `{"status": ["\"partially_resolved\"", "\"unresolved\""]}`

### annual

- Artifact: `analysis/phase6/outputs/validated_geographic_observations.csv`
- SHA-256: `c7e0fb4b7cbcc2c4baa15be0466f2a48f007dd6381022ee746bed849ca1a3ac3`
- Returned fields: `boundary_type, geography, geography_id, greenock_inference, indicator_id, name, observed_value, period_basis, period_end, period_start, publication_date, quality_status, scientific_status, sex, small_number_qualification, source_cell, source_data_cutoff, source_geography, source_path, source_raw_value, source_sha256, source_sheet, source_url, unit, year`
- Definition/model values: `{"unit": ["\"deaths\""], "period_basis": ["\"calendar_year_of_registration\""], "boundary_type": ["\"council\"", "\"country\""]}`
- Source scope and availability: `{"geography": ["\"Inverclyde\"", "\"Scotland\""], "indicator_id": ["\"nrs_registered_drug_misuse_deaths\""], "quality_status": ["\"observed\""], "publication_date": ["\"2025-09-02\""], "source_data_cutoff": ["\"2024-12-31\""]}`

### geographic_trends

- Artifact: `analysis/phase6/outputs/inverclyde_trends.csv`
- SHA-256: `7411f6f3f00775dc6b7e6b21254571410c855bff4e58b09ff4e747c3c063baf0`
- Returned fields: `annual_change, annual_change_pct, boundary_type, change_10y, change_10y_pct, change_3y, change_3y_pct, change_5y, change_5y_pct, change_since_2010, change_since_2010_pct, direction, geography, geography_id, greenock_inference, indicator_id, interpretation, name, observed_value, one_death_pct_of_previous, period_basis, period_end, period_start, previous_value, publication_date, quality_status, reference_10y, reference_3y, reference_5y, rolling_3y_complete, rolling_3y_mean, rolling_5y_complete, rolling_5y_mean, rolling_method, scientific_status, sex, small_number_qualification, source_cell, source_data_cutoff, source_geography, source_path, source_raw_value, source_sha256, source_sheet, source_url, unit, year`
- Definition/model values: `{"unit": ["\"deaths\""], "period_basis": ["\"calendar_year_of_registration\""], "boundary_type": ["\"council\""]}`
- Source scope and availability: `{"geography": ["\"Inverclyde\""], "indicator_id": ["\"nrs_registered_drug_misuse_deaths\""], "quality_status": ["\"observed\""], "publication_date": ["\"2025-09-02\""], "source_data_cutoff": ["\"2024-12-31\""]}`

### comparisons

- Artifact: `analysis/phase6/outputs/registered_scotland_comparisons.csv`
- SHA-256: `c7a155a8c631848f9a3bbd4f050c93ad449fd0e78a143adbf08e50acffd7e369`
- Returned fields: `direction_agreement, indicator_id, interpretation, inverclyde_deaths, inverclyde_index_2010, inverclyde_share_of_scotland_pct, local_annual_change_pct, local_boundary, local_geography, national_boundary, national_geography, period_basis, scotland_annual_change_pct, scotland_deaths, scotland_index_2010, source_cells, source_sha256, year`
- Definition/model values: `{"period_basis": ["\"calendar_year_of_registration\""]}`
- Source scope and availability: `{"indicator_id": ["\"nrs_registered_drug_misuse_deaths\""]}`

### rates

- Artifact: `analysis/phase6/outputs/published_five_year_rates.csv`
- SHA-256: `f5982b36885c7a18bcd1802cf5b64109cba1dd409a1721c78b4e301de7e4c401`
- Returned fields: `boundary_type, end_year, geography, geography_id, greenock_inference, indicator_id, lower95, name, period_basis, period_end, period_label, period_start, publication_date, qualification, quality_status, rate, rate_origin, scientific_status, source_cells, source_data_cutoff, source_geography, source_path, source_raw_lower95, source_raw_rate, source_raw_upper95, source_row, source_sha256, source_sheet, source_url, standard_population, start_year, total_check, total_deaths, unit, upper95`
- Definition/model values: `{"unit": ["\"published_age_standardised_deaths_per_100000\""], "period_basis": ["\"five_year_registration_period\""], "boundary_type": ["\"council\"", "\"country\""], "standard_population": ["\"2013 European Standard Population\""], "rate_origin": ["\"NRS published; not recalculated or back-solved from total counts\""]}`
- Source scope and availability: `{"geography": ["\"Inverclyde\"", "\"Scotland\""], "indicator_id": ["\"nrs_registered_drug_misuse_deaths\""], "quality_status": ["\"published\""], "publication_date": ["\"2025-09-02\""], "source_data_cutoff": ["\"2024-12-31\""]}`

### rate_comparisons

- Artifact: `analysis/phase6/outputs/published_rate_comparisons.csv`
- SHA-256: `8ab5e227f66fe49e21d6e0e008215d1bfb3b8d671c37f5b02c964be0f6e23dd2`
- Returned fields: `descriptive_rate_ratio, interpretation, inverclyde_lower95, inverclyde_rate, inverclyde_upper95, period_end, period_label, period_start, rate_difference, scotland_lower95, scotland_rate, scotland_upper95, source_rows, source_sha256, standard_population, unit`
- Definition/model values: `{"unit": ["\"published_age_standardised_deaths_per_100000\""], "standard_population": ["\"2013 European Standard Population\""]}`
- Source scope and availability: `{}`

### case_study

- Artifact: `analysis/phase6/outputs/dashboard_data_contract.json`
- SHA-256: `da4a88f40bcc6771cb4a60b633c033bf31eb0986987dc046e8abec703713315b`
- Returned fields: `annual_count_series, annual_crude_rates, default_geography, display_rules, findings, greenock, hierarchy, matched_annual_comparisons, public_or_database_write, published_five_year_rates, published_rate_comparisons, required_labels, schema_version, source, status, title`
- Definition/model values: `{}`
- Source scope and availability: `{"status": ["\"local_dashboard_ready_not_deployed\""]}`

### geographic_findings

- Artifact: `analysis/phase6/outputs/research_findings.json`
- SHA-256: `b37d2147182ecb12ce1b7b375eafac2916562355e805a4ed5a4f6f2212959dfe`
- Returned fields: `analysis_as_of, boundary_type, different_direction_years, extrema, geography, geography_id, historical_not_current, indicator_id, latest, latest_published_rate_comparison, limitations, local_anomaly_feasibility, matched_scotland_latest, name, nonoverlapping_five_year_blocks, publication_date, source_data_cutoff, source_geography, validated_annual_counts`
- Definition/model values: `{"boundary_type": ["\"council\""]}`
- Source scope and availability: `{"geography": ["\"Inverclyde\""], "indicator_id": ["\"nrs_registered_drug_misuse_deaths\""], "publication_date": ["\"2025-09-02\""], "source_data_cutoff": ["\"2024-12-31\""]}`

### forecast

- Artifact: `analysis/outputs/forecast.json`
- SHA-256: `d1e28adf528bd7f93bae20a74896144372d807efd3fae838753a673d604774df`
- Returned fields: `boundary_type, diagnostics, forecast_origin, geography, geography_id, horizon_quarters, interpretation, interval_method, issued_at_utc, lower80, lower95, model, name, outcome, predicted, source_geography, target_period, upper80, upper95, warnings`
- Definition/model values: `{"boundary_type": ["\"country\""], "model": ["\"naive\""], "target_period": ["\"2026 Q1\""], "forecast_origin": ["\"2025 Q4\""]}`
- Source scope and availability: `{"geography": ["\"Scotland national total\""], "outcome": ["\"Police Scotland suspected drug deaths\""]}`

### forecast_models

- Artifact: `analysis/outputs/model_metrics.json`
- SHA-256: `acaa7b3a8c39f21be58266fa5affd4109f0f1f2d0730170f98766cbe67954c49`
- Returned fields: `coverage80, coverage95, eligible_for_selection, evaluated_origins, failed_origins, interval_score95, mae, mae_skill_vs_naive, mae_skill_vs_seasonal_naive, mase, mean_width95, model, rmse, rmsse, scaled_origins`
- Definition/model values: `{"model": ["\"naive\"", "\"nb2_trend\"", "\"seasonal_naive\"", "\"ses\""]}`
- Source scope and availability: `{}`

### backtest

- Artifact: `analysis/outputs/rolling_origin_predictions.csv`
- SHA-256: `28ba9526cc934519f4c5d7c1bb7730bcfe727a15116e4dcb51d2971da5d4a38a`
- Returned fields: `actual, diagnostics, horizon, interval_method, lower80, lower95, mase_scale, model, origin, predicted, rmsse_scale_squared, status, target, training_count, upper80, upper95, warnings`
- Definition/model values: `{"model": ["\"naive\"", "\"nb2_trend\"", "\"seasonal_naive\"", "\"ses\""], "horizon": ["1"]}`
- Source scope and availability: `{"status": ["\"ok\""]}`

### forecast_observations

- Artifact: `analysis/outputs/validated_mortality.csv`
- SHA-256: `8466413fae42235d90b117e437b8e0bb0db58d2cbaa314d8f95efb82882a8868`
- Returned fields: `quarter, suspected_deaths, year`
- Definition/model values: `{}`
- Source scope and availability: `{}`

## Database, metadata and dynamic routes

| Endpoint | Existing contract / scope |
|---|---|
| `/mortality/quarterly` | Reviewed DB projection; national police counts; 36 live rows verified separately. |
| `/monitoring/configurations` | Reviewed DB projection; 4 configurations; parameters preserved via ordered value fingerprint. |
| `/monitoring/results` | Reviewed DB projection; 76 results; signed statistics and nullable limits/CUSUM fields. |
| `/health` | API health only; explicitly does not prove DB health. |
| `/overview` | Composite live DB/artifact state; independent resource failures, not one homogeneous observation list. |
| `/geographies` | 33 scopes, including unavailable Greenock; registry, not boundary geometry. |
| `/geographies/{id}` | One registry profile or rejected unknown identity. |
| `/geographies/{id}/{section}` | sections: indicators, trends, anomalies, evidence, comparisons; source/boundary-aware service selection. Comparisons require admitted compatible peers. |
| `/indicators` | Definitions assembled from six source families; units and period bases retained. |
| `/sources`, `/sources/gaps` | Compatibility metadata and evidence gaps; not observed outcomes. |
| `/methodology`, `/validation/status`, `/reports` | Research limitations, validation status and report metadata. |

All paths above have `/api/v1` prefix. Full parameter names, types, response schemas, route enums and export allowlist are in `openapi.json`. Dynamic area outputs are selection-dependent; their counts are not one fixed dataset. See `database-verification.json` for projected fields and live checks. No Phase 9 route is admitted.
