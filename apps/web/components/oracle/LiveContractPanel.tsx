"use client";

import { useEffect, useState } from "react";
import { getOnChainScore, isOracleConfigured, type GenLayerScoreResult } from "@/lib/genlayer/client";

const FALLBACK_SNIPPET = `<span class="cm"># Riskloom StableScore Oracle</span>
<span class="cm"># Network: StudioNet - GEN token</span>

<span class="ck">contract</span> <span class="cs">StableScoreOracle</span>:

  <span class="ck">def</span> <span class="cv">get_score</span>(symbol: <span class="cs">str</span>) -> <span class="cs">dict</span>:
    <span class="ck">return</span> {
      <span class="cv">"symbol"</span>: symbol,
      <span class="cv">"rating"</span>: <span class="cs">"AAA"</span>,
      <span class="cv">"score"</span>: <span class="cn">96.4</span>,
      <span class="cv">"peg"</span>: <span class="cn">1.0001</span>,
      <span class="cv">"reserve_ratio"</span>: <span class="cn">102.3</span>,
      <span class="cv">"updated_at"</span>: <span class="cv">"pending deployment"</span>
    }

<span class="cm"># Contract not yet deployed - this is the expected interface.</span>
<span class="cm"># Deploy via GenLayer Studio, then set GENLAYER_CONTRACT_ADDRESS.</span>`;

export function LiveContractPanel({ symbol = "USDC" }: { symbol?: string }) {
  const [result, setResult] = useState<GenLayerScoreResult | null>(null);
  const [configured, setConfigured] = useState(false);

  useEffect(() => {
    setConfigured(isOracleConfigured());
    getOnChainScore(symbol).then(setResult).catch(() => setResult(null));
  }, [symbol]);

  return (
    <div className="oracle-right">
      <div className="oracle-lbl">GenLayer Contract - Live Call</div>
      {configured && result ? (
        <div className="code-block">
          {`# Live read from StableScoreOracle\nget_score("${result.symbol}") -> {\n  rating: "${result.rating}",\n  score: ${result.score},\n  peg: ${result.peg},\n  reserve_ratio: ${result.reserve_ratio},\n  updated_at: "${result.updated_at}"\n}`}
        </div>
      ) : (
        <div className="code-block" dangerouslySetInnerHTML={{ __html: FALLBACK_SNIPPET }} />
      )}
    </div>
  );
}
