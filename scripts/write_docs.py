"""
StableShield AI - Documentation Writer (STEP 9)
Writes/refreshes docs/README.md, ARCHITECTURE.md, DEPLOYMENT.md,
API.md, and ENVIRONMENT_VARIABLES.md.
Run from the repository root: python scripts/write_docs.py
Safe to re-run: existing files are never overwritten, except
docs/README.md which is intentionally refreshed every run since it's
a short index that should always reflect the current step.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

README = """\
# StableShield AI

AI-powered stablecoin risk intelligence network. Continuously analyzes
reserves, issuer health, peg stability, market sentiment, and
regulatory exposure to produce real-time, on-chain StableScore(tm)
ratings and early-warning alerts for the stablecoin ecosystem.

## Stack

- **Frontend**: Next.js 15 (App Router), deployed on Vercel - `apps/web`
- **Backend**: Supabase (Postgres + Auth + Edge Functions + Realtime + pg_cron) - `backend/supabase`
- **Intelligent Contract**: one GenLayer contract (`StableScoreOracle`), deployed to GenLayer Studio / StudioNet, fees in GEN - `intelligent-contracts/stablescore_oracle`
- **Auth**: wallet-based (MetaMask, Rainbow, Zerion, WalletConnect-compatible) via Sign-In With Ethereum, no custodial key management
- **Monorepo tooling**: pnpm workspaces + Turborepo

## Repository layout

```
apps/web/                      Next.js frontend
backend/supabase/               Migrations, seed data, Edge Functions
intelligent-contracts/          The StableScoreOracle GenLayer contract
packages/shared-types/          Types shared between frontend and contract
scripts/                        Python automation (setup, deploy, seed, health)
docs/                           This documentation
.github/workflows/              CI + deploy pipelines
```

## Quick start (local development)

```bash
pnpm install
pnpm --filter @stableshield/web dev    # frontend on http://localhost:3000
```

The frontend needs `apps/web/.env.local` (copy from `.env.example`) with
real Supabase + WalletConnect values - see ENVIRONMENT_VARIABLES.md.

## Documentation index

- [ARCHITECTURE.md](./ARCHITECTURE.md) - system design, data flow, service boundaries
- [DEPLOYMENT.md](./DEPLOYMENT.md) - step-by-step production deployment
- [API.md](./API.md) - public Risk Intelligence API reference
- [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) - every env var, where it's used, where to get it

## Status

All ten build steps (scaffolding, backend, frontend, intelligent
contract, tests, deployment pipeline) are implemented and verified
locally (builds pass, 22/22 automated tests pass). What's outstanding
before this is live in production:

1. Create the real Supabase project and run `scripts/seed_database.py`
   against it (currently only verified against the migration/seed SQL
   directly, not a live Supabase instance).
2. Deploy `intelligent-contracts/stablescore_oracle/contract.gpy` via
   GenLayer Studio to StudioNet and supply the resulting contract
   address + RPC URL.
3. Wire the real env vars (Supabase, WalletConnect, GenLayer) into
   Vercel and Supabase Edge Function secrets.
4. Wire up the GitHub Actions secrets referenced in
   `.github/workflows/deploy-frontend.yml` and `deploy-backend.yml`.
"""

ARCHITECTURE = """\
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
"""

DEPLOYMENT = """\
# Deployment Guide

Follow these in order. Each step is independently scriptable via
`scripts/*.py` as noted.

## 1. Supabase project

1. Create a project at https://supabase.com/dashboard.
2. Grab the project ref, anon key, service role key, and DB connection
   string from Project Settings.
3. Apply the schema + seed data:
   ```bash
   export DATABASE_URL="postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres"
   python scripts/seed_database.py
   ```
4. Deploy the Edge Functions:
   ```bash
   npm install -g supabase
   supabase login
   supabase link --project-ref <project-ref>
   python scripts/deploy_supabase_functions.py
   ```
5. Set Edge Function secrets (Supabase Dashboard -> Edge Functions ->
   Secrets, or `supabase secrets set`):
   - `GENLAYER_CONTRACT_ADDRESS`, `GENLAYER_STUDIONET_RPC_URL` (from
     step 3 below)
6. (Optional) Regenerate frontend types against the live schema:
   ```bash
   python scripts/generate_supabase_types.py --project-ref <project-ref>
   ```

## 2. Frontend (Vercel)

1. `npm install -g vercel && vercel login`
2. From `apps/web`, run `vercel link` once to associate the project.
3. Set environment variables in the Vercel project (Settings ->
   Environment Variables) - see ENVIRONMENT_VARIABLES.md for the full
   list. At minimum: `NEXT_PUBLIC_SUPABASE_URL`,
   `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID`.
4. Deploy:
   ```bash
   python scripts/deploy_frontend.py --prod
   ```
   Or let `.github/workflows/deploy-frontend.yml` handle it on every
   push to `main` (requires the `VERCEL_TOKEN` repo secret).

## 3. GenLayer Intelligent Contract

1. Open GenLayer Studio (https://studio.genlayer.com or your StudioNet
   endpoint).
2. Paste in `intelligent-contracts/stablescore_oracle/contract.gpy`
   and deploy to StudioNet (pays the GEN deployment fee).
3. Call `register_stablecoin` once per stablecoin in
   `backend/supabase/seed/seed_stablecoins.sql` (USDC, USDT, DAI,
   FRAX, TUSD, BUSD, USDP, GUSD, LUSD, MIM).
4. Record the deployed contract address + StudioNet RPC URL in
   `intelligent-contracts/stablescore_oracle/deploy_notes.md`, then set
   them as:
   - Supabase Edge Function secrets: `GENLAYER_CONTRACT_ADDRESS`,
     `GENLAYER_STUDIONET_RPC_URL`
   - Vercel env vars: `NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS`,
     `NEXT_PUBLIC_GENLAYER_STUDIONET_RPC_URL`

## 4. CI/CD

- `.github/workflows/ci.yml` runs on every PR and push to `main`:
  frontend lint/typecheck/unit-tests/build, backend Deno unit tests,
  and a contract syntax check.
- `.github/workflows/deploy-frontend.yml` deploys `apps/web` to Vercel
  on push to `main` (only when frontend files change). Needs repo
  secret `VERCEL_TOKEN`.
- `.github/workflows/deploy-backend.yml` pushes migrations and deploys
  Edge Functions on push to `main` (only when backend files change),
  then verifies the `/health` endpoint. Needs repo secrets
  `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_REF`,
  `SUPABASE_DB_PASSWORD`.

## 5. Post-deploy verification

```bash
python scripts/check_health.py \\
  --frontend-url https://app.riskloom.io \\
  --supabase-url https://<project-ref>.supabase.co
```
"""

API = """\
# Risk Intelligence API

Base URL: `https://<your-domain>/api/v1` (proxies to the Supabase
Edge Functions of the same name, so either base URL works).

All endpoints require an `x-api-key` header. Keys are issued per
profile in the `api_keys` table and scoped (e.g. `read:scores`).

## GET /api/v1/scores

Current StableScore ratings for all tracked stablecoins, or a single
symbol.

**Query params**
- `symbol` (optional) - e.g. `USDC`. Omit to return all.

**Response**
```json
{
  "data": [
    {
      "rating": "AAA",
      "score_numeric": 98.25,
      "updated_at": "2026-06-20T12:00:00Z",
      "stablecoins": { "symbol": "USDC", "name": "USD Coin" }
    }
  ]
}
```

## GET /api/v1/history

Historical StableScore ratings for one symbol.

**Query params**
- `symbol` (required) - e.g. `USDC`
- `limit` (optional, default 100, max 500)

**Response**
```json
{
  "data": [
    {
      "rating": "AAA",
      "score_numeric": 98.25,
      "reason_summary": null,
      "recorded_at": "2026-06-20T12:00:00Z"
    }
  ]
}
```

## Errors

| Status | Meaning |
|---|---|
| 401 | Missing `x-api-key` header |
| 403 | Invalid, revoked, or insufficiently-scoped API key |
| 404 | Unknown `symbol` |
| 500 | Internal error |

## On-chain alternative

Anyone can also read scores directly from the `StableScoreOracle`
Intelligent Contract on GenLayer StudioNet via `get_score`,
`get_history`, and `is_safe` - no API key required, fully
decentralized, paid in GEN per call per GenLayer's fee model. See
`intelligent-contracts/stablescore_oracle/interface.json`.
"""

ENV_VARS = """\
# Environment Variables

## Frontend (`apps/web/.env.local`, also set in Vercel)

| Variable | Required | Where to get it |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | yes | Supabase Dashboard -> Project Settings -> API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | yes | Supabase Dashboard -> Project Settings -> API |
| `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID` | yes | https://cloud.walletconnect.com (free project) |
| `NEXT_PUBLIC_GENLAYER_STUDIONET_RPC_URL` | after contract deploy | GenLayer Studio, once deployed |
| `NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS` | after contract deploy | GenLayer Studio, once deployed |
| `SUPABASE_SERVICE_ROLE_KEY` | server-only, never expose to the client | Supabase Dashboard -> Project Settings -> API |

## Backend (Supabase Edge Function secrets)

Set via `supabase secrets set KEY=value` or the Dashboard:

| Variable | Required | Notes |
|---|---|---|
| `SUPABASE_URL` | auto-injected | Provided automatically by Supabase at runtime |
| `SUPABASE_SERVICE_ROLE_KEY` | auto-injected | Provided automatically by Supabase at runtime |
| `GENLAYER_CONTRACT_ADDRESS` | after contract deploy | Used by `publish-to-genlayer` |
| `GENLAYER_STUDIONET_RPC_URL` | after contract deploy | Used by `publish-to-genlayer` |

## CI/CD (GitHub repo secrets)

| Secret | Used by |
|---|---|
| `VERCEL_TOKEN` | `.github/workflows/deploy-frontend.yml` |
| `SUPABASE_ACCESS_TOKEN` | `.github/workflows/deploy-backend.yml` |
| `SUPABASE_PROJECT_REF` | `.github/workflows/deploy-backend.yml` |
| `SUPABASE_DB_PASSWORD` | `.github/workflows/deploy-backend.yml` |

## Local scripts

| Variable | Used by |
|---|---|
| `DATABASE_URL` | `scripts/seed_database.py` |
| `FRONTEND_URL`, `NEXT_PUBLIC_SUPABASE_URL` | `scripts/check_health.py` |
"""


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)

    # README is a living index - always refresh it.
    (DOCS / "README.md").write_text(README, encoding="utf-8")
    written = ["README.md (refreshed)"]

    for name, content in [
        ("ARCHITECTURE.md", ARCHITECTURE),
        ("DEPLOYMENT.md", DEPLOYMENT),
        ("API.md", API),
        ("ENVIRONMENT_VARIABLES.md", ENV_VARS),
    ]:
        path = DOCS / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            written.append(name)

    print(f"Docs directory: {DOCS}")
    print(f"Wrote {len(written)} file(s).")
    for f in written:
        print(f"  + {f}")


if __name__ == "__main__":
    main()
