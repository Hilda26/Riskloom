// compute-stablescore: combines the five risk modules into one
// composite StableScore rating and writes current + history rows.
import { createClient } from "npm:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";
import { computeComposite, scoreToGrade } from "../_shared/scoring.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { stablecoin_id, reserve, issuer, peg, regulatory, sentiment, reason } =
      await req.json();

    if (
      !stablecoin_id ||
      [reserve, issuer, peg, regulatory, sentiment].some(
        (v) => typeof v !== "number",
      )
    ) {
      return new Response(
        JSON.stringify({
          error:
            "stablecoin_id and numeric reserve/issuer/peg/regulatory/sentiment subscores are required",
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    const composite = computeComposite({ reserve, issuer, peg, regulatory, sentiment });
    const rating = scoreToGrade(composite);

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const { error: upsertErr } = await supabase.from("risk_scores").upsert(
      {
        stablecoin_id,
        rating,
        score_numeric: composite,
        reserve_subscore: reserve,
        issuer_subscore: issuer,
        peg_subscore: peg,
        regulatory_subscore: regulatory,
        sentiment_subscore: sentiment,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "stablecoin_id" },
    );
    if (upsertErr) throw upsertErr;

    const { error: historyErr } = await supabase.from("risk_score_history").insert({
      stablecoin_id,
      rating,
      score_numeric: composite,
      reason_summary: reason ?? null,
    });
    if (historyErr) throw historyErr;

    return new Response(JSON.stringify({ rating, score: composite }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
