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
