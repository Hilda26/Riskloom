# Architecture

## System overview

```
                         +-----------------------------+
                         |   Vercel (Next.js Frontend)  |
                         |  Landing + Dashboard + Auth   |
                         +---------------+---------------+
                                         | HTTPS / Supabase JS client
                 +-----------------------+------------------------+
                 v                                                v
   +--------------------------+                    +---------------------------+
   |   Supabase Postgres DB    |<----Realtime------>|  Supabase Edge Functions  |
   |  (scores, issuers, etc.)  |                     |  (Deno/TS - our "API")    |
   +-------------+--------------+                    +-------------+-------------+
                 | pg_cron (scheduled jobs)                         |
                 v                                                  v
   +--------------------------+                    +---------------------------+
   | Score Recompute Jobs      |                    |  GenLayer Studio Client    |
   | (reserve/peg/sentiment/   |------writes------->|  StudioNet RPC (GEN fee)   |
   |  regulatory ingestion)    |                    |  StableScoreOracle.gpy     |
   +--------------------------+                    +---------------------------+
                                                                   |
                                          DeFi protocols read scores on-chain
                                          (lending, treasury, payments, etc.)
```

## Why this shape

No standalone backend host (Railway/Fly/etc.) was used by design -
Supabase Edge Functions absorb everything a Node/Express API would
normally do, and Postgres + pg_cron handle scheduled recomputation.

## Service boundaries

| Service | Responsibility | Runtime |
|---|---|---|
| Frontend (Next.js) | Landing page, dashboard, wallet-connect UX, data viz | Vercel |
| `siwe-nonce` / `siwe-verify` | Sign-In With Ethereum challenge/response, session minting | Supabase Edge Function |
| `ingest-reserves` / `ingest-peg` / `ingest-sentiment` / `ingest-regulatory` | Normalize external data into staging tables | Supabase Edge Function |
| `compute-stablescore` | Combine the five module outputs into a composite StableScore | Supabase Edge Function |
| `publish-to-genlayer` | Push finalized scores to the GenLayer Intelligent Contract | Supabase Edge Function |
| `api-v1-scores` / `api-v1-history` | Rate-limited, API-key-gated public read access | Supabase Edge Function |
| `health` | Liveness/readiness check | Supabase Edge Function |
| `StableScoreOracle` | Canonical on-chain source of truth for scores, history, metadata | GenLayer Studio / StudioNet |

## Database schema

See `backend/supabase/migrations/*.sql` for the authoritative schema.
Summary: `wallets`/`profiles`/`api_keys` (identity), `issuers`/
`stablecoins` (universe), `reserve_reports`/`issuer_financials`/
`peg_snapshots`/`regulatory_events`/`sentiment_signals` (the five risk
modules' raw inputs), `risk_scores`/`risk_score_history` (composite
output), `oracle_publications`/`alerts`/`audit_log`.

## Wallet strategy & auth flow

Non-custodial wallet auth (MetaMask, Rainbow, Zerion, any
WalletConnect-compatible wallet) via wagmi + RainbowKit on the
frontend, Sign-In With Ethereum (EIP-4361) for session establishment:

1. Wallet connects -> frontend requests a nonce from `siwe-nonce`.
2. Wallet signs the SIWE message.
3. Frontend posts `{message, signature}` to `siwe-verify`, which
   verifies the signature, upserts `wallets`/`profiles`, and returns a
   Supabase magic-link action link.
4. Frontend redirects to that link; `/auth/callback` exchanges it for
   a real Supabase session cookie.

## GenLayer integration

One Intelligent Contract, `StableScoreOracle`
(`intelligent-contracts/stablescore_oracle/contract.gpy`), deployed
manually via GenLayer Studio to StudioNet, fees in GEN. The contract
takes the five raw subscores + an evidence summary and uses
`gl.nondet.exec_prompt` + `gl.eq_principle.prompt_non_comparative` so
GenLayer's validator network reaches consensus on the resulting letter
grade and its justification - not a plain deterministic setter. See
`intelligent-contracts/stablescore_oracle/deploy_notes.md` for the
full design rationale and documentation sources consulted while
writing it.
