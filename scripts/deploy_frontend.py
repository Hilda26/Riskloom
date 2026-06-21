"""
StableShield AI - Frontend Deployer
Deploys apps/web to Vercel using the Vercel CLI.

Prerequisites:
  npm install -g vercel
  vercel login
  vercel link (run once inside apps/web to associate the project)

Usage:
  python scripts/deploy_frontend.py            # preview deployment
  python scripts/deploy_frontend.py --prod     # production deployment
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "apps" / "web"


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy the StableShield AI frontend to Vercel")
    parser.add_argument("--prod", action="store_true", help="Deploy to production")
    args = parser.parse_args()

    if not WEB_DIR.exists():
        raise SystemExit(f"Frontend directory not found at {WEB_DIR}")

    cmd = ["vercel"]
    if args.prod:
        cmd.append("--prod")

    print(f"Running: {' '.join(cmd)} (cwd={WEB_DIR})")
    result = subprocess.run(cmd, cwd=WEB_DIR)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
