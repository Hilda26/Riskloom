import { createClient } from "@/lib/supabase/server";
import { ExportAuditButton } from "@/components/reports/ExportAuditButton";
import { RatingPill } from "@/components/ui/RatingPill";
import type { StableScoreGrade } from "@stableshield/shared-types";

export const revalidate = 0;

export default async function ReportsPage() {
  const supabase = await createClient();
  const { data } = await supabase
    .from("oracle_publications")
    .select("*, stablecoins(symbol, name)")
    .order("published_at", { ascending: false })
    .limit(50);

  const entries = data ?? [];

  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">Audit Trail</div>
          <div className="dm-sub">{entries.length} oracle publications recorded</div>
        </div>
        <div className="dm-acts">
          <ExportAuditButton entries={entries} />
        </div>
      </div>

      {entries.length === 0 && (
        <p style={{ color: "var(--text2)" }}>
          No oracle publications recorded yet. Scores published to the GenLayer
          StableScoreOracle contract will appear here automatically.
        </p>
      )}

      <div>
        {entries.length > 0 && (
          <div
            className="tbl-head"
            style={{ gridTemplateColumns: "1.2fr .6fr .8fr .8fr 1.6fr" }}
          >
            <div className="th">Stablecoin</div>
            <div className="th">Rating</div>
            <div className="th">Status</div>
            <div className="th">Network</div>
            <div className="th">Published</div>
          </div>
        )}
        {entries.map((entry) => (
          <div
            className="tbl-row"
            key={entry.id}
            style={{
              gridTemplateColumns: "1.2fr .6fr .8fr .8fr 1.6fr",
              cursor: "default",
            }}
          >
            <div>
              <div className="tc-name">
                {entry.stablecoins?.name ?? "Unknown"}
              </div>
              <div className="tc-sym">
                {entry.stablecoins?.symbol ?? entry.stablecoin_id}
              </div>
            </div>
            <div>
              <RatingPill
                grade={entry.published_rating as StableScoreGrade}
              />
            </div>
            <div
              className={`risk-ind ${
                entry.status === "confirmed"
                  ? "low-r"
                  : entry.status === "pending"
                    ? "mid-r"
                    : "hi-r"
              }`}
            >
              <span className="ri-dot" />
              <span className="ri-lbl">{entry.status}</span>
            </div>
            <div className="tc-sym">{entry.network}</div>
            <div className="tc-sym">
              {new Date(entry.published_at).toLocaleString()}
              {entry.tx_hash && (
                <span
                  style={{
                    marginLeft: ".5rem",
                    fontSize: ".65rem",
                    opacity: 0.6,
                  }}
                >
                  tx:{entry.tx_hash.slice(0, 10)}...
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
