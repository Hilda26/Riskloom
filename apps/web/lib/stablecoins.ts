// Shared data loader: pulls the tracked stablecoins (plus their current
// risk scores) from Supabase, then overlays live peg price / market cap
// from CoinGecko. Every page that lists stablecoins uses this so the
// live-data behaviour is identical everywhere.
import { createClient } from "@/lib/supabase/server";
import { fetchLiveMarketData, applyLiveMarketData } from "@/lib/marketdata";
import type { StablecoinWithScore } from "@/types/risk";

export async function getStablecoinsWithLiveData(): Promise<StablecoinWithScore[]> {
  const supabase = await createClient();
  const { data } = await supabase
    .from("stablecoins")
    .select("*, risk_scores(*)")
    .order("symbol");
  const items = (data ?? []) as unknown as StablecoinWithScore[];
  const live = await fetchLiveMarketData();
  return applyLiveMarketData(items, live);
}
