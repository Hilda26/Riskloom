"""
StableShield AI - Database Seed Runner
Applies the migrations in backend/supabase/migrations and the seed
data in backend/supabase/seed against a target Postgres database
using `psql` (ships with the Supabase CLI / any local Postgres
install - no Docker required).

Usage:
  DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres \\
    python scripts/seed_database.py
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "backend" / "supabase" / "migrations"
SEED_FILE = ROOT / "backend" / "supabase" / "seed" / "seed_stablecoins.sql"


def run_sql_file(database_url: str, sql_file: Path) -> None:
    print(f"Applying {sql_file.relative_to(ROOT)} ...")
    result = subprocess.run(
        ["psql", database_url, "-v", "ON_ERROR_STOP=1", "-f", str(sql_file)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"Failed applying {sql_file.name}")
    print(result.stdout)


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "DATABASE_URL is not set. Example:\n"
            "  postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres\n"
            "Find this under Supabase Dashboard -> Project Settings -> Database."
        )

    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migrations:
        raise SystemExit(f"No migrations found in {MIGRATIONS_DIR}")

    for migration in migrations:
        run_sql_file(database_url, migration)

    if SEED_FILE.exists():
        run_sql_file(database_url, SEED_FILE)
    else:
        print(f"No seed file at {SEED_FILE}, skipping seed step.")

    print("Database migrations + seed applied successfully.")


if __name__ == "__main__":
    main()
