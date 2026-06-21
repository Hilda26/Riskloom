"""
StableShield AI - Project Scaffolding Script
Creates the full production folder structure agreed on in STEP 3.
Run from the repository root:  python scripts/setup_project.py
Safe to re-run: existing files are never overwritten, only missing
directories/files are created.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DIRECTORIES = [
    "apps/web/app/(marketing)/pricing",
    "apps/web/app/(dashboard)/dashboard",
    "apps/web/app/(dashboard)/stablecoins/[symbol]",
    "apps/web/app/(dashboard)/oracle",
    "apps/web/app/(dashboard)/alerts",
    "apps/web/app/(dashboard)/reports",
    "apps/web/app/(dashboard)/settings",
    "apps/web/app/api/v1",
    "apps/web/app/auth/callback",
    "apps/web/components/ui",
    "apps/web/components/layout",
    "apps/web/components/dashboard",
    "apps/web/components/oracle",
    "apps/web/components/charts",
    "apps/web/components/wallet",
    "apps/web/hooks",
    "apps/web/lib/supabase",
    "apps/web/lib/genlayer",
    "apps/web/lib/wagmi",
    "apps/web/types",
    "apps/web/styles",
    "apps/web/public",
    "apps/web/tests/unit",
    "apps/web/tests/e2e",
    "backend/supabase/migrations",
    "backend/supabase/functions/siwe-nonce",
    "backend/supabase/functions/siwe-verify",
    "backend/supabase/functions/ingest-reserves",
    "backend/supabase/functions/ingest-peg",
    "backend/supabase/functions/ingest-sentiment",
    "backend/supabase/functions/ingest-regulatory",
    "backend/supabase/functions/compute-stablescore",
    "backend/supabase/functions/publish-to-genlayer",
    "backend/supabase/functions/api-v1-scores",
    "backend/supabase/functions/api-v1-history",
    "backend/supabase/functions/health",
    "backend/supabase/seed",
    "intelligent-contracts/stablescore_oracle",
    "packages/shared-types",
    "scripts",
    "docs",
    ".github/workflows",
]

# (relative path, content) - only created if the file does not already exist
FILES = [
    ("apps/web/.env.example", """\
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=
NEXT_PUBLIC_GENLAYER_STUDIONET_RPC_URL=
NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS=
SUPABASE_SERVICE_ROLE_KEY=
"""),
    ("apps/web/package.json", """\
{
  "name": "@stableshield/web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:e2e": "playwright test"
  }
}
"""),
    ("apps/web/tsconfig.json", """\
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "moduleResolution": "bundler",
    "module": "esnext",
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
"""),
    ("backend/supabase/config.toml", """\
# Supabase project configuration
# Filled in fully during STEP 5 (backend implementation)
project_id = "stableshield-ai"
"""),
    ("intelligent-contracts/stablescore_oracle/deploy_notes.md", """\
# StableScoreOracle - Deployment Notes

Deployment target: GenLayer Studio, Network: StudioNet, Fees: GEN token.

Steps will be filled in during STEP 7 once the contract is implemented.
After deployment, record the contract address here and supply it back
for backend/frontend integration.

Contract address: (pending)
"""),
    ("packages/shared-types/ratings.ts", """\
export const STABLE_SCORE_GRADES = [
  "AAA",
  "AA",
  "A",
  "BBB",
  "BB",
  "B",
  "CCC",
  "D",
] as const;

export type StableScoreGrade = (typeof STABLE_SCORE_GRADES)[number];
"""),
    ("packages/shared-types/index.ts", """\
export * from "./ratings";
"""),
    (".env.example", """\
# Root-level environment reference - see apps/web/.env.example and
# backend/supabase/.env.example for service-specific variables.
"""),
    (".gitignore", """\
node_modules/
.next/
out/
dist/
.env
.env.local
.turbo/
.vercel/
supabase/.branches/
supabase/.temp/
*.log
.DS_Store
"""),
    ("pnpm-workspace.yaml", """\
packages:
  - "apps/*"
  - "packages/*"
"""),
    ("turbo.json", """\
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": [".next/**"] },
    "dev": { "cache": false, "persistent": true },
    "lint": {},
    "typecheck": {},
    "test": {}
  }
}
"""),
    ("package.json", """\
{
  "name": "stableshield-ai",
  "version": "0.1.0",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "typecheck": "turbo run typecheck",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
"""),
    ("docs/README.md", """\
# StableShield AI

AI-powered stablecoin risk intelligence network. See ARCHITECTURE.md,
DEPLOYMENT.md, API.md, and ENVIRONMENT_VARIABLES.md in this directory.

Project scaffolding generated by scripts/setup_project.py (STEP 4).
Implementation follows in subsequent steps - backend, frontend,
intelligent contract, testing, deployment, integration.
"""),
]


def ensure_directories() -> list[str]:
    created = []
    for rel in DIRECTORIES:
        path = ROOT / rel
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(rel)
    return created


def ensure_files() -> list[str]:
    created = []
    for rel, content in FILES:
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(rel)
    return created


def main() -> None:
    print(f"Scaffolding StableShield AI at: {ROOT}")
    new_dirs = ensure_directories()
    new_files = ensure_files()

    print(f"\nCreated {len(new_dirs)} new directories.")
    for d in new_dirs:
        print(f"  + {d}")

    print(f"\nCreated {len(new_files)} new files.")
    for f in new_files:
        print(f"  + {f}")

    if not new_dirs and not new_files:
        print("\nNothing to do - structure already exists.")

    print("\nScaffolding complete.")


if __name__ == "__main__":
    main()
