"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import type { Alert } from "@/types/risk";

export function useRealtimeAlerts(initial: Alert[] = []) {
  const [alerts, setAlerts] = useState<Alert[]>(initial);

  useEffect(() => {
    const supabase = createClient();

    const channel = supabase
      .channel("alerts_changes")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "alerts" },
        (payload) => {
          setAlerts((prev) => [payload.new as Alert, ...prev]);
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return alerts;
}
