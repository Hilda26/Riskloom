"""
StableShield AI - Health Check Script
Pings the backend health Edge Function and the frontend homepage,
exits non-zero if either is unreachable or unhealthy.

Usage:
  python scripts/check_health.py
  python scripts/check_health.py --frontend-url https://app.riskloom.io --supabase-url https://xxx.supabase.co
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def check_url(url: str, label: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            status_ok = 200 <= resp.status < 300
            print(f"[{label}] HTTP {resp.status} - {body[:200]}")
            return status_ok
    except urllib.error.HTTPError as exc:
        print(f"[{label}] HTTP {exc.code} - {exc.read().decode('utf-8', 'ignore')[:200]}")
        return False
    except Exception as exc:  # network errors, timeouts, DNS failures
        print(f"[{label}] FAILED - {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Check StableShield AI service health")
    parser.add_argument(
        "--frontend-url",
        default=os.environ.get("FRONTEND_URL", "http://localhost:3000"),
    )
    parser.add_argument(
        "--supabase-url",
        default=os.environ.get("NEXT_PUBLIC_SUPABASE_URL", ""),
    )
    args = parser.parse_args()

    results = []

    results.append(check_url(args.frontend_url, "frontend"))

    if args.supabase_url:
        health_url = f"{args.supabase_url.rstrip('/')}/functions/v1/health"
        results.append(check_url(health_url, "backend-health"))
    else:
        print("[backend-health] SKIPPED - no --supabase-url / NEXT_PUBLIC_SUPABASE_URL set")

    print(json.dumps({"checks_passed": sum(results), "checks_total": len(results)}))

    if not results or not all(results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
