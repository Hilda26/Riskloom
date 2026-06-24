# Riskloom

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
