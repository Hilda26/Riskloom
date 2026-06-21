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
