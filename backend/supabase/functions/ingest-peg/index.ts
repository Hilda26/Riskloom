// ingest-peg: staging ingestion endpoint for the Peg Stability module.
// Normalizes incoming provider payloads into the `peg_snapshots` table.
// Source connectors (HTTP pulls, file drops, partner webhooks) are
// expected to call this endpoint; scoring is recomputed downstream by
// compute-stablescore once new rows land.
import { createClient } from "npm:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const payload = await req.json();
    const rows = Array.isArray(payload) ? payload : [payload];

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const { error, data } = await supabase.from("peg_snapshots").insert(rows).select("id");
    if (error) throw error;

    await supabase.from("audit_log").insert({
      actor: "ingest-peg",
      action: "insert",
      target_table: "peg_snapshots",
      payload: { count: rows.length },
    });

    return new Response(JSON.stringify({ inserted: data?.length ?? 0 }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
