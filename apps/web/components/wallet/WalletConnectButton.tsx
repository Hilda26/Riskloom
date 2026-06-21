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
