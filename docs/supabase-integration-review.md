# Public research integration review — 9 November 2026

Historical pre-approval review. Phase 1 subsequently confirmed anonymous read access to these three tables; see `dashboard-phase-1.md`. The pending-approval statements below describe the earlier stage. Do not reapply the historical migration automatically.

Status: local implementation complete; proposed migration NOT applied. No deployment or production permission/data changes are authorized by this document.

## Reviewed live scope

Read-only CLI queries inspected columns, nullability, keys/checks, anonymous grants, existing aggregate records, all four configurations and every distinct text value across 76 indicator results. No case-level records, personal identifiers, contact details, or credentials were found in these three tables. This is a review of current content, not a guarantee about future inserts or an independent validation of research methods.

| Table | Current records and columns | Constraints |
| --- | --- | --- |
| mortality_quarterly | 36 quarterly observations, 2017–2025; year, quarter, suspected_deaths, source_id. Counts range 222–413. No text columns. | PK (year, quarter); quarter 1–4; year 2000–2100; deaths >= 0; source_id FK to data_sources. |
| indicator_configurations | 4 configurations; configuration_id, indicator_name, configuration_label, method, baseline_description, rolling_window_quarters, lambda_value, limit_multiplier, lower_limit, upper_limit, cusum_k_sigma, cusum_h_sigma, notes. | PK configuration_id; unique (indicator_name, configuration_label); positive rolling window and limit multiplier when present; lambda in (0,1]. |
| indicator_results | 76 outputs, 2019–2025, one signal; result_id, configuration_id, observation_year, observation_quarter, statistic_value, lower_limit, upper_limit, signal_flag, computation_reference, cusum_positive, cusum_negative. | PK result_id; configuration_id FK to indicator_configurations; unique configuration/year/quarter; quarter 1–4; year 2000–2100. |

Nullable columns: mortality source_id; configuration baseline_description, all numeric tuning fields and notes; result limits, computation_reference and CUSUM components. Remaining columns are non-null.

## Text review

Configuration names/labels/methods describe Mortality EWMA (NB2-EWMA) at 8-, 12-, and 16-quarter rolling windows and an opioid-share CUSUM. Baseline descriptions describe rolling trend-only NB2 models or a forensic opioid-involvement share requiring baseline verification.

Configuration notes: configurations 1 and 2 say “Retrospective configuration; no signals reported.” Configuration 3 says “One reported signal in 2022 Q3.” Configuration 4 says “Parameters specified; computed quarterly outputs not yet verified.” These are public methodology caveats, not personal information. The UI preserves them; no scientific validation is claimed.

All result text is in computation_reference: 72 rows reference recomputed NB2 rolling one-step prediction and a methodology README; four reference recomputed two-sided opioid-share CUSUM, baseline 2022Q1–2023Q4, K=0.5 SD, H=4.77 SD, reset at 2024Q1. No other result text fields exist.

## Proposed access (manual review required)

Review `supabase/migrations/202611090001_public_research_reads.sql` in VS Code before running it manually in the intended project's SQL Editor. Do not run `db push` automatically. The transaction adds exactly three SELECT policies, to anon only, and explicitly retains RLS. Existing SELECT grants suffice. No other tables, roles, write policies or grants are opened.

Policies use USING (true), so all rows/columns of these three reviewed tables, including future rows, become readable through existing SELECT privileges. Explicit frontend column lists minimize downloads but are not column security. Keep these tables limited to public aggregates/model metadata; review future free-text additions. The other eight tables, particularly radar_intelligence, remain inaccessible through this proposal.

Anonymous INSERT, UPDATE, DELETE grants already exist on all three reviewed tables. Recommend revoking those privileges separately; the exact recommendation is commented at the end of the migration and is not executed. No write policy is proposed. Audit other roles/privileges separately before broader hardening.

## Local verification

Run `npm test` and `npm run build` from the repository root. No test command existed previously; `npm test` now uses Node's built-in test runner with simulated SDK responses for error, empty/RLS, pagination, ordering and relation handling. Fixtures exist only in tests; application code fetches live Supabase records.

Run `npm run dev` for the responsive verification page. Before policy approval, expect three separate “0 accessible records” states, not a successful load. After manually applying reviewed policies, reload and verify current counts (36, 4, 76), chronological mortality previews and configuration labels on results. Counts are not hard-coded in the application. A real successful anonymous read remains unverified until policies are applied. The UI previews up to eight rows per dataset while reporting the complete returned count.

No backend or framework was added. The root application uses the publishable key with the Supabase JS client; no service-role key is used. Data is rendered with textContent, not database-supplied HTML. g3-indicator remains reference material.
