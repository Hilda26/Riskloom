import { ActionButton } from "@/components/ui/Button";

export default function ReportsPage() {
  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">Compliance Reports</div>
          <div className="dm-sub">Institution-grade StableScore&trade; exports</div>
        </div>
        <div className="dm-acts">
          <ActionButton variant="primary">Generate Report</ActionButton>
        </div>
      </div>
      <p style={{ color: "var(--text2)", maxWidth: "540px" }}>
        Scheduled PDF/CSV compliance exports (reserve composition, issuer
        filings, peg history, regulatory events) are generated from the same
        data backing the dashboard. Report generation wiring lands once the
        api-v1-history endpoint has production traffic to validate against.
      </p>
    </>
  );
}
