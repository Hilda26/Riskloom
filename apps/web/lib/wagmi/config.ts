// wagmi + RainbowKit configuration. Supports MetaMask, Rainbow,
// Zerion, Coinbase Wallet, and any other WalletConnect-compatible
// wallet out of the box, per the project's wallet-auth requirement.
import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { mainnet, sepolia } from "wagmi/chains";

export const wagmiConfig = getDefaultConfig({
  appName: "StableShield AI",
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID ?? "",
  chains: [mainnet, sepolia],
  ssr: true,
});
