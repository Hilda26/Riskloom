"use client";

import { useState } from "react";

interface PublishResult {
  status?: "confirmed" | "failed";
  txHash?: string | null;
  rating?: string;
  error?: string;
}

export function PublishOnChainButton({ symbol }: { symbol: string }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PublishResult | null>(null);

  async function publish() {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`/api/publish/${encodeURIComponent(symbol)}`, {
        method: "POST",
      });
      const body = (await res.json()) as PublishResult;
      setResult(body);
    } catch (err) {
      setResult({ error: String(err) });
    } finally {
      setLoading(false);
    }
  }

  const txUrl = result?.txHash
    ? `https://explorer-studio.genlayer.com/tx/${result.txHash}`
    : null;

  return (
    <div style={{ marginTop: "1rem" }}>
      <button
        className="dm-b dm-bp"
        onClick={publish}
        disabled={loading}
        style={{ cursor: loading ? "wait" : "pointer" }}
      >
        {loading ? "Publishing to GenLayer..." : `⚡ Publish ${symbol} score on-chain`}
      </button>

      {loading && (
        <p style={{ color: "var(--text2)", fontSize: ".75rem", marginTop: ".6rem" }}>
          Signing and submitting an <code>update_score</code> transaction, then
          waiting for validator consensus. This can take ~20-40s.
        </p>
      )}

      {result && !loading && (
        <div style={{ marginTop: ".8rem", fontSize: ".8rem" }}>
          {result.error && (
            <p style={{ color: "var(--danger, #ef4444)" }}>
              Could not publish: {result.error}
            </p>
          )}

          {!result.error && (
            <>
              <p style={{ color: result.status === "confirmed" ? "var(--ok, #22c55e)" : "var(--warn, #f59e0b)" }}>
                Transaction {result.status === "confirmed" ? "confirmed on-chain" : "submitted"}
                {result.rating ? ` - published rating ${result.rating}` : ""}.
              </p>
              {txUrl ? (
                <p style={{ marginTop: ".3rem" }}>
                  <a href={txUrl} target="_blank" rel="noreferrer" style={{ color: "var(--amber2, #fbbf24)", textDecoration: "underline" }}>
                    View on GenLayer Explorer &rarr;
                  </a>
                  <span style={{ display: "block", color: "var(--text2)", marginTop: ".3rem", wordBreak: "break-all", fontFamily: "var(--mono)" }}>
                    {result.txHash}
                  </span>
                  <span style={{ display: "block", color: "var(--text2)", marginTop: ".3rem" }}>
                    Watch it move through proposing &rarr; committing &rarr; revealing
                    &rarr; accepted &rarr; finalized.
                  </span>
                </p>
              ) : (
                <p style={{ color: "var(--text2)", marginTop: ".3rem" }}>
                  No transaction hash was returned - check the Audit Trail for the
                  recorded publication.
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
