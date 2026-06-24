// Server-side on-chain read of the StableScoreOracle. Running the
// genlayer-js read here (Node runtime) rather than in the browser means
// the oracle panel never depends on the heavy SDK bundling cleanly into
// the client or on the GenLayer RPC's browser CORS behaviour - the
// client just fetches plain JSON from our own origin.
import { NextResponse } from "next/server";
import { getOnChainScore, isOracleConfigured } from "@/lib/genlayer/client";

export const revalidate = 30;

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ symbol: string }> },
) {
  const { symbol } = await params;

  if (!isOracleConfigured()) {
    return NextResponse.json({ configured: false, score: null });
  }

  const score = await getOnChainScore(symbol.toUpperCase());
  return NextResponse.json({ configured: true, score });
}
