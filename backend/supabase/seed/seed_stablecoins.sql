-- Seed data: issuers, stablecoins, and an initial risk_scores snapshot.
-- Mirrors the StableScore band and dashboard table shown in the
-- landing page design (riskloom-final.html).

insert into issuers (name, jurisdiction, website, regulatory_status)
values
  ('Circle', 'United States', 'https://www.circle.com', 'Licensed money transmitter (multi-state, US)'),
  ('Tether Ltd', 'British Virgin Islands', 'https://tether.to', 'Unregulated offshore issuer'),
  ('MakerDAO', 'Decentralized (Cayman Foundation)', 'https://makerdao.com', 'Decentralized governance, no central issuer license'),
  ('Frax Finance', 'Decentralized', 'https://frax.finance', 'Decentralized governance'),
  ('TrustToken', 'United States', 'https://www.trusttoken.com', 'State trust-chartered'),
  ('Paxos', 'United States', 'https://paxos.com', 'NYDFS-regulated trust company'),
  ('Gemini', 'United States', 'https://www.gemini.com', 'NYDFS-regulated trust company'),
  ('Liquity', 'Decentralized', 'https://www.liquity.org', 'Decentralized, no central issuer'),
  ('Abracadabra Money', 'Decentralized', 'https://abracadabra.money', 'Decentralized governance')
on conflict do nothing;

insert into stablecoins (symbol, name, issuer_id, chain, decimals, market_cap_usd, peg_price)
select v.symbol, v.name, i.id, v.chain, 18, v.market_cap, v.peg_price
from (values
  ('USDC', 'USD Coin', 'Circle', 'ethereum', 43200000000.00, 1.0001),
  ('USDT', 'Tether', 'Tether Ltd', 'ethereum', 118400000000.00, 0.9999),
  ('DAI',  'Dai', 'MakerDAO', 'ethereum', 5300000000.00, 1.0003),
  ('FRAX', 'Frax', 'Frax Finance', 'ethereum', 643000000.00, 0.9981),
  ('TUSD', 'TrueUSD', 'TrustToken', 'ethereum', 490000000.00, 0.9947),
  ('BUSD', 'Binance USD', 'Paxos', 'ethereum', 210000000.00, 0.9912),
  ('USDP', 'Pax Dollar', 'Paxos', 'ethereum', 150000000.00, 1.0000),
  ('GUSD', 'Gemini Dollar', 'Gemini', 'ethereum', 60000000.00, 0.9998),
  ('LUSD', 'Liquity USD', 'Liquity', 'ethereum', 320000000.00, 0.9975),
  ('MIM',  'Magic Internet Money', 'Abracadabra Money', 'ethereum', 28000000.00, 0.9801)
) as v(symbol, name, issuer_name, chain, market_cap, peg_price)
join issuers i on i.name = v.issuer_name
on conflict (symbol) do nothing;

-- Initial StableScore snapshot, consistent with the ratings band on
-- the landing page (AAA/AA/A/BBB/BB/B/CCC/D distribution).
--
-- score_numeric is the actual output of the weighted composite formula
-- in backend/supabase/functions/_shared/scoring.ts
-- (reserve*0.30 + issuer*0.20 + peg*0.25 + regulatory*0.15 + sentiment*0.10)
-- applied to each row's own subscores below - verified by
-- _shared/scoring.test.ts so the seed data never silently drifts from
-- what the live scoring engine would itself produce.
insert into risk_scores (
  stablecoin_id, rating, score_numeric,
  reserve_subscore, issuer_subscore, peg_subscore, regulatory_subscore, sentiment_subscore
)
select s.id, v.rating, v.score,
       v.reserve, v.issuer, v.peg, v.regulatory, v.sentiment
from (values
  ('USDC', 'AAA', 98.25, 99.0, 97.0, 100.0, 97.0, 96.0),
  ('USDT', 'AA',  91.20, 90.0, 90.0, 97.0,  85.0, 92.0),
  ('DAI',  'A',   82.30, 78.0, 85.0, 88.0,  80.0, 79.0),
  ('FRAX', 'BBB', 66.55, 60.0, 70.0, 72.0,  65.0, 68.0),
  ('TUSD', 'BB',  55.55, 50.0, 58.0, 60.0,  55.0, 57.0),
  ('BUSD', 'B',   38.05, 35.0, 38.0, 45.0,  30.0, 42.0),
  ('USDP', 'AA',  91.50, 92.0, 92.0, 94.0,  88.0, 88.0),
  ('GUSD', 'A',   82.40, 80.0, 84.0, 86.0,  80.0, 81.0),
  ('LUSD', 'BBB', 65.50, 62.0, 66.0, 70.0,  64.0, 66.0),
  ('MIM',  'CCC', 15.60, 12.0, 15.0, 20.0,  10.0, 25.0)
) as v(symbol, rating, score, reserve, issuer, peg, regulatory, sentiment)
join stablecoins s on s.symbol = v.symbol
on conflict (stablecoin_id) do nothing;
