"""
StableShield AI - Frontend Hooks Writer (STEP 6, part 5)
Run from the repository root: python scripts/write_frontend_hooks.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "apps" / "web"

FILES = {

"hooks/useStableScores.ts": """\
"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { StablecoinWithScore } from "@/types/risk";

export function useStableScores(initial: StablecoinWithScore[] = []) {
  const [items, setItems] = useState<StablecoinWithScore[]>(initial);

  useEffect(() => {
    const supabase = createClient();

    const channel = supabase
      .channel("risk_scores_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "risk_scores" },
        async () => {
          const { data } = await supabase
            .from("stablecoins")
            .select("*, risk_scores(*)")
            .order("symbol");
          if (data) setItems(data as unknown as StablecoinWithScore[]);
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return items;
}
""",

"hooks/useWalletAuth.ts": """\
"use client";

import { useEffect, useRef } from "react";
import { useAccount, useChainId, useSignMessage } from "wagmi";
import { buildSiweMessage, fetchNonce, verifySiwe } from "@/lib/siwe";

// Triggers the Sign-In With Ethereum flow the first time a wallet
// connects in this session, then exchanges the resulting magic link
// for a Supabase session via /auth/callback.
export function useWalletAuth() {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { signMessageAsync } = useSignMessage();
  const attempted = useRef<string | null>(null);

  useEffect(() => {
    if (!isConnected || !address) return;
    if (attempted.current === address) return;
    attempted.current = address;

    (async () => {
      try {
        const nonce = await fetchNonce(address);
        const siweMessage = buildSiweMessage({ address, chainId, nonce });
        const preparedMessage = siweMessage.prepareMessage();
        const signature = await signMessageAsync({ message: preparedMessage });
        const { tokenHash, type } = await verifySiwe(preparedMessage, signature);
        window.location.href = `/auth/callback?token_hash=${tokenHash}&type=${type}`;
      } catch (err) {
        console.error("SIWE sign-in failed", err);
        attempted.current = null;
      }
    })();
  }, [address, isConnected, chainId, signMessageAsync]);
}
""",

"hooks/useOraclePublication.ts": """\
"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { OraclePublication } from "@/types/genlayer";

export function useOraclePublication(stablecoinId: string | null) {
  const [publications, setPublications] = useState<OraclePublication[]>([]);

  useEffect(() => {
    if (!stablecoinId) return;
    const supabase = createClient();

    supabase
      .from("oracle_publications")
      .select("*")
      .eq("stablecoin_id", stablecoinId)
      .order("published_at", { ascending: false })
      .limit(20)
      .then(({ data }) => {
        if (data) setPublications(data as OraclePublication[]);
      });
  }, [stablecoinId]);

  return publications;
}
""",

"hooks/useRealtimeAlerts.ts": """\
"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { Alert } from "@/types/risk";

export function useRealtimeAlerts(initial: Alert[] = []) {
  const [alerts, setAlerts] = useState<Alert[]>(initial);

  useEffect(() => {
    const supabase = createClient();

    const channel = supabase
      .channel("alerts_changes")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "alerts" },
        (payload) => {
          setAlerts((prev) => [payload.new as Alert, ...prev]);
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return alerts;
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
