-- PROPOSED ONLY. Do not apply until the reviewed public-data scope is approved.
-- Review: docs/supabase-integration-review.md. No write policies or grants.
begin;

alter table public.mortality_quarterly enable row level security;
alter table public.indicator_configurations enable row level security;
alter table public.indicator_results enable row level security;

create policy "anon_read_public_mortality"
  on public.mortality_quarterly for select to anon using (true);

create policy "anon_read_public_configurations"
  on public.indicator_configurations for select to anon using (true);

create policy "anon_read_public_results"
  on public.indicator_results for select to anon using (true);

commit;

-- Separate recommendation, NOT executed by this migration:
-- revoke insert, update, delete on table
--   public.mortality_quarterly, public.indicator_configurations,
--   public.indicator_results from anon;
-- Existing anon SELECT privileges are sufficient. No other tables are opened.
