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
