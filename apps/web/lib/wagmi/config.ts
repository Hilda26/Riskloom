// wagmi + RainbowKit configuration. Supports MetaMask, Rainbow,
// Zerion, Coinbase Wallet, and any other WalletConnect-compatible
// wallet out of the box, per the project's wallet-auth requirement.
import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { http } from "wagmi";
import { mainnet, sepolia } from "wagmi/chains";

// wagmi/viem's default RPC for mainnet (eth.merkle.io) rejects
// cross-origin browser requests with a CORS error, which floods the
// console with failed background polls - publicnode.com's endpoints
// allow any origin.
export const wagmiConfig = getDefaultConfig({
  appName: "StableShield AI",
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID ?? "",
  chains: [mainnet, sepolia],
  transports: {
    [mainnet.id]: http("https://ethereum-rpc.publicnode.com"),
    [sepolia.id]: http("https://ethereum-sepolia-rpc.publicnode.com"),
  },
  ssr: true,
});
