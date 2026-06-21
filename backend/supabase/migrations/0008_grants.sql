-- Explicit privilege grants.
--
-- Migrations applied via a direct Postgres connection (supabase db
-- push) bypass the ALTER DEFAULT PRIVILEGES Supabase normally sets up
-- for tables created through its own tooling, so anon/authenticated/
-- service_role end up with zero SQL-level grants on these tables even
-- though RLS policies already exist. RLS is an additional filter on
-- top of GRANTs, not a replacement for them - both layers must allow
-- access, so this was failing with "permission denied" before RLS was
-- ever evaluated.
grant usage on schema public to anon, authenticated, service_role;

grant select, insert, update, delete on all tables in schema public
  to service_role;

grant select on
  wallets, profiles, stablecoins, issuers, risk_scores, risk_score_history,
  alerts, oracle_publications, reserve_reports, issuer_financials,
  peg_snapshots, regulatory_events, sentiment_signals
  to anon, authenticated;

grant select, update on profiles to authenticated;
grant select on api_keys to authenticated;

-- Cover any tables added by future migrations automatically.
alter default privileges in schema public
  grant select, insert, update, delete on tables to service_role;
