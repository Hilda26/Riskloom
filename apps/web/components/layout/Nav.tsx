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
        <a href="https://docs.genlayer.com/" target="_blank" rel="noreferrer" className="nav-ghost">Docs</a>
        <div className="wallet-slot">
          <WalletConnectButton />
        </div>
      </div>
    </nav>
  );
}
