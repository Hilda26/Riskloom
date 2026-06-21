"""
StableShield AI - Frontend Lib/Types/Config Writer (STEP 6, part 1)
Writes Next.js config, Supabase clients, wagmi/RainbowKit config,
SIWE helper, GenLayer client, and shared TS types.
Run from the repository root: python scripts/write_frontend_lib.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "apps" / "web"

FILES = {
    "next.config.ts": """\
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
};

export default nextConfig;
""",
    "middleware.ts": """\
import { type NextRequest, NextResponse } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

export async function middleware(request: NextRequest) {
  return await updateSession(request);
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|favicon.svg|.*\\\\.(?:svg|png|jpg|jpeg)$).*)",
  ],
};
""",
    "lib/supabase/client.ts": """\
// Browser-side Supabase client - safe to use in client components.
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
""",
    "lib/supabase/server.ts": """\
// Server-side Supabase client for Server Components / Route Handlers.
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // Called from a Server Component with no write access - ignore,
            // middleware refreshes the session on the next request instead.
          }
        },
      },
    },
  );
}
""",
    "lib/supabase/middleware.ts": """\
// Refreshes the Supabase session on every request so server components
// always see a valid (non-expired) auth state.
import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  await supabase.auth.getUser();
  return response;
}
""",
    "lib/wagmi/config.ts": """\
// wagmi + RainbowKit configuration. Supports MetaMask, Rainbow,
// Zerion, Coinbase Wallet, and any other WalletConnect-compatible
// wallet out of the box, per the project's wallet-auth requirement.
import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { mainnet, sepolia } from "wagmi/chains";

export const wagmiConfig = getDefaultConfig({
  appName: "StableShield AI",
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID ?? "",
  chains: [mainnet, sepolia],
  ssr: true,
});
""",
    "lib/siwe.ts": """\
// Client-side Sign-In With Ethereum helper. Builds the EIP-4361 message
// the connected wallet signs, then calls our siwe-nonce / siwe-verify
// Supabase Edge Functions to establish a session.
import { SiweMessage } from "siwe";

const FUNCTIONS_URL = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1`;

export async function fetchNonce(address: string): Promise<string> {
  const res = await fetch(`${FUNCTIONS_URL}/siwe-nonce`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address }),
  });
  if (!res.ok) throw new Error("failed to fetch SIWE nonce");
  const { nonce } = await res.json();
  return nonce;
}

export function buildSiweMessage(params: {
  address: string;
  chainId: number;
  nonce: string;
}): SiweMessage {
  return new SiweMessage({
    domain: typeof window !== "undefined" ? window.location.host : "stableshield.ai",
    address: params.address,
    statement: "Sign in to StableShield AI to access the risk intelligence dashboard.",
    uri: typeof window !== "undefined" ? window.location.origin : "https://stableshield.ai",
    version: "1",
    chainId: params.chainId,
    nonce: params.nonce,
  });
}

export async function verifySiwe(message: string, signature: string) {
  const res = await fetch(`${FUNCTIONS_URL}/siwe-verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, signature }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error ?? "SIWE verification failed");
  }
  return res.json() as Promise<{ address: string; userId: string; actionLink: string }>;
}
""",
    "lib/genlayer/contract-interface.ts": """\
// Mirrors intelligent-contracts/stablescore_oracle/contract.gpy.
// Kept here so the frontend can render the oracle panel and call
// read methods without re-deriving the contract shape by hand.
export interface StableScoreOracleContract {
  register_stablecoin(symbol: string, name: string): void;
  update_score(symbol: string, rating: string, score: number): void;
  get_score(symbol: string): {
    symbol: string;
    rating: string;
    score: number;
    peg: number;
    reserve_ratio: number;
    updated_at: string;
  };
  get_history(symbol: string, limit: number): Array<{
    rating: string;
    score: number;
    recorded_at: string;
  }>;
  is_safe(symbol: string, min_rating: string): boolean;
}

export const STABLESCORE_ORACLE_METHODS = [
  "register_stablecoin",
  "update_score",
  "get_score",
  "get_history",
  "is_safe",
] as const;
""",
    "lib/genlayer/client.ts": """\
// Thin client for read-only calls against the deployed StableScoreOracle
// Intelligent Contract on GenLayer StudioNet. Write calls (update_score)
// are performed server-side by the publish-to-genlayer Edge Function,
// which holds the service credentials - the frontend never signs
// GenLayer transactions directly.
const RPC_URL = process.env.NEXT_PUBLIC_GENLAYER_STUDIONET_RPC_URL;
const CONTRACT_ADDRESS = process.env.NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS;

export interface GenLayerScoreResult {
  symbol: string;
  rating: string;
  score: number;
  peg: number;
  reserve_ratio: number;
  updated_at: string;
}

export async function getOnChainScore(
  symbol: string,
): Promise<GenLayerScoreResult | null> {
  if (!RPC_URL || !CONTRACT_ADDRESS) {
    // Contract not deployed/configured yet (pre-STEP 10) - caller should
    // fall back to the off-chain Supabase score.
    return null;
  }

  const res = await fetch(RPC_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "gen_call",
      params: [{ to: CONTRACT_ADDRESS, function: "get_score", args: [symbol] }],
    }),
  });

  if (!res.ok) return null;
  const json = await res.json();
  return json.result ?? null;
}

export function isOracleConfigured(): boolean {
  return Boolean(RPC_URL && CONTRACT_ADDRESS);
}
""",
    "types/risk.ts": """\
import type { StableScoreGrade } from "@stableshield/shared-types";

export interface RiskScore {
  stablecoin_id: string;
  rating: StableScoreGrade;
  score_numeric: number;
  reserve_subscore: number | null;
  issuer_subscore: number | null;
  peg_subscore: number | null;
  regulatory_subscore: number | null;
  sentiment_subscore: number | null;
  updated_at: string;
}

export interface Stablecoin {
  id: string;
  symbol: string;
  name: string;
  chain: string;
  contract_address: string | null;
  decimals: number;
}

export interface StablecoinWithScore extends Stablecoin {
  risk_scores: RiskScore | null;
}

export interface RiskScoreHistoryEntry {
  rating: StableScoreGrade;
  score_numeric: number;
  reason_summary: string | null;
  recorded_at: string;
}

export interface Alert {
  id: string;
  stablecoin_id: string;
  severity: "info" | "warning" | "critical";
  message: string;
  triggered_at: string;
  resolved_at: string | null;
}
""",
    "types/genlayer.ts": """\
export interface OraclePublication {
  id: string;
  stablecoin_id: string;
  tx_hash: string | null;
  contract_address: string;
  network: string;
  published_rating: string;
  published_at: string;
  status: "pending" | "confirmed" | "failed";
}
""",
    "types/database.types.ts": """\
// Hand-authored mirror of the Supabase schema (backend/supabase/migrations).
// Replace with `supabase gen types typescript` output once the project is
// live - keeping this checked in means the frontend type-checks before
// that step happens.
export interface Database {
  public: {
    Tables: {
      wallets: {
        Row: {
          id: string;
          address: string;
          chain_id: number;
          created_at: string;
          last_login_at: string | null;
        };
      };
      profiles: {
        Row: {
          id: string;
          wallet_id: string;
          display_name: string | null;
          tier: "free" | "pro" | "institutional";
          created_at: string;
        };
      };
      stablecoins: {
        Row: {
          id: string;
          symbol: string;
          name: string;
          issuer_id: string | null;
          chain: string;
          contract_address: string | null;
          decimals: number;
          launched_at: string | null;
        };
      };
      risk_scores: {
        Row: {
          id: string;
          stablecoin_id: string;
          rating: string;
          score_numeric: number;
          reserve_subscore: number | null;
          issuer_subscore: number | null;
          peg_subscore: number | null;
          regulatory_subscore: number | null;
          sentiment_subscore: number | null;
          updated_at: string;
        };
      };
      risk_score_history: {
        Row: {
          id: string;
          stablecoin_id: string;
          rating: string;
          score_numeric: number;
          reason_summary: string | null;
          recorded_at: string;
        };
      };
      alerts: {
        Row: {
          id: string;
          stablecoin_id: string;
          severity: "info" | "warning" | "critical";
          message: string;
          triggered_at: string;
          resolved_at: string | null;
        };
      };
      oracle_publications: {
        Row: {
          id: string;
          stablecoin_id: string;
          tx_hash: string | null;
          contract_address: string;
          network: string;
          published_rating: string;
          published_at: string;
          status: "pending" | "confirmed" | "failed";
        };
      };
    };
  };
}
""",
}


def main() -> None:
    created = []
    for rel, content in FILES.items():
        path = WEB / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(rel)

    print(f"Web root: {WEB}")
    print(f"Created {len(created)} file(s).")
    for f in created:
        print(f"  + {f}")
    if not created:
        print("Nothing to do - all files already exist.")


if __name__ == "__main__":
    main()
