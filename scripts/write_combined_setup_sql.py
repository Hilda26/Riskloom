"""
StableShield AI - Combined Setup SQL Writer
Concatenates every migration (in order) plus the seed data into one
file, so it can be pasted into the Supabase Dashboard's SQL Editor in
a single run instead of seven separate pastes.

Run from the repository root: python scripts/write_combined_setup_sql.py
Re-running always regenerates this file (it's a derived artifact, not
a source of truth - the real source of truth is backend/supabase/migrations/*.sql).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "backend" / "supabase" / "migrations"
SEED_FILE = ROOT / "backend" / "supabase" / "seed" / "seed_stablecoins.sql"
OUTPUT_FILE = ROOT / "backend" / "supabase" / "combined_setup.sql"


def main() -> None:
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migrations:
        raise SystemExit(f"No migrations found in {MIGRATIONS_DIR}")

    parts = [
        "-- StableShield AI - combined setup script (auto-generated, do not hand-edit).",
        "-- Source of truth is backend/supabase/migrations/*.sql + seed/seed_stablecoins.sql -",
        "-- regenerate this file with: python scripts/write_combined_setup_sql.py",
        "-- Paste this entire file into Supabase Dashboard -> SQL Editor -> New query -> Run.",
        "",
    ]

    for migration in migrations:
        parts.append(f"-- ===== {migration.name} =====")
        parts.append(migration.read_text(encoding="utf-8"))

    if SEED_FILE.exists():
        parts.append(f"-- ===== seed/{SEED_FILE.name} =====")
        parts.append(SEED_FILE.read_text(encoding="utf-8"))

    OUTPUT_FILE.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE.relative_to(ROOT)} ({len(migrations)} migrations + seed)")


if __name__ == "__main__":
    main()
