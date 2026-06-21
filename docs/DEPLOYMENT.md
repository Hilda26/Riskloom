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
python scripts/check_health.py \
  --frontend-url https://app.riskloom.io \
  --supabase-url https://<project-ref>.supabase.co
```
