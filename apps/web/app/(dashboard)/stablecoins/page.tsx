import { createClient } from "@/lib/supabase/server";
import { StablecoinTable } from "@/components/dashboard/StablecoinTable";
import type { StablecoinWithScore } from "@/types/risk";

export const revalidate = 0;

export default async function StablecoinsPage() {
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
          <div className="dm-title">All Stablecoins</div>
          <div className="dm-sub">{items.length} assets tracked</div>
        </div>
      </div>
      <StablecoinTable items={items} />
    </>
  );
}
