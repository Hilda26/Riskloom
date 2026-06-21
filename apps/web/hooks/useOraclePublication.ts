"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { OraclePublication } from "@/types/genlayer";

export function useOraclePublication(stablecoinId: string | null) {
  const [publications, setPublications] = useState<OraclePublication[]>([]);

  useEffect(() => {
    if (!stablecoinId) return;
    const supabase = createClient();

    supabase
      .from("oracle_publications")
      .select("*")
      .eq("stablecoin_id", stablecoinId)
      .order("published_at", { ascending: false })
      .limit(20)
      .then(({ data }) => {
        if (data) setPublications(data as OraclePublication[]);
      });
  }, [stablecoinId]);

  return publications;
}
