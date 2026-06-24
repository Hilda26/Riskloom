"""
StableShield AI - Frontend Styles Writer (STEP 6, part 2)
Ports the design system from riskloom-final.html into
styles/tokens.css (design tokens) and app/globals.css (component
styles), unchanged in visual intent, so the React components can
reuse the original class names directly.
Run from the repository root: python scripts/write_frontend_styles.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "apps" / "web"

TOKENS_CSS = """\
:root {
  --bg:       #080B14;
  --bg2:      #0C0F1A;
  --surface:  #0F1221;
  --surface2: #161928;
  --surface3: #1D2035;
  --amber:    #F59E0B;
  --amber2:   #FBBF24;
  --amber3:   #FDE68A;
  --indigo:   #6366F1;
  --indigo2:  #818CF8;
  --indigo3:  #A5B4FC;
  --safe:     #10B981;
  --safe2:    #34D399;
  --warn:     #F97316;
  --danger:   #EF4444;
  --text:     #F8FAFC;
  --text2:    #94A3B8;
  --text3:    #475569;
  --ag: rgba(245,158,11,0.15);
  --ig: rgba(99,102,241,0.15);
  --ab: rgba(245,158,11,0.25);
  --ib: rgba(99,102,241,0.22);

  --sg: 'Space Grotesk', system-ui, sans-serif;
  --body: 'Inter', system-ui, sans-serif;
  --mono: 'JetBrains Mono', monospace;
}
"""

GLOBALS_CSS = """\
@import "../styles/tokens.css";

*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{font-family:var(--body);background:var(--bg);color:var(--text);overflow-x:hidden;-webkit-font-smoothing:antialiased;}

/* loom background */
.loom-bg {
  position: fixed; inset:0; z-index:0; pointer-events:none;
  background-image:
    repeating-linear-gradient(-45deg, rgba(99,102,241,0.028) 0px, rgba(99,102,241,0.028) 1px, transparent 1px, transparent 28px),
    repeating-linear-gradient(45deg, rgba(245,158,11,0.022) 0px, rgba(245,158,11,0.022) 1px, transparent 1px, transparent 28px);
}

/* ambient orbs */
.orbs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;}
.orb{position:absolute;border-radius:50%;filter:blur(110px);}
.orb-a{width:640px;height:640px;background:radial-gradient(circle,rgba(245,158,11,0.38) 0%,transparent 70%);top:-180px;right:-100px;animation:oa 28s ease-in-out infinite alternate;}
.orb-i{width:580px;height:580px;background:radial-gradient(circle,rgba(99,102,241,0.32) 0%,transparent 70%);bottom:-150px;left:-100px;animation:oi 34s ease-in-out infinite alternate;}
.orb-m{width:360px;height:360px;background:radial-gradient(circle,rgba(245,158,11,0.15) 0%,transparent 70%);top:42%;left:52%;animation:om 20s ease-in-out infinite alternate;}
@keyframes oa{0%{transform:translate(0,0) scale(1);}50%{transform:translate(-80px,70px) scale(1.1);}100%{transform:translate(-40px,120px) scale(0.93);}}
@keyframes oi{0%{transform:translate(0,0);}50%{transform:translate(90px,-70px) scale(1.12);}100%{transform:translate(50px,-110px) scale(0.91);}}
@keyframes om{0%{transform:translate(0,0) scale(1);}100%{transform:translate(-90px,80px) scale(1.22);}}

/* nav */
nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:1.125rem 2.75rem;background:rgba(8,11,20,0.85);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border-bottom:1px solid rgba(245,158,11,0.1);}
nav::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(245,158,11,0.5),rgba(99,102,241,0.4),transparent);}
.logo{display:flex;align-items:center;gap:0.75rem;font-family:var(--sg);font-size:1.25rem;font-weight:700;color:var(--text);text-decoration:none;letter-spacing:-0.01em;}
.logo-mark{width:30px;height:30px;position:relative;display:grid;place-items:center;flex-shrink:0;}
.logo-mark svg{overflow:visible;}
.nav-links{display:flex;gap:2rem;list-style:none;}
.nav-links a{font-family:var(--body);font-size:0.875rem;font-weight:500;color:var(--text2);text-decoration:none;transition:color 180ms;}
.nav-links a:hover{color:var(--text);}
.nav-r{display:flex;gap:0.75rem;align-items:center;}
.nav-ghost{font-size:0.875rem;font-weight:500;color:var(--text2);text-decoration:none;padding:0.5rem 1rem;transition:color 180ms;}
.nav-ghost:hover{color:var(--text);}
.nav-cta{font-family:var(--sg);font-size:0.875rem;font-weight:600;padding:0.5625rem 1.375rem;border-radius:6px;text-decoration:none;background:linear-gradient(135deg,var(--amber) 0%,var(--warn) 60%,var(--amber2) 100%);background-size:200% auto;color:#080B14;box-shadow:0 0 22px rgba(245,158,11,0.38);transition:background-position .5s,transform 200ms,box-shadow 220ms;border:none;cursor:pointer;}
.nav-cta:hover{background-position:right center;transform:translateY(-1px);box-shadow:0 0 34px rgba(245,158,11,0.55);}

/* ticker */
.ticker{position:relative;z-index:2;background:rgba(15,18,33,0.9);border-bottom:1px solid rgba(245,158,11,0.1);padding:0.6rem 0;overflow:hidden;display:flex;align-items:center;margin-top:62px;}
.ticker-label{font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--amber);padding:0 1.5rem;flex-shrink:0;border-right:1px solid rgba(245,158,11,0.2);margin-right:1rem;}
.ticker-track{display:flex;gap:0;white-space:nowrap;animation:tick 22s linear infinite;}
.ticker-item{display:inline-flex;align-items:center;gap:0.5rem;padding:0 1.75rem;border-right:1px solid rgba(148,163,184,0.08);}
.ti-name{font-family:var(--mono);font-size:0.7rem;color:var(--text2);}
.ti-score{font-family:var(--sg);font-size:0.7rem;font-weight:700;padding:0.1rem 0.4rem;border-radius:3px;}
.ti-price{font-family:var(--mono);font-size:0.68rem;}
.s-aaa{color:#10B981;background:rgba(16,185,129,0.12);}
.s-aa{color:#34D399;background:rgba(52,211,153,0.1);}
.s-a{color:#6EE7B7;background:rgba(110,231,183,0.1);}
.s-bbb{color:#FBBF24;background:rgba(251,191,36,0.12);}
.s-bb{color:#F59E0B;background:rgba(245,158,11,0.12);}
.s-b{color:#F97316;background:rgba(249,115,22,0.12);}
.s-ccc{color:#EF4444;background:rgba(239,68,68,0.12);}
.s-d{color:#991B1B;background:rgba(153,27,27,0.18);}
.safe{color:var(--safe2);}.warn-c{color:var(--warn);}.danger-c{color:var(--danger);}
@keyframes tick{0%{transform:translateX(0);}100%{transform:translateX(-50%);}}

/* hero */
.hero{position:relative;z-index:2;min-height:calc(100vh - 62px);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:5rem 2rem 4rem;}
.hero-eye{font-family:var(--mono);font-size:0.72rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--amber2);padding:0.4375rem 1.125rem;border:1px solid rgba(245,158,11,0.25);border-radius:4px;background:rgba(245,158,11,0.07);margin-bottom:2.5rem;display:inline-flex;align-items:center;gap:0.625rem;opacity:0;animation:up .7s .15s ease forwards;}
.eye-dot{width:6px;height:6px;border-radius:50%;background:var(--amber);box-shadow:0 0 10px var(--amber);animation:edot 2.2s ease-in-out infinite;}
@keyframes edot{0%,100%{opacity:1;box-shadow:0 0 10px var(--amber);}50%{opacity:.3;box-shadow:0 0 3px var(--amber2);}}
h1.ht{font-family:var(--sg);font-size:clamp(3rem,10vw,7.5rem);font-weight:700;letter-spacing:-0.04em;line-height:.95;margin-bottom:1.5rem;max-width:880px;position:relative;z-index:1;}
h1.ht .ln{display:block;overflow:hidden;}
h1.ht .w{display:inline-block;color:var(--text);opacity:0;transform:translateY(56px);animation:up 1.1s cubic-bezier(0.16,1,0.3,1) forwards;}
h1.ht .gw{display:inline-block;opacity:0;transform:translateY(56px);background:linear-gradient(110deg,var(--text) 0%,var(--amber2) 28%,var(--amber) 50%,var(--indigo2) 72%,var(--text) 100%);background-size:270% auto;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:up 1.1s cubic-bezier(0.16,1,0.3,1) forwards,shimmer 6s 1.3s linear infinite;}
@keyframes shimmer{to{background-position:270% center;}}
@keyframes up{to{opacity:1;transform:translateY(0);}}
.hero-sub{font-family:var(--body);font-size:1.125rem;line-height:1.65;color:var(--text2);max-width:580px;margin-bottom:2.75rem;position:relative;z-index:1;opacity:0;animation:up .7s .8s ease forwards;}
.hl{color:var(--amber2);}
.hero-btns{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;position:relative;z-index:1;opacity:0;animation:up .7s 1s ease forwards;}
.btn{font-family:var(--sg);font-size:0.9375rem;font-weight:600;padding:.875rem 1.875rem;border-radius:7px;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;transition:all 240ms ease;position:relative;overflow:hidden;cursor:pointer;border:none;}
.btn-p{background:linear-gradient(135deg,var(--amber) 0%,var(--warn) 55%,var(--amber2) 100%);background-size:200% auto;color:#080B14;box-shadow:0 3px 24px rgba(245,158,11,.45);}
.btn-p:hover{background-position:right center;transform:translateY(-2px);box-shadow:0 8px 38px rgba(245,158,11,.65);}
.btn-g{background:transparent;color:var(--text);border:1px solid rgba(248,250,252,0.14);}
.btn-g:hover{border-color:rgba(245,158,11,0.45);background:rgba(245,158,11,0.07);transform:translateY(-2px);}
.arr{transition:transform .25s;}.btn:hover .arr{transform:translateX(5px);}

/* stablescore band */
.score-band{position:relative;z-index:2;max-width:1160px;margin:0 auto;padding:3.5rem 2rem;}
.sb-inner{background:rgba(15,18,33,0.85);border:1px solid rgba(245,158,11,0.14);border-radius:14px;padding:2.5rem 2.5rem 2rem;position:relative;overflow:hidden;}
.sb-inner::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#10B981,#34D399,#FBBF24,#F59E0B,#F97316,#EF4444,#991B1B);border-radius:14px 14px 0 0;}
.sb-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:2rem;}
.sb-title{font-family:var(--sg);font-size:1.125rem;font-weight:700;color:var(--text);}
.sb-sub{font-family:var(--mono);font-size:0.65rem;letter-spacing:.14em;text-transform:uppercase;color:var(--text3);margin-top:.25rem;}
.sb-live{display:flex;align-items:center;gap:.5rem;font-family:var(--mono);font-size:0.65rem;color:var(--safe2);letter-spacing:.12em;text-transform:uppercase;}
.sb-live-dot{width:6px;height:6px;border-radius:50%;background:var(--safe2);box-shadow:0 0 8px var(--safe2);animation:edot 2s ease-in-out infinite;}
.ratings-row{display:grid;grid-template-columns:repeat(8,1fr);gap:.75rem;}
.rating-slot{text-align:center;padding:.875rem .5rem;border-radius:8px;cursor:pointer;transition:all 200ms;}
.rs-aaa{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.22);}
.rs-aa {background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.18);}
.rs-a  {background:rgba(110,231,183,0.06);border:1px solid rgba(110,231,183,0.14);}
.rs-bbb{background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.22);}
.rs-bb {background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.22);}
.rs-b  {background:rgba(249,115,22,0.1);border:1px solid rgba(249,115,22,0.22);}
.rs-ccc{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.22);}
.rs-d  {background:rgba(153,27,27,0.14);border:1px solid rgba(153,27,27,0.28);}
.rating-slot:hover{transform:translateY(-3px);filter:brightness(1.15);}
.rs-grade{font-family:var(--sg);font-size:1.125rem;font-weight:700;display:block;margin-bottom:.25rem;}
.rs-label{font-family:var(--mono);font-size:.55rem;letter-spacing:.1em;text-transform:uppercase;display:block;margin-bottom:.5rem;}
.rs-count{font-family:var(--sg);font-size:1rem;font-weight:600;display:block;}
.c-aaa{color:#10B981;}.c-aa{color:#34D399;}.c-a{color:#6EE7B7;}.c-bbb{color:#FBBF24;}.c-bb{color:#F59E0B;}.c-b{color:#F97316;}.c-ccc{color:#EF4444;}.c-d{color:#DC2626;}

/* divider / section */
.divider{position:relative;z-index:2;height:1px;margin:0 2rem;background:linear-gradient(90deg,transparent,rgba(245,158,11,0.3),rgba(99,102,241,0.25),transparent);}
.sec{position:relative;z-index:2;max-width:1160px;margin:0 auto;padding:7rem 2rem;}
.sec-lbl{font-family:var(--mono);font-size:.7rem;letter-spacing:.22em;text-transform:uppercase;color:var(--amber);margin-bottom:1rem;display:flex;align-items:center;gap:.75rem;}
.sec-lbl::before{content:'';width:24px;height:1.5px;background:linear-gradient(90deg,var(--amber),var(--amber2));}
h2.st{font-family:var(--sg);font-size:clamp(2.5rem,6vw,4rem);font-weight:700;letter-spacing:-.03em;color:var(--text);line-height:1.05;margin-bottom:1.25rem;}
h2.st .gs{background:linear-gradient(110deg,var(--amber2) 0%,var(--amber) 40%,var(--indigo2) 75%,var(--amber2) 100%);background-size:220% auto;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 5s linear infinite;}
.sec-sub{font-size:1.0625rem;color:var(--text2);line-height:1.65;max-width:540px;}

/* dashboard preview */
.dash{margin-top:3rem;background:rgba(15,18,33,0.85);border:1px solid rgba(245,158,11,0.14);border-radius:14px;overflow:hidden;position:relative;}
.dash::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--amber),var(--indigo2),transparent);background-size:200% auto;animation:scan 3.5s linear infinite;}
@keyframes scan{to{background-position:200% center;}}
.dash-bar{display:flex;align-items:center;gap:.5rem;padding:.9rem 1.5rem;background:rgba(8,11,20,.9);border-bottom:1px solid rgba(245,158,11,.08);}
.d-dot{width:9px;height:9px;border-radius:50%;}
.dd-r{background:#EF4444;}.dd-y{background:#F59E0B;}.dd-g{background:#10B981;}
.d-url{font-family:var(--mono);font-size:.72rem;color:var(--text3);margin-left:.75rem;letter-spacing:.04em;}
.dash-grid{display:grid;grid-template-columns:200px 1fr;min-height:500px;}
.dsb{background:rgba(6,8,16,.9);border-right:1px solid rgba(245,158,11,.08);padding:1.25rem .875rem;}
.dsb-logo{font-family:var(--sg);font-size:.9375rem;font-weight:700;color:var(--text);margin-bottom:1.75rem;padding:0 .5rem;display:flex;align-items:center;gap:.5rem;}
.dsb-s{font-family:var(--mono);font-size:.58rem;letter-spacing:.2em;text-transform:uppercase;color:var(--text3);margin:1rem 0 .5rem .5rem;}
.dsb-i{display:flex;align-items:center;gap:.625rem;padding:.5625rem .75rem;border-radius:6px;font-family:var(--body);font-size:.8125rem;font-weight:500;color:var(--text2);cursor:pointer;transition:all 180ms;margin-bottom:1px;text-decoration:none;}
.dsb-i:hover{background:rgba(245,158,11,.08);color:var(--text);}
.dsb-i.act{background:linear-gradient(90deg,rgba(245,158,11,.2),rgba(245,158,11,.06),transparent);color:var(--amber2);border-left:2px solid var(--amber);}
.dsb-badge{margin-left:auto;font-family:var(--mono);font-size:.58rem;background:rgba(239,68,68,.18);color:#F87171;padding:.1rem .4rem;border-radius:3px;}
.dm{padding:1.625rem;overflow:hidden;}
.dm-h{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;flex-wrap:wrap;gap:1rem;}
.dm-title{font-family:var(--sg);font-size:1.125rem;font-weight:700;color:var(--text);}
.dm-sub{font-family:var(--mono);font-size:.65rem;color:var(--text3);margin-top:.2rem;letter-spacing:.06em;}
.dm-acts{display:flex;gap:.5rem;}
.dm-b{font-family:var(--sg);font-size:.72rem;font-weight:600;padding:.4rem .9rem;border-radius:5px;cursor:pointer;border:none;transition:all 180ms;}
.dm-bp{background:linear-gradient(135deg,var(--amber),var(--amber2));color:#080B14;box-shadow:0 2px 12px rgba(245,158,11,.35);}
.dm-bs{background:rgba(245,158,11,.1);color:var(--amber2);border:1px solid rgba(245,158,11,.2);}

/* KPI row */
.krow{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;margin-bottom:1.5rem;}
.kpi{background:rgba(8,11,20,.7);border:1px solid rgba(245,158,11,.08);border-radius:8px;padding:1rem 1.125rem;position:relative;overflow:hidden;}
.kpi::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;border-radius:8px 8px 0 0;}
.k1::after{background:linear-gradient(90deg,var(--amber),var(--amber2));}
.k2::after{background:linear-gradient(90deg,var(--safe),var(--safe2));}
.k3::after{background:linear-gradient(90deg,var(--warn),#FBBF24);}
.k4::after{background:linear-gradient(90deg,var(--danger),#F87171);}
.knum{font-family:var(--sg);font-size:1.75rem;font-weight:700;color:var(--text);letter-spacing:-.03em;margin-bottom:.2rem;}
.klbl{font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--text3);}
.ktrend{font-family:var(--body);font-size:.72rem;font-weight:500;margin-top:.4rem;}
.kt-s{color:var(--safe2);}.kt-d{color:var(--danger);}

/* table */
.tbl-head{display:grid;grid-template-columns:1.8fr 1fr 1.2fr 1fr 1fr 1fr;gap:.75rem;padding:.5rem 1rem;margin-bottom:.375rem;}
.th{font-family:var(--mono);font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;color:var(--text3);}
.tbl-row{display:grid;grid-template-columns:1.8fr 1fr 1.2fr 1fr 1fr 1fr;gap:.75rem;align-items:center;padding:.75rem 1rem;border-radius:7px;background:rgba(8,11,20,.6);border:1px solid rgba(245,158,11,.07);margin-bottom:.4375rem;cursor:pointer;transition:border-color 200ms,background 200ms;text-decoration:none;}
.tbl-row:hover{border-color:rgba(245,158,11,.22);background:rgba(22,25,40,.7);}
.tc-name{font-family:var(--sg);font-size:.875rem;font-weight:600;color:var(--text);}
.tc-sym{font-family:var(--mono);font-size:.65rem;color:var(--text3);margin-top:.15rem;}
.tc-rating{display:inline-flex;align-items:center;gap:.35rem;}
.rat-pill{font-family:var(--sg);font-size:.8125rem;font-weight:700;padding:.2rem .625rem;border-radius:4px;}
.rat-bar{width:50px;height:4px;border-radius:2px;background:rgba(248,250,252,.06);overflow:hidden;margin-top:.3rem;}
.rb-fill{height:100%;border-radius:2px;}
.rb-safe{background:linear-gradient(90deg,var(--safe),var(--safe2));}
.rb-warn{background:linear-gradient(90deg,var(--warn),var(--amber));}
.rb-danger{background:linear-gradient(90deg,var(--danger),#F87171);}
.tc-peg{font-family:var(--mono);font-size:.8125rem;}
.tc-cap{font-family:var(--mono);font-size:.8rem;color:var(--text2);}
.tc-chg{font-family:var(--mono);font-size:.75rem;font-weight:500;}
.chg-s{color:var(--safe2);}.chg-d{color:var(--danger);}
.risk-ind{display:inline-flex;align-items:center;gap:.375rem;}
.ri-dot{width:7px;height:7px;border-radius:50%;}
.ri-lbl{font-family:var(--mono);font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;}
.low-r{color:var(--safe2);}.low-r .ri-dot{background:var(--safe2);box-shadow:0 0 6px var(--safe2);}
.mid-r{color:var(--amber);}.mid-r .ri-dot{background:var(--amber);box-shadow:0 0 6px var(--amber);}
.hi-r{color:var(--danger);}.hi-r .ri-dot{background:var(--danger);box-shadow:0 0 6px var(--danger);}

/* modules grid */
.mods{display:grid;grid-template-columns:repeat(3,1fr);gap:1.125rem;margin-top:3rem;}
.mod{padding:2rem 1.875rem;border-radius:10px;background:linear-gradient(135deg,rgba(245,158,11,.07) 0%,rgba(15,18,33,.9) 100%);border:1px solid rgba(245,158,11,.12);position:relative;overflow:hidden;transition:transform 260ms ease;}
.mod::before{content:'';position:absolute;top:0;left:0;right:0;height:1.5px;background:linear-gradient(90deg,transparent,var(--amber),var(--amber2),transparent);opacity:0;transition:opacity 280ms;}
.mod:hover{transform:translateY(-4px);}.mod:hover::before{opacity:1;}
.mod-icon{width:44px;height:44px;border-radius:10px;margin-bottom:1.375rem;background:linear-gradient(135deg,rgba(245,158,11,.25),rgba(99,102,241,.15));display:grid;place-items:center;font-size:1.25rem;box-shadow:0 4px 18px rgba(245,158,11,.2);}
.mod h3{font-family:var(--sg);font-size:1.125rem;font-weight:700;color:var(--text);margin-bottom:.5rem;letter-spacing:-.02em;}
.mod p{font-size:.9375rem;color:var(--text2);line-height:1.6;}

/* oracle */
.oracle-wrap{margin-top:3rem;background:rgba(15,18,33,.75);border:1px solid rgba(99,102,241,.18);border-radius:14px;overflow:hidden;position:relative;}
.oracle-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--indigo),var(--indigo2),transparent);background-size:200% auto;animation:scan 3.5s linear infinite reverse;}
.oracle-grid{display:grid;grid-template-columns:1fr 1fr;gap:0;}
.oracle-left{padding:2.5rem;border-right:1px solid rgba(99,102,241,.12);}
.oracle-right{padding:2.5rem;}
.oracle-lbl{font-family:var(--mono);font-size:.65rem;letter-spacing:.2em;text-transform:uppercase;color:var(--indigo2);margin-bottom:1.5rem;}
.oracle-item{display:flex;align-items:center;gap:1rem;padding:.875rem 1rem;background:rgba(8,11,20,.7);border:1px solid rgba(99,102,241,.1);border-radius:7px;margin-bottom:.625rem;transition:border-color 200ms;cursor:pointer;}
.oracle-item:hover{border-color:rgba(99,102,241,.28);}
.oi-icon{width:36px;height:36px;border-radius:8px;display:grid;place-items:center;font-size:1rem;flex-shrink:0;}
.oi-v{background:rgba(99,102,241,.16);border:1px solid rgba(99,102,241,.25);}
.oi-a{background:rgba(245,158,11,.14);border:1px solid rgba(245,158,11,.22);}
.oi-s{background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.22);}
.oi-name{font-family:var(--sg);font-size:.875rem;font-weight:600;color:var(--text);}
.oi-desc{font-family:var(--body);font-size:.78rem;color:var(--text3);margin-top:.15rem;}
.oi-status{margin-left:auto;font-family:var(--mono);font-size:.6rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;padding:.175rem .5rem;border-radius:3px;}
.ois-live{color:var(--safe2);background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.2);}
.ois-ready{color:var(--indigo2);background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);}
.code-block{background:rgba(6,8,16,.9);border:1px solid rgba(99,102,241,.15);border-radius:8px;padding:1.25rem 1.375rem;font-family:var(--mono);font-size:.75rem;line-height:1.7;overflow-x:auto;white-space:pre;}
.code-block .cm{color:var(--text3);}.code-block .ck{color:var(--indigo2);}.code-block .cv{color:var(--amber2);}.code-block .cs{color:var(--safe2);}.code-block .cn{color:#F87171;}

/* final cta */
.fcta{position:relative;z-index:2;max-width:960px;margin:8rem auto 5rem;padding:5rem 3rem;border-radius:16px;text-align:center;overflow:hidden;background:linear-gradient(135deg,rgba(245,158,11,.18) 0%,rgba(15,18,33,.95) 40%,rgba(99,102,241,.14) 100%);border:1px solid rgba(245,158,11,.2);}
.fcta::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--amber),var(--indigo2),transparent);background-size:200% auto;animation:scan 3.5s linear infinite;}
.fcta::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at 25% 50%,rgba(245,158,11,.1),transparent 55%);pointer-events:none;}
.fcta-i{position:relative;z-index:1;}
.fcta h2{font-family:var(--sg);font-size:clamp(2.25rem,6vw,3.75rem);font-weight:700;letter-spacing:-.03em;color:var(--text);line-height:1.05;margin-bottom:1.25rem;}
.fcta h2 .gs2{background:linear-gradient(110deg,var(--amber2) 0%,var(--amber) 40%,var(--indigo2) 75%,var(--amber2) 100%);background-size:220% auto;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 4s linear infinite;}
.fcta p{font-size:1.0625rem;color:var(--text2);line-height:1.65;margin:0 auto 2.5rem;max-width:520px;}
.btn-lt{background:var(--text);color:var(--bg);font-family:var(--sg);font-size:.9375rem;font-weight:700;padding:.9375rem 2.25rem;border-radius:7px;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;transition:all 280ms ease;}
.btn-lt:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(8,11,20,.6);}

footer{position:relative;z-index:2;padding:2.5rem 2rem;text-align:center;border-top:1px solid rgba(245,158,11,.08);}
footer p{font-family:var(--mono);font-size:.75rem;color:var(--text3);letter-spacing:.08em;}

/* reveal-on-scroll */
.reveal{opacity:0;transform:translateY(28px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1);}
.reveal.on{opacity:1;transform:translateY(0);}

/* wallet connect button slot (RainbowKit renders inside) */
.wallet-slot{display:inline-flex;align-items:center;}

/* mobile dashboard nav (shown instead of .dsb below the 1000px breakpoint
   so dashboard pages always have a way to navigate between tabs) */
.dsb-mobile{display:none;}

/* responsive */
@media(max-width:1000px){.dash-grid{grid-template-columns:1fr;}.dsb{display:none;}.dsb-mobile{display:flex;gap:.4rem;overflow-x:auto;padding:.75rem 1rem;background:rgba(6,8,16,.9);border-bottom:1px solid rgba(245,158,11,.08);}.dsb-mobile .dsb-i{flex-shrink:0;margin-bottom:0;white-space:nowrap;}.krow{grid-template-columns:repeat(2,1fr);}.oracle-grid{grid-template-columns:1fr;}.oracle-left{border-right:none;border-bottom:1px solid rgba(99,102,241,.12);}}
@media(max-width:820px){.ratings-row{grid-template-columns:repeat(4,1fr);}.mods{grid-template-columns:1fr;}.tbl-head{display:none;}.tbl-row{grid-template-columns:1fr 1fr;gap:.5rem;}}
@media(max-width:680px){nav{padding:.9rem 1.25rem;}.nav-links{display:none;}.hero{padding:4.5rem 1.25rem 3rem;}.sec{padding:5rem 1.25rem;}.krow{grid-template-columns:1fr;}.fcta{margin:4rem auto 3rem;padding:3.5rem 1.5rem;}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms !important;transition-duration:.01ms !important;}.reveal{opacity:1;transform:none;}}
"""


def main() -> None:
    written = []

    tokens_path = WEB / "styles" / "tokens.css"
    tokens_path.parent.mkdir(parents=True, exist_ok=True)
    if not tokens_path.exists():
        tokens_path.write_text(TOKENS_CSS, encoding="utf-8")
        written.append("styles/tokens.css")

    globals_path = WEB / "app" / "globals.css"
    globals_path.parent.mkdir(parents=True, exist_ok=True)
    if not globals_path.exists():
        globals_path.write_text(GLOBALS_CSS, encoding="utf-8")
        written.append("app/globals.css")

    print(f"Web root: {WEB}")
    print(f"Created {len(written)} file(s).")
    for f in written:
        print(f"  + {f}")
    if not written:
        print("Nothing to do - all files already exist.")


if __name__ == "__main__":
    main()
