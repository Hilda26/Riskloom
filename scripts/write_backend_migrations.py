"""
StableShield AI - Backend Migration Writer
Writes the full Supabase SQL migration set (STEP 5).
Run from the repository root: python scripts/write_backend_migrations.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "backend" / "supabase" / "migrations"

FILES = {
    "0001_init_identity.sql": """\
-- Identity: wallets, profiles, api keys
create extension if not exists "pgcrypto";

create table if not exists wallets (
  id uuid primary key default gen_random_uuid(),
  address text not null unique,
  chain_id integer not null default 1,
  created_at timestamptz not null default now(),
  last_login_at timestamptz
);

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  wallet_id uuid not null references wallets(id) on delete cascade,
  display_name text,
  tier text not null default 'free' check (tier in ('free', 'pro', 'institutional')),
  created_at timestamptz not null default now()
);

create table if not exists api_keys (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles(id) on delete cascade,
  key_hash text not null unique,
  scopes text[] not null default array['read:scores'],
  rate_limit integer not null default 60,
  created_at timestamptz not null default now(),
  revoked_at timestamptz
);

create index if not exists idx_profiles_wallet_id on profiles(wallet_id);
create index if not exists idx_api_keys_profile_id on api_keys(profile_id);
""",
    "0002_stablecoins_issuers.sql": """\
-- Stablecoin universe: issuers and stablecoins
create table if not exists issuers (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  jurisdiction text,
  website text,
  regulatory_status text,
  created_at timestamptz not null default now()
);

create table if not exists stablecoins (
  id uuid primary key default gen_random_uuid(),
  symbol text not null unique,
  name text not null,
  issuer_id uuid references issuers(id) on delete set null,
  chain text not null default 'ethereum',
  contract_address text,
  decimals integer not null default 18,
  launched_at date
);

create index if not exists idx_stablecoins_issuer_id on stablecoins(issuer_id);
""",
    "0003_module_inputs.sql": """\
-- Raw/staged module inputs feeding the scoring engine
create table if not exists reserve_reports (
  id uuid primary key default gen_random_uuid(),
  stablecoin_id uuid not null references stablecoins(id) on delete cascade,
  cash_pct numeric(5,2),
  commercial_paper_pct numeric(5,2),
  treasuries_pct numeric(5,2),
  other_pct numeric(5,2),
  audit_firm text,
  attestation_date date,
  transparency_score numeric(5,2),
  source_url text,
  created_at timestamptz not null default now()
);

create table if not exists issuer_financials (
  id uuid primary key default gen_random_uuid(),
  issuer_id uuid not null references issuers(id) on delete cascade,
  period text not null,
  liquidity_ratio numeric(6,3),
  credit_indicator text,
  filing_url text,
  enforcement_flag boolean not null default false,
  reported_at timestamptz not null default now()
);

create table if not exists peg_snapshots (
  id uuid primary key default gen_random_uuid(),
  stablecoin_id uuid not null references stablecoins(id) on delete cascade,
  price numeric(12,6) not null,
  deviation_bps numeric(8,2) not null,
  redemption_volume_24h numeric(20,2),
  market_depth_usd numeric(20,2),
  captured_at timestamptz not null default now()
);

create table if not exists regulatory_events (
  id uuid primary key default gen_random_uuid(),
  issuer_id uuid not null references issuers(id) on delete cascade,
  jurisdiction text not null,
  event_type text not null,
  severity text not null check (severity in ('low', 'medium', 'high', 'critical')),
  description text,
  occurred_at timestamptz not null default now()
);

create table if not exists sentiment_signals (
  id uuid primary key default gen_random_uuid(),
  stablecoin_id uuid not null references stablecoins(id) on delete cascade,
  source text not null,
  sentiment_score numeric(5,2) not null,
  panic_flag boolean not null default false,
  captured_at timestamptz not null default now()
);

create index if not exists idx_reserve_reports_stablecoin on reserve_reports(stablecoin_id);
create index if not exists idx_issuer_financials_issuer on issuer_financials(issuer_id);
create index if not exists idx_peg_snapshots_stablecoin_time on peg_snapshots(stablecoin_id, captured_at);
create index if not exists idx_regulatory_events_issuer on regulatory_events(issuer_id);
create index if not exists idx_sentiment_signals_stablecoin_time on sentiment_signals(stablecoin_id, captured_at);
""",
    "0004_risk_scores.sql": """\
-- Composite StableScore output + history
create table if not exists risk_scores (
  id uuid primary key default gen_random_uuid(),
  stablecoin_id uuid not null unique references stablecoins(id) on delete cascade,
  rating text not null check (rating in ('AAA','AA','A','BBB','BB','B','CCC','D')),
  score_numeric numeric(5,2) not null,
  reserve_subscore numeric(5,2),
  issuer_subscore numeric(5,2),
  peg_subscore numeric(5,2),
  regulatory_subscore numeric(5,2),
  sentiment_subscore numeric(5,2),
  updated_at timestamptz not null default now()
);

create table if not exists risk_score_history (
  id uuid primary key default gen_random_uuid(),
  stablecoin_id uuid not null references stablecoins(id) on delete cascade,
  rating text not null check (rating in ('AAA','AA','A','BBB','BB','B','CCC','D')),
  score_numeric numeric(5,2) not null,
  reason_summary text,
  recorded_at timestamptz not null default now()
);

create index if not exists idx_risk_score_history_stablecoin_time
  on risk_score_history(stablecoin_id, recorded_at desc);
""",
    "0005_oracle_alerts_audit.sql": """\
-- Oracle publication tracking, alerts, audit log
create table if not exists oracle_publications (
  id uuid primary key default gen_random_uuid(),
  stablecoin_id uuid not null references stablecoins(id) on delete cascade,
  tx_hash text,
  contract_address text not null,
  network text not null default 'studionet',
  published_rating text not null,
  published_at timestamptz not null default now(),
  status text not null default 'pending' check (status in ('pending','confirmed','failed'))
);

create table if not exists alerts (
  id uuid primary key default gen_random_uuid(),
  stablecoin_id uuid not null references stablecoins(id) on delete cascade,
  severity text not null check (severity in ('info','warning','critical')),
  message text not null,
  triggered_at timestamptz not null default now(),
  resolved_at timestamptz
);

create table if not exists audit_log (
  id uuid primary key default gen_random_uuid(),
  actor text not null,
  action text not null,
  target_table text,
  target_id uuid,
  payload jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_oracle_publications_stablecoin on oracle_publications(stablecoin_id);
create index if not exists idx_alerts_stablecoin on alerts(stablecoin_id);
create index if not exists idx_audit_log_created_at on audit_log(created_at desc);
""",
    "0006_rls_policies.sql": """\
-- Row Level Security policies
alter table wallets enable row level security;
alter table profiles enable row level security;
alter table api_keys enable row level security;
alter table stablecoins enable row level security;
alter table issuers enable row level security;
alter table risk_scores enable row level security;
alter table risk_score_history enable row level security;
alter table alerts enable row level security;
alter table oracle_publications enable row level security;
alter table audit_log enable row level security;
alter table reserve_reports enable row level security;
alter table issuer_financials enable row level security;
alter table peg_snapshots enable row level security;
alter table regulatory_events enable row level security;
alter table sentiment_signals enable row level security;

-- Public, read-only access to the risk intelligence surface
create policy "public read stablecoins" on stablecoins for select using (true);
create policy "public read issuers" on issuers for select using (true);
create policy "public read risk_scores" on risk_scores for select using (true);
create policy "public read risk_score_history" on risk_score_history for select using (true);
create policy "public read alerts" on alerts for select using (true);
create policy "public read oracle_publications" on oracle_publications for select using (true);
create policy "public read reserve_reports" on reserve_reports for select using (true);
create policy "public read issuer_financials" on issuer_financials for select using (true);
create policy "public read peg_snapshots" on peg_snapshots for select using (true);
create policy "public read regulatory_events" on regulatory_events for select using (true);
create policy "public read sentiment_signals" on sentiment_signals for select using (true);

-- Users may only see their own identity records
create policy "user reads own wallet" on wallets for select
  using (auth.uid() in (select id from profiles where wallet_id = wallets.id));
create policy "user reads own profile" on profiles for select
  using (auth.uid() = id);
create policy "user updates own profile" on profiles for update
  using (auth.uid() = id);
create policy "user reads own api keys" on api_keys for select
  using (auth.uid() = profile_id);

-- audit_log: service-role only (no public/user policies defined - default deny)
""",
    "0007_siwe_nonces.sql": """\
-- Short-lived nonces for Sign-In With Ethereum challenge/response
create table if not exists siwe_nonces (
  id uuid primary key default gen_random_uuid(),
  address text not null,
  nonce text not null unique,
  expires_at timestamptz not null,
  consumed_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists idx_siwe_nonces_address on siwe_nonces(address);

alter table siwe_nonces enable row level security;
-- service-role only: no select/insert policy for anon/authenticated roles
""",
    "0008_grants.sql": """\
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
""",
}


def main() -> None:
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    for filename, content in FILES.items():
        path = MIGRATIONS_DIR / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(filename)

    print(f"Migrations directory: {MIGRATIONS_DIR}")
    print(f"Created {len(created)} migration file(s).")
    for f in created:
        print(f"  + {f}")
    if not created:
        print("Nothing to do - all migration files already exist.")


if __name__ == "__main__":
    main()
