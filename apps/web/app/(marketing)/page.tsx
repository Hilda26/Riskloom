import { getStablecoinsWithLiveData } from "@/lib/stablecoins";
import { Ticker } from "@/components/layout/Ticker";
import { RatingBand } from "@/components/dashboard/RatingBand";
import { KpiRow } from "@/components/dashboard/KpiRow";
import { StablecoinTable } from "@/components/dashboard/StablecoinTable";
import { OracleIntegrationList } from "@/components/oracle/OracleIntegrationList";
import { LiveContractPanel } from "@/components/oracle/LiveContractPanel";
import { LinkButton } from "@/components/ui/Button";
import { LoomMark } from "@/components/layout/LoomMark";
import type { StablecoinWithScore } from "@/types/risk";
import type { StableScoreGrade } from "@stableshield/shared-types";

export const revalidate = 60;

function countByGrade(items: StablecoinWithScore[]): Record<StableScoreGrade, number> {
  const counts: Record<StableScoreGrade, number> = {
    AAA: 0, AA: 0, A: 0, BBB: 0, BB: 0, B: 0, CCC: 0, D: 0,
  };
  for (const item of items) {
    if (item.risk_scores) counts[item.risk_scores.rating] += 1;
  }
  return counts;
}

export default async function LandingPage() {
  const stablecoins = await getStablecoinsWithLiveData();
  const counts = countByGrade(stablecoins);
  const previewItems = stablecoins.slice(0, 4);

  return (
    <>
      <Ticker items={stablecoins} />

      <section className="hero">
        <div className="hero-eye">
          <span className="eye-dot" />
          Powered by GenLayer Intelligent Contracts - StudioNet
        </div>
        <h1 className="ht">
          <span className="ln"><span className="w" style={{ animationDelay: ".15s" }}>The stablecoin</span></span>
          <span className="ln"><span className="gw" style={{ animationDelay: ".38s" }}>risk intelligence</span></span>
          <span className="ln"><span className="w" style={{ animationDelay: ".62s" }}>layer.</span></span>
        </h1>
        <p className="hero-sub">
          Riskloom continuously analyzes reserves, issuer health, peg stability, and regulatory
          exposure - publishing real-time <span className="hl">StableScore&trade;</span> ratings
          on-chain for every major stablecoin.
        </p>
        <div className="hero-btns">
          <LinkButton href="/dashboard" variant="primary" arrow>Explore the Dashboard</LinkButton>
          <LinkButton href="#oracle" variant="ghost">View Risk Oracle</LinkButton>
        </div>
      </section>

      <div className="score-band" id="ratings">
        <RatingBand counts={counts} />
      </div>

      <div className="divider" />
      <div className="sec" id="dashboard">
        <div className="reveal">
          <div className="sec-lbl">Live Platform</div>
          <h2 className="st">Your risk <span className="gs">command center.</span></h2>
          <p className="sec-sub">
            Real-time StableScore&trade; ratings, reserve analysis, peg monitoring, and early
            warnings - all in one dashboard.
          </p>
        </div>
        <div className="dash reveal">
          <div className="dash-bar">
            <span className="d-dot dd-r" /><span className="d-dot dd-y" /><span className="d-dot dd-g" />
            <span className="d-url">app.riskloom.io / dashboard</span>
          </div>
          <div className="dash-grid">
            <div className="dsb">
              <div className="dsb-logo"><LoomMark size={16} /> Riskloom</div>
              <div className="dsb-s">Overview</div>
              <div className="dsb-i act">&#11041; Dashboard<span className="dsb-badge">live</span></div>
              <div className="dsb-i">&#9678; Risk Feed</div>
              <div className="dsb-i">&#9672; Oracle</div>
              <div className="dsb-s">Analysis</div>
              <div className="dsb-i">&#8859; Reserves</div>
              <div className="dsb-i">&#9673; Peg Monitor</div>
            </div>
            <div className="dm">
              <div className="dm-h">
                <div>
                  <div className="dm-title">Risk Intelligence Dashboard</div>
                  <div className="dm-sub">LIVE - {stablecoins.length} assets - Supabase Realtime</div>
                </div>
              </div>
              <KpiRow items={stablecoins} />
              <StablecoinTable items={previewItems} />
            </div>
          </div>
        </div>
      </div>

      <div className="divider" />
      <div className="sec" id="modules">
        <div className="reveal">
          <div className="sec-lbl">Intelligence Modules</div>
          <h2 className="st">Five lenses. <span className="gs">One verdict.</span></h2>
          <p className="sec-sub">
            Every StableScore&trade; is produced by five independent analysis engines, synthesized
            by GenLayer consensus.
          </p>
        </div>
        <div className="mods">
          <div className="mod reveal"><div className="mod-icon">&#127974;</div><h3>Reserve Health</h3><p>Analyzes reserve composition, liquidity concentration, audit frequency, and transparency score. Cash vs. commercial paper exposure classified in real time.</p></div>
          <div className="mod reveal"><div className="mod-icon">&#128203;</div><h3>Issuer Intelligence</h3><p>Monitors financial statements, regulatory filings, enforcement actions, and credit quality indicators for each stablecoin issuer continuously.</p></div>
          <div className="mod reveal"><div className="mod-icon">&#9878;</div><h3>Peg Stability</h3><p>Tracks peg deviation, redemption pressure, market depth, volume anomalies, and arbitrage activity - generating early warnings before depeg events.</p></div>
          <div className="mod reveal"><div className="mod-icon">&#9878;&#65039;</div><h3>Regulatory Risk</h3><p>Evaluates jurisdiction exposure, licensing status, compliance history, active investigations, and enforcement actions across 40+ regulatory bodies.</p></div>
          <div className="mod reveal"><div className="mod-icon">&#128225;</div><h3>Sentiment Intelligence</h3><p>Reads governance forums, developer activity, news, and social signals - detecting panic conditions before they appear in price data.</p></div>
          <div className="mod reveal"><div className="mod-icon">&#9939;</div><h3>On-Chain Oracle</h3><p>Publishes StableScore&trade; ratings on-chain via GenLayer Intelligent Contracts. DeFi protocols consume scores directly for automated risk management.</p></div>
        </div>
      </div>

      <div className="divider" />
      <div className="sec" id="oracle">
        <div className="reveal">
          <div className="sec-lbl">Risk Oracle</div>
          <h2 className="st">Scores on-chain. <span className="gs">Protocols react.</span></h2>
          <p className="sec-sub">
            Riskloom publishes StableScore&trade; ratings via GenLayer Intelligent Contracts. Any
            DeFi protocol can read and act on live risk data.
          </p>
        </div>
        <div className="oracle-wrap reveal">
          <div className="oracle-grid">
            <OracleIntegrationList />
            <LiveContractPanel symbol={stablecoins[0]?.symbol ?? "USDC"} />
          </div>
        </div>
      </div>

      <div className="fcta reveal">
        <div className="fcta-i">
          <h2>Know the risk <span className="gs2">before the depeg.</span></h2>
          <p>
            Riskloom gives protocols, treasuries, and institutions the real-time stablecoin
            intelligence layer they have never had. On-chain. Continuous. Explainable.
          </p>
          <LinkButton href="/settings" variant="light" arrow>Request API Access</LinkButton>
        </div>
      </div>
    </>
  );
}
