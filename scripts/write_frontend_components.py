"""
StableShield AI - Frontend Components + Hooks Writer (STEP 6, part 4)
Run from the repository root: python scripts/write_frontend_components.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "apps" / "web"

FILES = {

# ---------------------------------------------------------------- ui --
"components/ui/RatingPill.tsx": """\
import type { StableScoreGrade } from "@stableshield/shared-types";

const GRADE_CLASS: Record<StableScoreGrade, string> = {
  AAA: "s-aaa",
  AA: "s-aa",
  A: "s-a",
  BBB: "s-bbb",
  BB: "s-bb",
  B: "s-b",
  CCC: "s-ccc",
  D: "s-d",
};

export function RatingPill({ grade }: { grade: StableScoreGrade }) {
  return <span className={`rat-pill ${GRADE_CLASS[grade]}`}>{grade}</span>;
}

export function riskLevelForGrade(
  grade: StableScoreGrade,
): "low" | "medium" | "critical" {
  if (["AAA", "AA", "A"].includes(grade)) return "low";
  if (["BBB", "BB"].includes(grade)) return "medium";
  return "critical";
}

export function ratingBarFillClass(grade: StableScoreGrade): string {
  const level = riskLevelForGrade(grade);
  if (level === "low") return "rb-safe";
  if (level === "medium") return "rb-warn";
  return "rb-danger";
}
""",

"components/ui/Button.tsx": """\
import Link from "next/link";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost" | "light";

const VARIANT_CLASS: Record<Variant, string> = {
  primary: "btn btn-p",
  ghost: "btn btn-g",
  light: "btn-lt",
};

interface LinkButtonProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  variant?: Variant;
  arrow?: boolean;
}

export function LinkButton({
  href,
  variant = "primary",
  arrow = false,
  children,
  className,
  ...rest
}: LinkButtonProps) {
  return (
    <Link href={href} className={`${VARIANT_CLASS[variant]} ${className ?? ""}`} {...rest}>
      {children}
      {arrow && <span className="arr">&rarr;</span>}
    </Link>
  );
}

interface ActionButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function ActionButton({
  variant = "secondary",
  className,
  children,
  ...rest
}: ActionButtonProps) {
  const variantClass = variant === "primary" ? "dm-b dm-bp" : "dm-b dm-bs";
  return (
    <button className={`${variantClass} ${className ?? ""}`} {...rest}>
      {children}
    </button>
  );
}
""",

# ------------------------------------------------------------ layout --
"components/layout/LoomMark.tsx": """\
export function LoomMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#6366F1" />
        </linearGradient>
      </defs>
      <path d="M14 2 L22 9 L14 16 L6 9 Z" fill="none" stroke="url(#lg1)" strokeWidth="1.5" />
      <path d="M14 12 L22 19 L14 26 L6 19 Z" fill="none" stroke="url(#lg1)" strokeWidth="1.5" opacity={0.7} />
      <line x1="14" y1="2" x2="14" y2="26" stroke="url(#lg1)" strokeWidth="1" opacity={0.4} />
      <circle cx="14" cy="9" r="2.5" fill="url(#lg1)" />
      <circle cx="14" cy="19" r="2" fill="url(#lg1)" opacity={0.7} />
      <circle cx="6" cy="9" r="1.2" fill="#F59E0B" opacity={0.6} />
      <circle cx="22" cy="9" r="1.2" fill="#6366F1" opacity={0.6} />
    </svg>
  );
}
""",

"components/layout/Nav.tsx": """\
import Link from "next/link";
import { LoomMark } from "./LoomMark";
import { WalletConnectButton } from "../wallet/WalletConnectButton";

export function Nav() {
  return (
    <nav>
      <Link href="/" className="logo">
        <div className="logo-mark">
          <LoomMark />
        </div>
        Riskloom
      </Link>
      <ul className="nav-links">
        <li><Link href="/#ratings">StableScore&trade;</Link></li>
        <li><Link href="/dashboard">Dashboard</Link></li>
        <li><Link href="/#oracle">Oracle</Link></li>
        <li><Link href="/#modules">Intelligence</Link></li>
      </ul>
      <div className="nav-r">
        <Link href="/docs" className="nav-ghost">Docs</Link>
        <div className="wallet-slot">
          <WalletConnectButton />
        </div>
      </div>
    </nav>
  );
}
""",

"components/layout/Footer.tsx": """\
export function Footer() {
  return (
    <footer>
      <p>Riskloom - Stablecoin Risk Intelligence Network - StableScore&trade; - Powered by GenLayer Intelligent Contracts</p>
    </footer>
  );
}
""",

"components/layout/Ticker.tsx": """\
import type { StablecoinWithScore } from "@/types/risk";
import { formatPegPrice, pegPriceClass } from "@/lib/format";

export function Ticker({ items }: { items: StablecoinWithScore[] }) {
  const doubled = [...items, ...items];
  return (
    <div className="ticker">
      <div className="ticker-label">&#11049; Live</div>
      <div className="ticker-track">
        {doubled.map((coin, i) => (
          <div className="ticker-item" key={`${coin.symbol}-${i}`}>
            <span className="ti-name">{coin.symbol}</span>
            <span className={`ti-score s-${(coin.risk_scores?.rating ?? "d").toLowerCase()}`}>
              {coin.risk_scores?.rating ?? "-"}
            </span>
            <span className={`ti-price ${pegPriceClass(coin.peg_price)}`}>
              {formatPegPrice(coin.peg_price)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
""",

"components/layout/Sidebar.tsx": """\
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LoomMark } from "./LoomMark";

const NAV_SECTIONS: { label: string; items: { href: string; label: string; icon: string }[] }[] = [
  {
    label: "Overview",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: "\\u2b21" },
      { href: "/alerts", label: "Risk Feed", icon: "\\u25ce" },
      { href: "/oracle", label: "Oracle", icon: "\\u25c8" },
    ],
  },
  {
    label: "Analysis",
    items: [
      { href: "/stablecoins", label: "Stablecoins", icon: "\\u229b" },
    ],
  },
  {
    label: "Reports",
    items: [
      { href: "/reports", label: "Audit Trail", icon: "\\u2261" },
      { href: "/settings", label: "Settings", icon: "\\u2699" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="dsb">
      <div className="dsb-logo">
        <LoomMark size={16} />
        Riskloom
      </div>
      {NAV_SECTIONS.map((section) => (
        <div key={section.label}>
          <div className="dsb-s">{section.label}</div>
          {section.items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`dsb-i ${pathname === item.href ? "act" : ""}`}
            >
              {item.icon} {item.label}
            </Link>
          ))}
        </div>
      ))}
    </div>
  );
}
""",

# --------------------------------------------------------- dashboard --
"components/dashboard/RatingBand.tsx": """\
import type { StableScoreGrade } from "@stableshield/shared-types";

const GRADES: { grade: StableScoreGrade; label: string; slot: string; cls: string }[] = [
  { grade: "AAA", label: "Extremely Safe", slot: "rs-aaa", cls: "c-aaa" },
  { grade: "AA", label: "Very Safe", slot: "rs-aa", cls: "c-aa" },
  { grade: "A", label: "Safe", slot: "rs-a", cls: "c-a" },
  { grade: "BBB", label: "Moderate", slot: "rs-bbb", cls: "c-bbb" },
  { grade: "BB", label: "Elevated", slot: "rs-bb", cls: "c-bb" },
  { grade: "B", label: "High Risk", slot: "rs-b", cls: "c-b" },
  { grade: "CCC", label: "Severe", slot: "rs-ccc", cls: "c-ccc" },
  { grade: "D", label: "Critical", slot: "rs-d", cls: "c-d" },
];

export function RatingBand({ counts }: { counts: Record<StableScoreGrade, number> }) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="sb-inner reveal">
      <div className="sb-top">
        <div>
          <div className="sb-title">StableScore&trade; Rating System</div>
          <div className="sb-sub">Continuous AI-powered risk ratings - updated every 60 seconds</div>
        </div>
        <div className="sb-live">
          <span className="sb-live-dot" />
          {total} stablecoins tracked
        </div>
      </div>
      <div className="ratings-row">
        {GRADES.map((g) => (
          <div className={`rating-slot ${g.slot}`} key={g.grade}>
            <span className={`rs-grade ${g.cls}`}>{g.grade}</span>
            <span className={`rs-label ${g.cls}`} style={{ opacity: 0.7 }}>{g.label}</span>
            <span className={`rs-count ${g.cls}`}>{counts[g.grade] ?? 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
""",

"components/dashboard/KpiRow.tsx": """\
import type { StablecoinWithScore } from "@/types/risk";
import { riskLevelForGrade } from "../ui/RatingPill";

export function KpiRow({ items }: { items: StablecoinWithScore[] }) {
  const tracked = items.length;
  const safe = items.filter(
    (i) => i.risk_scores && riskLevelForGrade(i.risk_scores.rating) === "low",
  ).length;
  const watchlist = items.filter(
    (i) => i.risk_scores && riskLevelForGrade(i.risk_scores.rating) === "medium",
  ).length;
  const critical = items.filter(
    (i) => i.risk_scores && riskLevelForGrade(i.risk_scores.rating) === "critical",
  ).length;

  const safePct = tracked > 0 ? ((safe / tracked) * 100).toFixed(1) : "0.0";

  return (
    <div className="krow">
      <div className="kpi k1">
        <div className="knum">{tracked}</div>
        <div className="klbl">Assets Tracked</div>
        <div className="ktrend kt-s">Live from Supabase</div>
      </div>
      <div className="kpi k2">
        <div className="knum">{safe}</div>
        <div className="klbl">AAA-A Rated</div>
        <div className="ktrend kt-s">{safePct}% safe</div>
      </div>
      <div className="kpi k3">
        <div className="knum">{watchlist}</div>
        <div className="klbl">&#9888; Watchlist</div>
        <div className="ktrend" style={{ color: "var(--warn)" }}>BB-B Rating</div>
      </div>
      <div className="kpi k4">
        <div className="knum">{critical}</div>
        <div className="klbl">&#x1f6a8; Critical</div>
        <div className="ktrend kt-d">CCC or D Rating</div>
      </div>
    </div>
  );
}
""",

"components/dashboard/StablecoinTable.tsx": """\
import Link from "next/link";
import type { StablecoinWithScore } from "@/types/risk";
import { RatingPill, ratingBarFillClass, riskLevelForGrade } from "../ui/RatingPill";
import { formatPegPrice, formatMarketCap, pegPriceClass } from "@/lib/format";

const SCORE_TO_BAR_PCT: Record<string, number> = {
  AAA: 96, AA: 84, A: 75, BBB: 55, BB: 42, B: 30, CCC: 18, D: 5,
};

export function StablecoinTable({ items }: { items: StablecoinWithScore[] }) {
  return (
    <div>
      <div className="tbl-head">
        <div className="th">Stablecoin</div>
        <div className="th">StableScore&trade;</div>
        <div className="th">Peg Price</div>
        <div className="th">Market Cap</div>
        <div className="th">24h Change</div>
        <div className="th">Risk Level</div>
      </div>
      {items.map((coin) => {
        const rating = coin.risk_scores?.rating ?? "D";
        const level = riskLevelForGrade(rating);
        return (
          <Link href={`/stablecoins/${coin.symbol}`} className="tbl-row" key={coin.id}>
            <div>
              <div className="tc-name">{coin.name}</div>
              <div className="tc-sym">{coin.symbol}</div>
            </div>
            <div className="tc-rating">
              <div>
                <RatingPill grade={rating} />
                <div className="rat-bar">
                  <div
                    className={`rb-fill ${ratingBarFillClass(rating)}`}
                    style={{ width: `${SCORE_TO_BAR_PCT[rating] ?? 50}%` }}
                  />
                </div>
              </div>
            </div>
            <div className={`tc-peg ${pegPriceClass(coin.peg_price)}`}>
              {formatPegPrice(coin.peg_price)}
            </div>
            <div className="tc-cap">{formatMarketCap(coin.market_cap_usd)}</div>
            <div className="tc-chg" style={{ color: "var(--text2)" }}>--</div>
            <div className={`risk-ind ${level === "low" ? "low-r" : level === "medium" ? "mid-r" : "hi-r"}`}>
              <span className="ri-dot" />
              <span className="ri-lbl">{level === "low" ? "Low" : level === "medium" ? "Medium" : "Critical"}</span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
""",

# ------------------------------------------------------------ oracle --
"components/oracle/OracleIntegrationList.tsx": """\
const INTEGRATIONS = [
  {
    icon: "\\ud83c\\udfe6",
    iconClass: "oi-v",
    name: "Lending Protocols",
    desc: "Auto-reduce borrow limits when rating drops below BBB",
    status: "Live",
  },
  {
    icon: "\\ud83c\\udfdb",
    iconClass: "oi-a",
    name: "Treasury Systems",
    desc: "Rebalance reserves when any holding drops below A",
    status: "Live",
  },
  {
    icon: "\\ud83d\\udcb3",
    iconClass: "oi-s",
    name: "Payment Networks",
    desc: "Accept only stablecoins rated BBB or above",
    status: "Ready",
  },
  {
    icon: "\\u26a1",
    iconClass: "oi-v",
    name: "Liquidation Engines",
    desc: "Trigger early liquidation on CCC-rated collateral",
    status: "Ready",
  },
];

export function OracleIntegrationList() {
  return (
    <div className="oracle-left">
      <div className="oracle-lbl">Oracle Integrations</div>
      {INTEGRATIONS.map((item) => (
        <div className="oracle-item" key={item.name}>
          <div className={`oi-icon ${item.iconClass}`}>{item.icon}</div>
          <div>
            <div className="oi-name">{item.name}</div>
            <div className="oi-desc">{item.desc}</div>
          </div>
          <div className={`oi-status ${item.status === "Live" ? "ois-live" : "ois-ready"}`}>
            {item.status}
          </div>
        </div>
      ))}
    </div>
  );
}
""",

"components/oracle/LiveContractPanel.tsx": """\
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
          {`# Live read from StableScoreOracle\\nget_score("${result.symbol}") -> {\\n  rating: "${result.rating}",\\n  score: ${result.score},\\n  peg: ${result.peg},\\n  reserve_ratio: ${result.reserve_ratio},\\n  updated_at: "${result.updated_at}"\\n}`}
        </div>
      ) : (
        <div className="code-block" dangerouslySetInnerHTML={{ __html: FALLBACK_SNIPPET }} />
      )}
    </div>
  );
}
""",

# ------------------------------------------------------------ wallet --
"components/wallet/WalletConnectButton.tsx": """\
"use client";

import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useWalletAuth } from "@/hooks/useWalletAuth";

export function WalletConnectButton() {
  useWalletAuth();
  return (
    <ConnectButton
      label="Connect Wallet"
      chainStatus="icon"
      accountStatus="address"
      showBalance={false}
    />
  );
}
""",

"components/wallet/WalletGuard.tsx": """\
"use client";

import { useAccount } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";

export function WalletGuard({ children }: { children: React.ReactNode }) {
  const { isConnected } = useAccount();

  if (!isConnected) {
    return (
      <div style={{ padding: "4rem 2rem", textAlign: "center" }}>
        <p style={{ color: "var(--text2)", marginBottom: "1.5rem" }}>
          Connect a wallet to access the risk intelligence dashboard.
        </p>
        <ConnectButton />
      </div>
    );
  }

  return <>{children}</>;
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
