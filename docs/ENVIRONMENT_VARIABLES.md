# Environment Variables

## Frontend (`apps/web/.env.local`, also set in Vercel)

| Variable | Required | Where to get it |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | yes | Supabase Dashboard -> Project Settings -> API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | yes | Supabase Dashboard -> Project Settings -> API |
| `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID` | yes | https://cloud.walletconnect.com (free project) |
| `NEXT_PUBLIC_GENLAYER_STUDIONET_RPC_URL` | yes | `https://studio.genlayer.com/api` (GenLayer's hosted Studio endpoint) |
| `NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS` | yes | The deployed `StableScoreOracle` address from GenLayer Studio |
| `SUPABASE_SERVICE_ROLE_KEY` | server-only, never expose to the client | Supabase Dashboard -> Project Settings -> API |

## Backend (Supabase Edge Function secrets)

Set via `supabase secrets set KEY=value` or the Dashboard:

| Variable | Required | Notes |
|---|---|---|
| `SUPABASE_URL` | auto-injected | Provided automatically by Supabase at runtime |
| `SUPABASE_SERVICE_ROLE_KEY` | auto-injected | Provided automatically by Supabase at runtime |
| `GENLAYER_CONTRACT_ADDRESS` | yes | Used by `publish-to-genlayer` |
| `GENLAYER_STUDIONET_RPC_URL` | yes | Used by `publish-to-genlayer` |
| `GENLAYER_PRIVATE_KEY` | yes | The service account `publish-to-genlayer` signs `update_score` transactions with. Generated via `genlayer-js`'s `createAccount()`/`generatePrivateKey()` - fund its address with StudioNet GEN before the first write call. |

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
