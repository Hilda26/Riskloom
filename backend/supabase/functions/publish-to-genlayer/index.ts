// publish-to-genlayer: pushes a finalized StableScore to the
// StableScoreOracle Intelligent Contract on GenLayer StudioNet via the
// official genlayer-js SDK (createClient/createAccount/writeContract -
// not hand-rolled JSON-RPC, which silently encodes calldata wrong).
//
// NOTE: GENLAYER_CONTRACT_ADDRESS, GENLAYER_STUDIONET_RPC_URL, and
// GENLAYER_PRIVATE_KEY are set once the contract is deployed and a
// funded service account exists (STEP 7/10). Until then this function
// records a 'failed' publication with a clear error message.
import { createClient } from "npm:@supabase/supabase-js@2";
import { createClient as createGenLayerClient, createAccount } from "npm:genlayer-js@1.1.8";
import { studionet } from "npm:genlayer-js@1.1.8/chains";
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
      .select(
        "rating, score_numeric, reserve_subscore, issuer_subscore, peg_subscore, regulatory_subscore, sentiment_subscore",
      )
      .eq("stablecoin_id", stablecoin_id)
      .single();
    if (scoreErr || !score) throw new Error("no score found for stablecoin");

    const { data: coin } = await supabase
      .from("stablecoins")
      .select("peg_price")
      .eq("id", stablecoin_id)
      .single();

    const contractAddress = Deno.env.get("GENLAYER_CONTRACT_ADDRESS");
    const rpcUrl = Deno.env.get("GENLAYER_STUDIONET_RPC_URL");
    const privateKey = Deno.env.get("GENLAYER_PRIVATE_KEY");

    if (!contractAddress || !rpcUrl || !privateKey) {
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
            "GENLAYER_CONTRACT_ADDRESS / GENLAYER_STUDIONET_RPC_URL / GENLAYER_PRIVATE_KEY not configured yet (STEP 7/10)",
        }),
        {
          status: 503,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    // Calls update_score on StableScoreOracle via the official
    // genlayer-js SDK, matching intelligent-contracts/stablescore_oracle/
    // contract.gpy::update_score exactly - the contract re-derives the
    // composite score and uses its LLM-backed equivalence principle to
    // assign + justify the letter grade, it does not just accept our
    // off-chain rating as given.
    const pegPriceBps = Math.round((coin?.peg_price ?? 1) * 10_000);
    const reserveRatioBps = Math.round((score.reserve_subscore ?? 0) * 100);
    const evidenceSummary =
      `reserve=${score.reserve_subscore ?? "n/a"} issuer=${score.issuer_subscore ?? "n/a"} ` +
      `peg=${score.peg_subscore ?? "n/a"} regulatory=${score.regulatory_subscore ?? "n/a"} ` +
      `sentiment=${score.sentiment_subscore ?? "n/a"}`;

    const account = createAccount(privateKey as `0x${string}`);
    const genlayer = createGenLayerClient({
      chain: studionet,
      endpoint: rpcUrl,
      account,
    });

    let status: "confirmed" | "failed" = "failed";
    let txHash: string | null = null;
    try {
      txHash = await genlayer.writeContract({
        address: contractAddress as `0x${string}`,
        functionName: "update_score",
        args: [
          symbol,
          Math.round(score.reserve_subscore ?? 0),
          Math.round(score.issuer_subscore ?? 0),
          Math.round(score.peg_subscore ?? 0),
          Math.round(score.regulatory_subscore ?? 0),
          Math.round(score.sentiment_subscore ?? 0),
          pegPriceBps,
          reserveRatioBps,
          evidenceSummary,
          new Date().toISOString(),
        ],
        value: 0n,
      });
      try {
        await genlayer.waitForTransactionReceipt({ hash: txHash as `0x${string}` });
        status = "confirmed";
      } catch (waitErr) {
        // waitForTransactionReceipt polls for a specific status and can
        // throw a timeout even when the transaction already finalized
        // successfully past that status (confirmed against a real
        // StudioNet tx during testing) - fall back to checking the
        // transaction's actual recorded outcome directly instead of
        // assuming failure.
        console.error("waitForTransactionReceipt threw, checking tx directly", waitErr);
        const tx: any = await genlayer.getTransaction({ hash: txHash as `0x${string}` });
        const resultName = tx.result_name ?? tx.resultName;
        const leaderSucceeded =
          (tx.consensus_data?.leader_receipt ?? tx.consensusData?.leaderReceipt)?.[0]
            ?.execution_result === "SUCCESS";
        const consensusReached = resultName === "MAJORITY_AGREE" || resultName === "AGREE";
        status = leaderSucceeded && consensusReached ? "confirmed" : "failed";
      }
    } catch (writeErr) {
      console.error("genlayer writeContract failed", writeErr);
    }

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
