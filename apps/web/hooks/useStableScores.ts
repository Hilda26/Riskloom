"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { StablecoinWithScore } from "@/types/risk";

export function useStableScores(initial: StablecoinWithScore[] = []) {
  const [items, setItems] = useState<StablecoinWithScore[]>(initial);

  useEffect(() => {
    const supabase = createClient();

    const channel = supabase
      .channel("risk_scores_changes")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "risk_scores" },
        async () => {
          const { data } = await supabase
            .from("stablecoins")
            .select("*, risk_scores(*)")
            .order("symbol");
          if (data) setItems(data as unknown as StablecoinWithScore[]);
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return items;
}
