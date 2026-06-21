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
  launched_at date,
  market_cap_usd numeric(20,2),
  peg_price numeric(12,6) not null default 1.0
);

create index if not exists idx_stablecoins_issuer_id on stablecoins(issuer_id);
