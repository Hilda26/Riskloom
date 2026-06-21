"use client";

import { useEffect, useRef } from "react";
import { useAccount, useChainId, useSignMessage } from "wagmi";
import { buildSiweMessage, fetchNonce, verifySiwe } from "@/lib/siwe";

// Triggers the Sign-In With Ethereum flow the first time a wallet
// connects in this session, then exchanges the resulting magic link
// for a Supabase session via /auth/callback.
export function useWalletAuth() {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { signMessageAsync } = useSignMessage();
  const attempted = useRef<string | null>(null);

  useEffect(() => {
    if (!isConnected || !address) return;
    if (attempted.current === address) return;
    attempted.current = address;

    (async () => {
      try {
        const nonce = await fetchNonce(address);
        const siweMessage = buildSiweMessage({ address, chainId, nonce });
        const preparedMessage = siweMessage.prepareMessage();
        const signature = await signMessageAsync({ message: preparedMessage });
        const { actionLink } = await verifySiwe(preparedMessage, signature);
        window.location.href = actionLink;
      } catch (err) {
        console.error("SIWE sign-in failed", err);
        attempted.current = null;
      }
    })();
  }, [address, isConnected, chainId, signMessageAsync]);
}
