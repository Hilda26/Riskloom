"use client";

import { useEffect, useState } from "react";
import { useAccount } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";

const GUEST_KEY = "riskloom_guest_mode";

export function WalletGuard({ children }: { children: React.ReactNode }) {
  const { isConnected } = useAccount();
  const [guest, setGuest] = useState(false);

  // Persist guest mode for the browser session so it survives client-side
  // navigation between dashboard pages.
  useEffect(() => {
    if (sessionStorage.getItem(GUEST_KEY) === "1") setGuest(true);
  }, []);

  function continueAsGuest() {
    sessionStorage.setItem(GUEST_KEY, "1");
    setGuest(true);
  }

  if (isConnected || guest) {
    return <>{children}</>;
  }

  return (
    <div style={{ padding: "4rem 2rem", textAlign: "center" }}>
      <p style={{ color: "var(--text2)", marginBottom: "1.5rem" }}>
        Connect a wallet to access the full risk intelligence dashboard.
      </p>
      <ConnectButton />
      <div style={{ marginTop: "1.75rem" }}>
        <button
          className="dm-b dm-bs"
          onClick={continueAsGuest}
          style={{ cursor: "pointer" }}
        >
          Continue as guest (read-only)
        </button>
        <p style={{ color: "var(--text2)", fontSize: ".75rem", marginTop: ".6rem", opacity: 0.75 }}>
          Browse live ratings and the on-chain oracle without a wallet. Sign in
          with a wallet to link an account.
        </p>
      </div>
    </div>
  );
}
