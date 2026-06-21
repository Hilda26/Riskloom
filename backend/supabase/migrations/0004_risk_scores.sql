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
