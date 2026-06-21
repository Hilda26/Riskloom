// api-v1-scores: public, API-key-gated read access to current
// StableScore ratings for exchanges/fintechs/wallets/institutions.
import { createClient } from "npm:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const apiKey = req.headers.get("x-api-key");
    if (!apiKey) {
      return new Response(JSON.stringify({ error: "x-api-key header is required" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const keyHash = await sha256(apiKey);
    const { data: keyRow, error: keyErr } = await supabase
      .from("api_keys")
      .select("id, scopes, revoked_at")
      .eq("key_hash", keyHash)
      .is("revoked_at", null)
      .maybeSingle();

    if (keyErr || !keyRow || !keyRow.scopes.includes("read:scores")) {
      return new Response(JSON.stringify({ error: "invalid or unauthorized api key" }), {
        status: 403,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const url = new URL(req.url);
    const symbol = url.searchParams.get("symbol");

    let query = supabase
      .from("risk_scores")
      .select("rating, score_numeric, updated_at, stablecoins(symbol, name)");

    if (symbol) {
      const { data: coin } = await supabase
        .from("stablecoins")
        .select("id")
        .eq("symbol", symbol.toUpperCase())
        .maybeSingle();
      if (!coin) {
        return new Response(JSON.stringify({ error: "unknown symbol" }), {
          status: 404,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      query = query.eq("stablecoin_id", coin.id);
    }

    const { data, error } = await query;
    if (error) throw error;

    return new Response(JSON.stringify({ data }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

async function sha256(input: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
