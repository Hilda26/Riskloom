"""
StableShield AI - Supabase Edge Functions Writer
Writes all backend Edge Functions (STEP 5).
Run from the repository root: python scripts/write_backend_functions.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNCTIONS_DIR = ROOT / "backend" / "supabase" / "functions"

SHARED_CORS = """\
export const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};
"""

SIWE_NONCE = """\
// siwe-nonce: issues a one-time nonce for Sign-In With Ethereum
import { createClient } from "npm:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { address } = await req.json();
    if (!address || typeof address !== "string") {
      return new Response(JSON.stringify({ error: "address is required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const nonce = crypto.randomUUID().replace(/-/g, "");
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000).toISOString();

    const { error } = await supabase.from("siwe_nonces").insert({
      address: address.toLowerCase(),
      nonce,
      expires_at: expiresAt,
    });

    if (error) throw error;

    return new Response(JSON.stringify({ nonce, expiresAt }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
"""

SIWE_VERIFY = """\
// siwe-verify: verifies a signed SIWE message, links the wallet to a
// Supabase auth identity, and returns a session.
import { createClient } from "npm:@supabase/supabase-js@2";
import { SiweMessage } from "npm:siwe@2";
import { corsHeaders } from "../_shared/cors.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { message, signature } = await req.json();
    if (!message || !signature) {
      return new Response(
        JSON.stringify({ error: "message and signature are required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    const siwe = new SiweMessage(message);
    const { data: fields } = await siwe.verify({ signature });
    const address = fields.address.toLowerCase();

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    // Nonce must exist, be unconsumed, and unexpired
    const { data: nonceRow, error: nonceErr } = await supabase
      .from("siwe_nonces")
      .select("*")
      .eq("address", address)
      .eq("nonce", fields.nonce)
      .is("consumed_at", null)
      .gt("expires_at", new Date().toISOString())
      .single();

    if (nonceErr || !nonceRow) {
      throw new Error("invalid or expired nonce");
    }

    await supabase
      .from("siwe_nonces")
      .update({ consumed_at: new Date().toISOString() })
      .eq("id", nonceRow.id);

    // Upsert wallet
    const { data: wallet, error: walletErr } = await supabase
      .from("wallets")
      .upsert(
        { address, chain_id: fields.chainId, last_login_at: new Date().toISOString() },
        { onConflict: "address" },
      )
      .select()
      .single();
    if (walletErr) throw walletErr;

    // Find or create the auth user + profile bound to this wallet
    const email = `${address}@wallet.stableshield.local`;
    let userId: string;

    const { data: existing } = await supabase
      .from("profiles")
      .select("id")
      .eq("wallet_id", wallet.id)
      .maybeSingle();

    if (existing) {
      userId = existing.id;
    } else {
      const { data: created, error: createErr } =
        await supabase.auth.admin.createUser({
          email,
          email_confirm: true,
          user_metadata: { wallet_address: address },
        });
      if (createErr) throw createErr;
      userId = created.user.id;

      const { error: profileErr } = await supabase.from("profiles").insert({
        id: userId,
        wallet_id: wallet.id,
      });
      if (profileErr) throw profileErr;
    }

    const { data: link, error: linkErr } =
      await supabase.auth.admin.generateLink({
        type: "magiclink",
        email,
      });
    if (linkErr) throw linkErr;

    // Return the bare hashed_token instead of properties.action_link.
    // action_link points at GoTrue's own hosted /auth/v1/verify
    // endpoint on the *Supabase* domain, which then 302-redirects to
    // the project's Site URL with the session in a URL hash fragment -
    // that depends on Site URL being correctly configured AND on some
    // page reading window.location.hash, neither of which our
    // /auth/callback route (which expects ?token_hash=&type= query
    // params per Supabase's documented SSR/PKCE pattern) does. Using
    // hashed_token directly with our own same-origin /auth/callback
    // keeps the whole redirect on whatever domain the user is
    // actually on, independent of the Site URL setting.
    return new Response(
      JSON.stringify({
        address,
        userId,
        tokenHash: link.properties.hashed_token,
        type: "magiclink",
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 401,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
"""

COMPUTE_STABLESCORE = """\
// compute-stablescore: combines the five risk modules into one
// composite StableScore rating and writes current + history rows.
import { createClient } from "npm:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";

const GRADE_BOUNDARIES: [number, string][] = [
  [97, "AAA"],
  [90, "AA"],
  [80, "A"],
  [65, "BBB"],
  [50, "BB"],
  [35, "B"],
  [15, "CCC"],
  [0, "D"],
];

function scoreToGrade(score: number): string {
  for (const [min, grade] of GRADE_BOUNDARIES) {
    if (score >= min) return grade;
  }
  return "D";
}

// Weighted composite across the five intelligence modules.
function computeComposite(sub: {
  reserve: number;
  issuer: number;
  peg: number;
  regulatory: number;
  sentiment: number;
}): number {
  return (
    sub.reserve * 0.3 +
    sub.issuer * 0.2 +
    sub.peg * 0.25 +
    sub.regulatory * 0.15 +
    sub.sentiment * 0.1
  );
}

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
"""

PUBLISH_TO_GENLAYER = """\
// publish-to-genlayer: pushes a finalized StableScore to the
// StableScoreOracle Intelligent Contract on GenLayer StudioNet.
//
// NOTE: GENLAYER_CONTRACT_ADDRESS is set once the contract is deployed
// via GenLayer Studio (STEP 7 / STEP 10). Until then this function
// will record a 'failed' publication with a clear error message.
import { createClient } from "npm:@supabase/supabase-js@2";
import { corsHeaders } from "../_shared/cors.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { stablecoin_id, symbol } = await req.json();
    if (!stablecoin_id || !symbol) {
      return new Response(
        JSON.stringify({ error: "stablecoin_id and symbol are required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const { data: score, error: scoreErr } = await supabase
      .from("risk_scores")
      .select("rating, score_numeric")
      .eq("stablecoin_id", stablecoin_id)
      .single();
    if (scoreErr || !score) throw new Error("no score found for stablecoin");

    const contractAddress = Deno.env.get("GENLAYER_CONTRACT_ADDRESS");
    const rpcUrl = Deno.env.get("GENLAYER_STUDIONET_RPC_URL");

    if (!contractAddress || !rpcUrl) {
      await supabase.from("oracle_publications").insert({
        stablecoin_id,
        contract_address: contractAddress ?? "unset",
        network: "studionet",
        published_rating: score.rating,
        status: "failed",
      });
      return new Response(
        JSON.stringify({
          error:
            "GENLAYER_CONTRACT_ADDRESS / GENLAYER_STUDIONET_RPC_URL not configured yet - deploy the contract first (STEP 7/10)",
        }),
        {
          status: 503,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    // GenLayer StudioNet JSON-RPC call invoking update_score on
    // StableScoreOracle. Exact method name matches intelligent-contracts/
    // stablescore_oracle/contract.gpy::update_score.
    const rpcResponse = await fetch(rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "gen_call",
        params: [
          {
            to: contractAddress,
            function: "update_score",
            args: [symbol, score.rating, score.score_numeric],
          },
        ],
      }),
    });
    const rpcResult = await rpcResponse.json();

    const status = rpcResult.error ? "failed" : "confirmed";
    const txHash = rpcResult.result?.tx_hash ?? null;

    await supabase.from("oracle_publications").insert({
      stablecoin_id,
      tx_hash: txHash,
      contract_address: contractAddress,
      network: "studionet",
      published_rating: score.rating,
      status,
    });

    return new Response(JSON.stringify({ status, txHash, rating: score.rating }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
"""

INGEST_TEMPLATE = """\
// {name}: staging ingestion endpoint for the {module} module.
// Normalizes incoming provider payloads into the `{table}` table.
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

    const { error, data } = await supabase.from("{table}").insert(rows).select("id");
    if (error) throw error;

    await supabase.from("audit_log").insert({
      actor: "ingest-{slug}",
      action: "insert",
      target_table: "{table}",
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
"""

API_V1_SCORES = """\
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
"""

API_V1_HISTORY = """\
// api-v1-history: public, API-key-gated read access to historical
// StableScore ratings for a given symbol.
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

    const url = new URL(req.url);
    const symbol = url.searchParams.get("symbol");
    const limit = Number(url.searchParams.get("limit") ?? "100");
    if (!symbol) {
      return new Response(JSON.stringify({ error: "symbol query param is required" }), {
        status: 400,
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

    const { data, error } = await supabase
      .from("risk_score_history")
      .select("rating, score_numeric, reason_summary, recorded_at")
      .eq("stablecoin_id", coin.id)
      .order("recorded_at", { ascending: false })
      .limit(Math.min(limit, 500));
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
"""

HEALTH = """\
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
"""

INGEST_SPECS = [
    ("ingest-reserves", "Reserve Health", "reserve_reports", "reserves"),
    ("ingest-peg", "Peg Stability", "peg_snapshots", "peg"),
    ("ingest-sentiment", "Sentiment Intelligence", "sentiment_signals", "sentiment"),
    ("ingest-regulatory", "Regulatory Risk", "regulatory_events", "regulatory"),
]


def main() -> None:
    created = []

    shared_dir = FUNCTIONS_DIR / "_shared"
    shared_dir.mkdir(parents=True, exist_ok=True)
    cors_path = shared_dir / "cors.ts"
    if not cors_path.exists():
        cors_path.write_text(SHARED_CORS, encoding="utf-8")
        created.append("_shared/cors.ts")

    simple_functions = {
        "siwe-nonce": SIWE_NONCE,
        "siwe-verify": SIWE_VERIFY,
        "compute-stablescore": COMPUTE_STABLESCORE,
        "publish-to-genlayer": PUBLISH_TO_GENLAYER,
        "api-v1-scores": API_V1_SCORES,
        "api-v1-history": API_V1_HISTORY,
        "health": HEALTH,
    }

    for name, content in simple_functions.items():
        func_dir = FUNCTIONS_DIR / name
        func_dir.mkdir(parents=True, exist_ok=True)
        path = func_dir / "index.ts"
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(f"{name}/index.ts")

    for name, module, table, slug in INGEST_SPECS:
        func_dir = FUNCTIONS_DIR / name
        func_dir.mkdir(parents=True, exist_ok=True)
        path = func_dir / "index.ts"
        if not path.exists():
            content = (
                INGEST_TEMPLATE.replace("{name}", name)
                .replace("{module}", module)
                .replace("{table}", table)
                .replace("{slug}", slug)
            )
            path.write_text(content, encoding="utf-8")
            created.append(f"{name}/index.ts")

    print(f"Functions directory: {FUNCTIONS_DIR}")
    print(f"Created {len(created)} file(s).")
    for f in created:
        print(f"  + {f}")
    if not created:
        print("Nothing to do - all function files already exist.")


if __name__ == "__main__":
    main()
