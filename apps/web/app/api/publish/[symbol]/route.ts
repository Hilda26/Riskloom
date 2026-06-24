// User-triggered on-chain publish. Proxies to the publish-to-genlayer
// Supabase Edge Function (which holds the GenLayer signing key) so a
// click in the UI produces a real `update_score` transaction on the
// StableScoreOracle contract - visible on the GenLayer Studio explorer
// going through the full consensus lifecycle.
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

// GenLayer consensus on a write can take a while; give the request room
// rather than letting the platform cut it off at the default timeout.
export const maxDuration = 60;

export async function POST(
  _req: Request,
  { params }: { params: Promise<{ symbol: string }> },
) {
  const { symbol } = await params;
  const sym = symbol.toUpperCase();

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!supabaseUrl || !anonKey) {
    return NextResponse.json(
      { error: "Supabase is not configured" },
      { status: 500 },
    );
  }

  // Resolve the stablecoin id the Edge Function expects.
  const supabase = await createClient();
  const { data: coin } = await supabase
    .from("stablecoins")
    .select("id")
    .eq("symbol", sym)
    .maybeSingle();
  if (!coin) {
    return NextResponse.json({ error: `unknown symbol ${sym}` }, { status: 404 });
  }

  try {
    const res = await fetch(`${supabaseUrl}/functions/v1/publish-to-genlayer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${anonKey}`,
      },
      body: JSON.stringify({ stablecoin_id: coin.id, symbol: sym }),
    });
    const body = await res.json().catch(() => ({}));
    // Pass the Edge Function's own status through (e.g. 503 when the
    // GenLayer secrets aren't set) so the UI can show a useful message.
    return NextResponse.json(body, { status: res.status });
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 502 });
  }
}
