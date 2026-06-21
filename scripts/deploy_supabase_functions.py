"""
StableShield AI - Supabase Edge Functions Deployer
Deploys every function under backend/supabase/functions (skipping the
_shared helper directory) using the Supabase CLI.

Prerequisites:
  npm install -g supabase
  supabase login
  supabase link --project-ref <your-project-ref>

Usage:
  python scripts/deploy_supabase_functions.py
  python scripts/deploy_supabase_functions.py --project-ref abcdefghijklmnop
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNCTIONS_DIR = ROOT / "backend" / "supabase" / "functions"

# On Windows, global npm CLIs install as .cmd shims that subprocess
# won't resolve without shell=True or an explicit extension lookup.
SUPABASE_BIN = shutil.which("supabase") or "supabase"


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy all Supabase Edge Functions")
    parser.add_argument("--project-ref", default=None, help="Supabase project ref (optional if already linked)")
    args = parser.parse_args()

    if not FUNCTIONS_DIR.exists():
        raise SystemExit(f"No functions directory at {FUNCTIONS_DIR}")

    function_dirs = sorted(
        d for d in FUNCTIONS_DIR.iterdir() if d.is_dir() and d.name != "_shared"
    )
    if not function_dirs:
        raise SystemExit("No functions found to deploy.")

    failures = []
    for func_dir in function_dirs:
        name = func_dir.name
        # --use-api bundles server-side instead of via Docker, matching
        # the project's no-Docker deployment constraint.
        cmd = [SUPABASE_BIN, "functions", "deploy", name, "--workdir", "backend", "--use-api"]
        if args.project_ref:
            cmd += ["--project-ref", args.project_ref]

        print(f"\n--- Deploying {name} ---")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            failures.append(name)

    if failures:
        print(f"\nFailed to deploy: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"\nDeployed {len(function_dirs)} function(s) successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
