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
