"use client";

interface AuditEntry {
  id: string;
  stablecoin_id: string;
  tx_hash: string | null;
  contract_address: string;
  network: string;
  published_rating: string;
  published_at: string;
  status: string;
  stablecoins?: { symbol: string; name: string } | null;
}

function buildCsv(rows: AuditEntry[]): string {
  const header = "Symbol,Name,Rating,Status,Network,Contract,TxHash,Published At";
  const lines = rows.map((r) =>
    [
      r.stablecoins?.symbol ?? "",
      `"${r.stablecoins?.name ?? ""}"`,
      r.published_rating,
      r.status,
      r.network,
      r.contract_address,
      r.tx_hash ?? "",
      r.published_at,
    ].join(","),
  );
  return [header, ...lines].join("\n");
}

export function ExportAuditButton({ entries }: { entries: AuditEntry[] }) {
  function handleExport() {
    const csv = buildCsv(entries);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `riskloom-audit-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <button className="dm-b dm-bp" onClick={handleExport}>
      Export Audit Trail
    </button>
  );
}
