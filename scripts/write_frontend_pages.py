"""
StableShield AI - Frontend App Router Pages Writer (STEP 6, part 6)
Writes root layout/providers, the marketing route group (landing
page rebuilt from riskloom-final.html), the dashboard route group,
auth callback, and the public API proxy routes.
Run from the repository root: python scripts/write_frontend_pages.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "apps" / "web"

FILES = {

# ------------------------------------------------------------- root --
"app/providers.tsx": """\
\"use client\";

import \"@rainbow-me/rainbowkit/styles.css\";
import { WagmiProvider } from \"wagmi\";
import { RainbowKitProvider, darkTheme } from \"@rainbow-me/rainbowkit\";
import { QueryClient, QueryClientProvider } from \"@tanstack/react-query\";
import { wagmiConfig } from \"@/lib/wagmi/config\";

const queryClient = new QueryClient();

const riskloomTheme = darkTheme({
  accentColor: \"#F59E0B\",
  accentColorForeground: \"#080B14\",
  borderRadius: \"medium\",
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider theme={riskloomTheme}>{children}</RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
""",

"app/layout.tsx": """\
import type { Metadata } from \"next\";
import { Space_Grotesk, Inter, JetBrains_Mono } from \"next/font/google\";
import \"./globals.css\";
import { Providers } from \"./providers\";

const spaceGrotesk = Space_Grotesk({
  subsets: [\"latin\"],
  weight: [\"300\", \"400\", \"500\", \"600\", \"700\"],
  variable: \"--font-sg\",
});
const inter = Inter({
  subsets: [\"latin\"],
  weight: [\"400\", \"500\", \"600\"],
  variable: \"--font-body\",
});
const jetbrainsMono = JetBrains_Mono({
  subsets: [\"latin\"],
  weight: [\"400\", \"500\"],
  variable: \"--font-mono\",
});

export const metadata: Metadata = {
  title: \"Riskloom - Stablecoin Risk Intelligence\",
  description:
    \"Riskloom continuously analyzes reserves, issuer health, peg stability, and regulatory exposure - publishing real-time StableScore ratings on-chain for every major stablecoin.\",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang=\"en\"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}
    >
      <body>
        <div className=\"loom-bg\" />
        <div className=\"orbs\">
          <div className=\"orb orb-a\" />
          <div className=\"orb orb-i\" />
          <div className=\"orb orb-m\" />
        </div>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
""",

"components/layout/RevealInit.tsx": """\
\"use client\";

import { useEffect } from \"react\";

// Ports the original riskloom-final.html IntersectionObserver behavior:
// any element with class \"reveal\" fades/slides in once it scrolls into
// view, with a slight stagger across sibling reveal elements.
export function RevealInit() {
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add(\"on\");
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 },
    );

    const elements = document.querySelectorAll(\".reveal\");
    elements.forEach((el) => {
      const parent = el.parentElement;
      if (parent) {
        const sibs = parent.querySelectorAll(\".reveal\");
        if (sibs.length > 1) {
          const idx = Array.from(sibs).indexOf(el);
          (el as HTMLElement).style.transitionDelay = `${idx * 0.09}s`;
        }
      }
      obs.observe(el);
    });

    return () => obs.disconnect();
  }, []);

  return null;
}
""",

# -------------------------------------------------------- marketing --
"app/(marketing)/layout.tsx": """\
import { Nav } from \"@/components/layout/Nav\";
import { Footer } from \"@/components/layout/Footer\";
import { RevealInit } from \"@/components/layout/RevealInit\";

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Nav />
      {children}
      <Footer />
      <RevealInit />
    </>
  );
}
""",

"app/(marketing)/page.tsx": """\
import { createClient } from \"@/lib/supabase/server\";
import { Ticker } from \"@/components/layout/Ticker\";
import { RatingBand } from \"@/components/dashboard/RatingBand\";
import { KpiRow } from \"@/components/dashboard/KpiRow\";
import { StablecoinTable } from \"@/components/dashboard/StablecoinTable\";
import { OracleIntegrationList } from \"@/components/oracle/OracleIntegrationList\";
import { LiveContractPanel } from \"@/components/oracle/LiveContractPanel\";
import { LinkButton } from \"@/components/ui/Button\";
import { LoomMark } from \"@/components/layout/LoomMark\";
import type { StablecoinWithScore } from \"@/types/risk\";
import type { StableScoreGrade } from \"@stableshield/shared-types\";

export const revalidate = 60;

async function getStablecoins(): Promise<StablecoinWithScore[]> {
  const supabase = await createClient();
  const { data } = await supabase
    .from(\"stablecoins\")
    .select(\"*, risk_scores(*)\")
    .order(\"symbol\");
  return (data ?? []) as unknown as StablecoinWithScore[];
}

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
  const stablecoins = await getStablecoins();
  const counts = countByGrade(stablecoins);
  const previewItems = stablecoins.slice(0, 4);

  return (
    <>
      <Ticker items={stablecoins} />

      <section className=\"hero\">
        <div className=\"hero-eye\">
          <span className=\"eye-dot\" />
          Powered by GenLayer Intelligent Contracts - StudioNet
        </div>
        <h1 className=\"ht\">
          <span className=\"ln\"><span className=\"w\" style={{ animationDelay: \".15s\" }}>The stablecoin</span></span>
          <span className=\"ln\"><span className=\"gw\" style={{ animationDelay: \".38s\" }}>risk intelligence</span></span>
          <span className=\"ln\"><span className=\"w\" style={{ animationDelay: \".62s\" }}>layer.</span></span>
        </h1>
        <p className=\"hero-sub\">
          Riskloom continuously analyzes reserves, issuer health, peg stability, and regulatory
          exposure - publishing real-time <span className=\"hl\">StableScore&trade;</span> ratings
          on-chain for every major stablecoin.
        </p>
        <div className=\"hero-btns\">
          <LinkButton href=\"/dashboard\" variant=\"primary\" arrow>Explore the Dashboard</LinkButton>
          <LinkButton href=\"#oracle\" variant=\"ghost\">View Risk Oracle</LinkButton>
        </div>
      </section>

      <div className=\"score-band\" id=\"ratings\">
        <RatingBand counts={counts} />
      </div>

      <div className=\"divider\" />
      <div className=\"sec\" id=\"dashboard\">
        <div className=\"reveal\">
          <div className=\"sec-lbl\">Live Platform</div>
          <h2 className=\"st\">Your risk <span className=\"gs\">command center.</span></h2>
          <p className=\"sec-sub\">
            Real-time StableScore&trade; ratings, reserve analysis, peg monitoring, and early
            warnings - all in one dashboard.
          </p>
        </div>
        <div className=\"dash reveal\">
          <div className=\"dash-bar\">
            <span className=\"d-dot dd-r\" /><span className=\"d-dot dd-y\" /><span className=\"d-dot dd-g\" />
            <span className=\"d-url\">app.riskloom.io / dashboard</span>
          </div>
          <div className=\"dash-grid\">
            <div className=\"dsb\">
              <div className=\"dsb-logo\"><LoomMark size={16} /> Riskloom</div>
              <div className=\"dsb-s\">Overview</div>
              <div className=\"dsb-i act\">&#11041; Dashboard<span className=\"dsb-badge\">live</span></div>
              <div className=\"dsb-i\">&#9678; Risk Feed</div>
              <div className=\"dsb-i\">&#9672; Oracle</div>
              <div className=\"dsb-s\">Analysis</div>
              <div className=\"dsb-i\">&#8859; Reserves</div>
              <div className=\"dsb-i\">&#9673; Peg Monitor</div>
            </div>
            <div className=\"dm\">
              <div className=\"dm-h\">
                <div>
                  <div className=\"dm-title\">Risk Intelligence Dashboard</div>
                  <div className=\"dm-sub\">LIVE - {stablecoins.length} assets - Supabase Realtime</div>
                </div>
              </div>
              <KpiRow items={stablecoins} />
              <StablecoinTable items={previewItems} />
            </div>
          </div>
        </div>
      </div>

      <div className=\"divider\" />
      <div className=\"sec\" id=\"modules\">
        <div className=\"reveal\">
          <div className=\"sec-lbl\">Intelligence Modules</div>
          <h2 className=\"st\">Five lenses. <span className=\"gs\">One verdict.</span></h2>
          <p className=\"sec-sub\">
            Every StableScore&trade; is produced by five independent analysis engines, synthesized
            by GenLayer consensus.
          </p>
        </div>
        <div className=\"mods\">
          <div className=\"mod reveal\"><div className=\"mod-icon\">&#127974;</div><h3>Reserve Health</h3><p>Analyzes reserve composition, liquidity concentration, audit frequency, and transparency score. Cash vs. commercial paper exposure classified in real time.</p></div>
          <div className=\"mod reveal\"><div className=\"mod-icon\">&#128203;</div><h3>Issuer Intelligence</h3><p>Monitors financial statements, regulatory filings, enforcement actions, and credit quality indicators for each stablecoin issuer continuously.</p></div>
          <div className=\"mod reveal\"><div className=\"mod-icon\">&#9878;</div><h3>Peg Stability</h3><p>Tracks peg deviation, redemption pressure, market depth, volume anomalies, and arbitrage activity - generating early warnings before depeg events.</p></div>
          <div className=\"mod reveal\"><div className=\"mod-icon\">&#9878;&#65039;</div><h3>Regulatory Risk</h3><p>Evaluates jurisdiction exposure, licensing status, compliance history, active investigations, and enforcement actions across 40+ regulatory bodies.</p></div>
          <div className=\"mod reveal\"><div className=\"mod-icon\">&#128225;</div><h3>Sentiment Intelligence</h3><p>Reads governance forums, developer activity, news, and social signals - detecting panic conditions before they appear in price data.</p></div>
          <div className=\"mod reveal\"><div className=\"mod-icon\">&#9939;</div><h3>On-Chain Oracle</h3><p>Publishes StableScore&trade; ratings on-chain via GenLayer Intelligent Contracts. DeFi protocols consume scores directly for automated risk management.</p></div>
        </div>
      </div>

      <div className=\"divider\" />
      <div className=\"sec\" id=\"oracle\">
        <div className=\"reveal\">
          <div className=\"sec-lbl\">Risk Oracle</div>
          <h2 className=\"st\">Scores on-chain. <span className=\"gs\">Protocols react.</span></h2>
          <p className=\"sec-sub\">
            Riskloom publishes StableScore&trade; ratings via GenLayer Intelligent Contracts. Any
            DeFi protocol can read and act on live risk data.
          </p>
        </div>
        <div className=\"oracle-wrap reveal\">
          <div className=\"oracle-grid\">
            <OracleIntegrationList />
            <LiveContractPanel symbol={stablecoins[0]?.symbol ?? \"USDC\"} />
          </div>
        </div>
      </div>

      <div className=\"fcta reveal\">
        <div className=\"fcta-i\">
          <h2>Know the risk <span className=\"gs2\">before the depeg.</span></h2>
          <p>
            Riskloom gives protocols, treasuries, and institutions the real-time stablecoin
            intelligence layer they have never had. On-chain. Continuous. Explainable.
          </p>
          <LinkButton href=\"/settings\" variant=\"light\" arrow>Request API Access</LinkButton>
        </div>
      </div>
    </>
  );
}
""",

# -------------------------------------------------------- dashboard --
"app/(dashboard)/layout.tsx": """\
import { Sidebar } from \"@/components/layout/Sidebar\";
import { WalletGuard } from \"@/components/wallet/WalletGuard\";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ paddingTop: \"62px\", position: \"relative\", zIndex: 2, minHeight: \"100vh\" }}>
      <WalletGuard>
        <div className=\"dash-grid\" style={{ minHeight: \"calc(100vh - 62px)\" }}>
          <Sidebar />
          <div className=\"dm\">{children}</div>
        </div>
      </WalletGuard>
    </div>
  );
}
""",

"app/(dashboard)/dashboard/page.tsx": """\
import { createClient } from \"@/lib/supabase/server\";
import { KpiRow } from \"@/components/dashboard/KpiRow\";
import { StablecoinTable } from \"@/components/dashboard/StablecoinTable\";
import { ActionButton } from \"@/components/ui/Button\";
import type { StablecoinWithScore } from \"@/types/risk\";

export const revalidate = 0;

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data } = await supabase
    .from(\"stablecoins\")
    .select(\"*, risk_scores(*)\")
    .order(\"symbol\");
  const items = (data ?? []) as unknown as StablecoinWithScore[];

  return (
    <>
      <div className=\"dm-h\">
        <div>
          <div className=\"dm-title\">Risk Intelligence Dashboard</div>
          <div className=\"dm-sub\">LIVE - {items.length} assets - StudioNet Oracle</div>
        </div>
        <div className=\"dm-acts\">
          <ActionButton>Export Report</ActionButton>
          <ActionButton variant=\"primary\">&#9889; Live Alerts</ActionButton>
        </div>
      </div>
      <KpiRow items={items} />
      <StablecoinTable items={items} />
    </>
  );
}
""",

"app/(dashboard)/stablecoins/page.tsx": """\
import { createClient } from \"@/lib/supabase/server\";
import { StablecoinTable } from \"@/components/dashboard/StablecoinTable\";
import type { StablecoinWithScore } from \"@/types/risk\";

export const revalidate = 0;

export default async function StablecoinsPage() {
  const supabase = await createClient();
  const { data } = await supabase
    .from(\"stablecoins\")
    .select(\"*, risk_scores(*)\")
    .order(\"symbol\");
  const items = (data ?? []) as unknown as StablecoinWithScore[];

  return (
    <>
      <div className=\"dm-h\">
        <div>
          <div className=\"dm-title\">All Stablecoins</div>
          <div className=\"dm-sub\">{items.length} assets tracked</div>
        </div>
      </div>
      <StablecoinTable items={items} />
    </>
  );
}
""",

"app/(dashboard)/stablecoins/[symbol]/page.tsx": """\
import { createClient } from \"@/lib/supabase/server\";
import { notFound } from \"next/navigation\";
import { RatingPill } from \"@/components/ui/RatingPill\";
import { LiveContractPanel } from \"@/components/oracle/LiveContractPanel\";
import { formatPegPrice, formatMarketCap } from \"@/lib/format\";

export const revalidate = 0;

export default async function StablecoinDetailPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = await params;
  const supabase = await createClient();

  const { data: coin } = await supabase
    .from(\"stablecoins\")
    .select(\"*, risk_scores(*)\")
    .eq(\"symbol\", symbol.toUpperCase())
    .maybeSingle();

  if (!coin) notFound();

  const { data: history } = await supabase
    .from(\"risk_score_history\")
    .select(\"*\")
    .eq(\"stablecoin_id\", coin.id)
    .order(\"recorded_at\", { ascending: false })
    .limit(10);

  const score = coin.risk_scores;

  return (
    <>
      <div className=\"dm-h\">
        <div>
          <div className=\"dm-title\">{coin.name} ({coin.symbol})</div>
          <div className=\"dm-sub\">{coin.chain} - peg {formatPegPrice(coin.peg_price)} - cap {formatMarketCap(coin.market_cap_usd)}</div>
        </div>
        {score && <RatingPill grade={score.rating} />}
      </div>

      {score && (
        <div className=\"krow\">
          <div className=\"kpi k1\"><div className=\"knum\">{score.reserve_subscore ?? \"-\"}</div><div className=\"klbl\">Reserve Health</div></div>
          <div className=\"kpi k2\"><div className=\"knum\">{score.issuer_subscore ?? \"-\"}</div><div className=\"klbl\">Issuer Intelligence</div></div>
          <div className=\"kpi k3\"><div className=\"knum\">{score.peg_subscore ?? \"-\"}</div><div className=\"klbl\">Peg Stability</div></div>
          <div className=\"kpi k4\"><div className=\"knum\">{score.regulatory_subscore ?? \"-\"}</div><div className=\"klbl\">Regulatory Risk</div></div>
        </div>
      )}

      <div className=\"oracle-lbl\" style={{ marginTop: \"2rem\" }}>Score History</div>
      {(history ?? []).map((h) => (
        <div className=\"tbl-row\" key={h.id} style={{ gridTemplateColumns: \"1fr 1fr 2fr\", cursor: \"default\" }}>
          <div><RatingPill grade={h.rating} /></div>
          <div className=\"tc-cap\">{h.score_numeric}</div>
          <div className=\"tc-sym\">{new Date(h.recorded_at).toLocaleString()} {h.reason_summary ? `- ${h.reason_summary}` : \"\"}</div>
        </div>
      ))}

      <div className=\"oracle-wrap\" style={{ marginTop: \"2rem\" }}>
        <div className=\"oracle-grid\" style={{ gridTemplateColumns: \"1fr\" }}>
          <LiveContractPanel symbol={coin.symbol} />
        </div>
      </div>
    </>
  );
}
""",

"app/(dashboard)/oracle/page.tsx": """\
import { OracleIntegrationList } from \"@/components/oracle/OracleIntegrationList\";
import { LiveContractPanel } from \"@/components/oracle/LiveContractPanel\";

export default function OraclePage() {
  return (
    <>
      <div className=\"dm-h\">
        <div>
          <div className=\"dm-title\">Risk Oracle</div>
          <div className=\"dm-sub\">GenLayer StudioNet - StableScoreOracle</div>
        </div>
      </div>
      <div className=\"oracle-wrap\">
        <div className=\"oracle-grid\">
          <OracleIntegrationList />
          <LiveContractPanel />
        </div>
      </div>
    </>
  );
}
""",

"app/(dashboard)/alerts/page.tsx": """\
import { createClient } from \"@/lib/supabase/server\";

export const revalidate = 0;

export default async function AlertsPage() {
  const supabase = await createClient();
  const { data } = await supabase
    .from(\"alerts\")
    .select(\"*, stablecoins(symbol, name)\")
    .order(\"triggered_at\", { ascending: false })
    .limit(50);

  const alerts = data ?? [];

  return (
    <>
      <div className=\"dm-h\">
        <div>
          <div className=\"dm-title\">Risk Feed</div>
          <div className=\"dm-sub\">{alerts.length} recent alerts</div>
        </div>
      </div>
      {alerts.length === 0 && (
        <p style={{ color: \"var(--text2)\" }}>No alerts recorded yet.</p>
      )}
      {alerts.map((alert) => (
        <div
          className=\"tbl-row\"
          key={alert.id}
          style={{ gridTemplateColumns: \"1fr 3fr 1fr\", cursor: \"default\" }}
        >
          <div className={alert.severity === \"critical\" ? \"hi-r risk-ind\" : alert.severity === \"warning\" ? \"mid-r risk-ind\" : \"low-r risk-ind\"}>
            <span className=\"ri-dot\" />
            <span className=\"ri-lbl\">{alert.severity}</span>
          </div>
          <div className=\"tc-name\">{alert.message}</div>
          <div className=\"tc-sym\">{new Date(alert.triggered_at).toLocaleString()}</div>
        </div>
      ))}
    </>
  );
}
""",

"app/(dashboard)/reports/page.tsx": """\
import { ActionButton } from \"@/components/ui/Button\";

export default function ReportsPage() {
  return (
    <>
      <div className=\"dm-h\">
        <div>
          <div className=\"dm-title\">Compliance Reports</div>
          <div className=\"dm-sub\">Institution-grade StableScore&trade; exports</div>
        </div>
        <div className=\"dm-acts\">
          <ActionButton variant=\"primary\">Generate Report</ActionButton>
        </div>
      </div>
      <p style={{ color: \"var(--text2)\", maxWidth: \"540px\" }}>
        Scheduled PDF/CSV compliance exports (reserve composition, issuer
        filings, peg history, regulatory events) are generated from the same
        data backing the dashboard. Report generation wiring lands once the
        api-v1-history endpoint has production traffic to validate against.
      </p>
    </>
  );
}
""",

"app/(dashboard)/settings/page.tsx": """\
import { createClient } from \"@/lib/supabase/server\";

export const revalidate = 0;

export default async function SettingsPage() {
  const supabase = await createClient();
  const { data: userData } = await supabase.auth.getUser();
  const user = userData?.user;

  let profile = null;
  if (user) {
    const { data } = await supabase
      .from(\"profiles\")
      .select(\"*, wallets(address)\")
      .eq(\"id\", user.id)
      .maybeSingle();
    profile = data;
  }

  return (
    <>
      <div className=\"dm-h\">
        <div>
          <div className=\"dm-title\">Settings</div>
          <div className=\"dm-sub\">Account &amp; API access</div>
        </div>
      </div>
      <div className=\"kpi k1\" style={{ maxWidth: \"480px\" }}>
        <div className=\"klbl\">Connected Wallet</div>
        <div className=\"knum\" style={{ fontSize: \"1rem\", fontFamily: \"var(--mono)\" }}>
          {profile?.wallets?.address ?? \"Not linked yet\"}
        </div>
        <div className=\"ktrend\">Tier: {profile?.tier ?? \"free\"}</div>
      </div>
      <p style={{ color: \"var(--text2)\", marginTop: \"1.5rem\", maxWidth: \"540px\" }}>
        API key issuance for the Risk Intelligence API (exchanges, fintechs,
        institutions) is managed server-side via the api_keys table. Self-serve
        key generation UI ships alongside the billing/business-model work.
      </p>
    </>
  );
}
""",

# -------------------------------------------------------------- auth --
"app/auth/callback/route.ts": """\
import { NextResponse } from \"next/server\";
import { createClient } from \"@/lib/supabase/server\";
import type { EmailOtpType } from \"@supabase/supabase-js\";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const tokenHash = url.searchParams.get(\"token_hash\");
  const type = url.searchParams.get(\"type\") as EmailOtpType | null;

  if (tokenHash && type) {
    const supabase = await createClient();
    const { error } = await supabase.auth.verifyOtp({ token_hash: tokenHash, type });
    if (!error) {
      return NextResponse.redirect(new URL(\"/dashboard\", url.origin));
    }
  }

  return NextResponse.redirect(new URL(\"/?auth_error=1\", url.origin));
}
""",

# ----------------------------------------------------------- api v1 --
"app/api/v1/scores/route.ts": """\
// Thin proxy to the api-v1-scores Supabase Edge Function, so external
// consumers can hit a stable first-party domain instead of the
// Supabase functions URL directly.
export async function GET(request: Request) {
  const url = new URL(request.url);
  const target = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1/api-v1-scores${url.search}`;

  const res = await fetch(target, {
    headers: { \"x-api-key\": request.headers.get(\"x-api-key\") ?? \"\" },
  });
  const body = await res.text();

  return new Response(body, {
    status: res.status,
    headers: { \"Content-Type\": \"application/json\" },
  });
}
""",

"app/api/v1/history/route.ts": """\
// Thin proxy to the api-v1-history Supabase Edge Function.
export async function GET(request: Request) {
  const url = new URL(request.url);
  const target = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1/api-v1-history${url.search}`;

  const res = await fetch(target, {
    headers: { \"x-api-key\": request.headers.get(\"x-api-key\") ?? \"\" },
  });
  const body = await res.text();

  return new Response(body, {
    status: res.status,
    headers: { \"Content-Type\": \"application/json\" },
  });
}
""",
}


def main() -> None:
    created = []
    for rel, content in FILES.items():
        path = WEB / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(rel)

    print(f"Web root: {WEB}")
    print(f"Created {len(created)} file(s).")
    for f in created:
        print(f"  + {f}")
    if not created:
        print("Nothing to do - all files already exist.")


if __name__ == "__main__":
    main()
