// health: lightweight liveness/readiness check for monitoring.
import { createClient } from "npm:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );
    const { error } = await supabase.from("stablecoins").select("id").limit(1);

    const ok = !error;
    return new Response(
      JSON.stringify({
        status: ok ? "healthy" : "degraded",
        database: ok ? "reachable" : (error?.message ?? JSON.stringify(error)),
        timestamp: new Date().toISOString(),
      }),
      {
        status: ok ? 200 : 503,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ status: "unhealthy", error: String(err) }),
      {
        status: 503,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  }
});
