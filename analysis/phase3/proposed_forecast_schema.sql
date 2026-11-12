-- DESIGN ONLY. NOT A MIGRATION. DO NOT EXECUTE OR ADD TO AN AUTOMATIC PUSH.
-- No existing objects or policies are altered. Publication/access needs review.
begin;
create schema forecast_research;
revoke all on schema forecast_research from public, anon, authenticated;

create table forecast_research.sources (
  source_id uuid primary key,
  source_url text not null,
  publication_date date,
  retrieved_at timestamptz not null,
  data_cutoff date not null,
  content_sha256 text not null check (content_sha256 ~ '^[0-9a-f]{64}$'),
  period_basis text not null,
  outcome_definition text not null,
  geography text not null,
  revision_notes text,
  unique(source_url, content_sha256)
);
create table forecast_research.runs (
  run_id uuid primary key,
  model_id text not null,
  model_version text not null,
  parameters jsonb not null,
  outcome text not null,
  geography text not null,
  training_start date not null,
  training_end date not null check (training_end >= training_start),
  origin_period date not null check (origin_period = date_trunc('quarter',origin_period)::date),
  source_data_cutoff date not null,
  executed_at timestamptz not null,
  forecast_issued_at timestamptz,
  run_kind text not null check (run_kind in ('development_backtest','retrospective_later_evaluation','elapsed_projection','future_issued')),
  selection_reference uuid references forecast_research.runs(run_id),
  code_sha256 text not null check (code_sha256 ~ '^[0-9a-f]{64}$'),
  manifest jsonb not null,
  review_status text not null default 'draft' check (review_status in ('draft','reviewed','approved_for_publication')),
  unique(run_id, origin_period),
  check (training_end <= source_data_cutoff),
  check (source_data_cutoff < (origin_period + interval '3 months')::date)
);
create table forecast_research.run_sources (
  run_id uuid references forecast_research.runs(run_id),
  source_id uuid references forecast_research.sources(source_id),
  primary key(run_id, source_id)
);
create table forecast_research.forecast_values (
  forecast_id uuid primary key,
  run_id uuid not null,
  origin_period date not null,
  target_period date not null,
  horizon_quarters integer not null check (horizon_quarters > 0),
  point_value numeric not null check (point_value >= 0),
  interpretation text not null,
  foreign key(run_id,origin_period) references forecast_research.runs(run_id,origin_period),
  check (target_period = (origin_period + make_interval(months => 3*horizon_quarters))::date),
  unique(run_id, target_period)
);
create table forecast_research.intervals (
  forecast_id uuid references forecast_research.forecast_values(forecast_id),
  nominal_coverage numeric not null check (nominal_coverage > 0 and nominal_coverage < 1),
  lower_value numeric not null check (lower_value >= 0),
  upper_value numeric not null check (upper_value >= lower_value),
  method text not null,
  assumptions text not null,
  primary key(forecast_id, nominal_coverage)
);
create table forecast_research.evaluations (
  evaluation_id uuid primary key,
  selected_run_id uuid not null references forecast_research.runs(run_id),
  evaluation_kind text not null check (evaluation_kind in ('development','later_retrospective','prospective')),
  evaluated_at timestamptz not null,
  sample_size integer not null check (sample_size > 0),
  mae numeric check (mae >= 0),
  rmse numeric check (rmse >= 0),
  scaled_metrics jsonb not null,
  interval_metrics jsonb not null,
  compatibility_decision text not null,
  limitations text not null
);
create table forecast_research.evaluation_cases (
  evaluation_id uuid references forecast_research.evaluations(evaluation_id),
  forecast_id uuid references forecast_research.forecast_values(forecast_id),
  outcome_source_id uuid not null references forecast_research.sources(source_id),
  observed_value numeric not null check (observed_value >= 0),
  forecast_error numeric not null,
  primary key(evaluation_id,forecast_id,outcome_source_id)
);
-- New tables default-deny; there are intentionally NO public policies or grants.
-- Review future safe projections, publisher role, review gates and RLS separately.
alter table forecast_research.sources enable row level security;
alter table forecast_research.runs enable row level security;
alter table forecast_research.run_sources enable row level security;
alter table forecast_research.forecast_values enable row level security;
alter table forecast_research.intervals enable row level security;
alter table forecast_research.evaluations enable row level security;
alter table forecast_research.evaluation_cases enable row level security;
revoke all on all tables in schema forecast_research from public, anon, authenticated;
commit;
-- Review before implementation: enforce cross-table evaluation counts/errors,
-- source availability vs issue time, interval nesting, and non-overlapping targets
-- using triggers/transactional publisher validation. "prospective" must require
-- evidence of issue time before target start; an execution timestamp is not proof.
