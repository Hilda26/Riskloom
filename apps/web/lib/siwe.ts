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
  return res.json() as Promise<{
    address: string;
    userId: string;
    tokenHash: string;
    type: string;
  }>;
}
