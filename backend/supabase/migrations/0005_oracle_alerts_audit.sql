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
