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
