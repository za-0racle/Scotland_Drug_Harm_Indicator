# Task 08B — deployed database metadata verification matrix

Live verification used existing publishable/anon read access; no permissions were broadened. The PostgREST metadata root returned **HTTP 401**. It was not bypassed. Credentials, project hostnames, raw response errors and RADAR narratives are not recorded.

| Expected table | Current existence evidence | Accessible projection | Keys, constraints, indexes and policy definitions |
|---|---|---|---|
| `mortality_quarterly` | Verified SELECT; **36 rows** | `year, quarter, suspected_deaths` | Unverified deployed DDL; year/quarter unique in observed projection |
| `indicator_configurations` | Verified SELECT; **4 rows** | 13 projected fields, listed below | Unverified deployed DDL; configuration ID unique in observed projection |
| `indicator_results` | Verified SELECT; **76 rows** | 11 projected fields, listed below | Unverified deployed DDL; configuration/year/quarter unique in observed projection |
| `data_sources` | Unverified | Not queried outside reviewed table scope | Unverified |
| `forensic_toxicology` | Unverified | Not queried outside reviewed table scope | Unverified |
| `assist_toxicology` | Unverified | Not queried outside reviewed table scope | Unverified |
| `radar_intelligence` | Unverified | No narratives queried | Unverified |
| `radar_alerts` | Unverified | Not queried outside reviewed table scope | Unverified |
| `naloxone_activity` | Unverified | Not queried outside reviewed table scope | Unverified |
| `population_estimates` | Unverified | Not queried outside reviewed table scope | Unverified |
| `geographic_areas` | Unverified | Not queried outside reviewed table scope | Unverified |

Configuration projection: `configuration_id, indicator_name, configuration_label, method, baseline_description, rolling_window_quarters, lambda_value, limit_multiplier, lower_limit, upper_limit, cusum_k_sigma, cusum_h_sigma, notes`.

Result projection: `result_id, configuration_id, observation_year, observation_quarter, statistic_value, lower_limit, upper_limit, signal_flag, cusum_positive, cusum_negative, computation_reference`.

`database-verification.json` records actual returned JSON types, null-bearing fields, candidate-key checks, ordered projection fingerprints and configuration identities. JSON types are **not SQL type declarations**. An integer in a response does not prove a PostgreSQL integer column; observed uniqueness does not prove a deployed UNIQUE constraint. Read success proves accessible rows under the current credential, not the actual policy predicate or absence of broader grants.

The database API adds fields to these projections: national mortality geography, boundary, indicator, unit, period and period basis; results additionally join `configuration_label`. It returns the ordinary Envelope with `kind=database_observation`, table/storage/limitation metadata, and `analytical_version=null`. DB endpoints use the common offset/limit envelope. Mortality implements national boundary/year filtering; do not assume configuration/results implement every filter accepted by the shared query schema.

Historical evidence in `docs/supabase-integration-review.md` describes mortality/configuration/result key and check constraints. The repository's public-read SQL is explicitly proposed; forecast SQL is design-only. Neither establishes current deployment. No authoritative complete deployed schema dump was found.

Future verification should use an already authorised metadata export or DBA-provided schema/policy listing. No permission change is requested or performed by this task. Unverified tables must not be described as absent.
