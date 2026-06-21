// Thin client for read-only calls against the deployed StableScoreOracle
// Intelligent Contract on GenLayer StudioNet, via the official
// genlayer-js SDK. Write calls (update_score) are performed
// server-side by the publish-to-genlayer Edge Function, which holds
// the service credentials - the frontend never signs GenLayer
// transactions directly.
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

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

  try {
    const client = createClient({ chain: studionet, endpoint: RPC_URL });
    const result = await client.readContract({
      address: CONTRACT_ADDRESS as `0x${string}`,
      functionName: "get_score",
      args: [symbol],
    });

    // get_score never throws - an unregistered symbol comes back as
    // { error: "..." } instead, which the caller should treat as absent.
    if (!result || typeof result !== "object" || "error" in result) {
      return null;
    }
    return result as unknown as GenLayerScoreResult;
  } catch {
    return null;
  }
}

export function isOracleConfigured(): boolean {
  return Boolean(RPC_URL && CONTRACT_ADDRESS);
}
