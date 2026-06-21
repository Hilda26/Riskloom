import { createClient } from "@/lib/supabase/server";

export const revalidate = 0;

export default async function AlertsPage() {
  const supabase = await createClient();
  const { data } = await supabase
    .from("alerts")
    .select("*, stablecoins(symbol, name)")
    .order("triggered_at", { ascending: false })
    .limit(50);

  const alerts = data ?? [];

  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">Risk Feed</div>
          <div className="dm-sub">{alerts.length} recent alerts</div>
        </div>
      </div>
      {alerts.length === 0 && (
        <p style={{ color: "var(--text2)" }}>No alerts recorded yet.</p>
      )}
      {alerts.map((alert) => (
        <div
          className="tbl-row"
          key={alert.id}
          style={{ gridTemplateColumns: "1fr 3fr 1fr", cursor: "default" }}
        >
          <div className={alert.severity === "critical" ? "hi-r risk-ind" : alert.severity === "warning" ? "mid-r risk-ind" : "low-r risk-ind"}>
            <span className="ri-dot" />
            <span className="ri-lbl">{alert.severity}</span>
          </div>
          <div className="tc-name">{alert.message}</div>
          <div className="tc-sym">{new Date(alert.triggered_at).toLocaleString()}</div>
        </div>
      ))}
    </>
  );
}
