import Link from "next/link";
import { createClient } from "@/lib/supabase/server";
import { KpiRow } from "@/components/dashboard/KpiRow";
import { StablecoinTable } from "@/components/dashboard/StablecoinTable";
import { ExportReportButton } from "@/components/dashboard/ExportReportButton";
import type { StablecoinWithScore } from "@/types/risk";

export const revalidate = 0;

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data } = await supabase
    .from("stablecoins")
    .select("*, risk_scores(*)")
    .order("symbol");
  const items = (data ?? []) as unknown as StablecoinWithScore[];

  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">Risk Intelligence Dashboard</div>
          <div className="dm-sub">LIVE - {items.length} assets - StudioNet Oracle</div>
        </div>
        <div className="dm-acts">
          <ExportReportButton items={items} />
          <Link href="/alerts" className="dm-b dm-bp" style={{ textDecoration: "none" }}>
            &#9889; Live Alerts
          </Link>
        </div>
      </div>
      <KpiRow items={items} />
      <StablecoinTable items={items} />
    </>
  );
}
