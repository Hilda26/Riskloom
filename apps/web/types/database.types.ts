// Hand-authored mirror of the Supabase schema (backend/supabase/migrations).
// Replace with `supabase gen types typescript` output once the project is
// live - keeping this checked in means the frontend type-checks before
// that step happens.
export interface Database {
  public: {
    Tables: {
      wallets: {
        Row: {
          id: string;
          address: string;
          chain_id: number;
          created_at: string;
          last_login_at: string | null;
        };
      };
      profiles: {
        Row: {
          id: string;
          wallet_id: string;
          display_name: string | null;
          tier: "free" | "pro" | "institutional";
          created_at: string;
        };
      };
      stablecoins: {
        Row: {
          id: string;
          symbol: string;
          name: string;
          issuer_id: string | null;
          chain: string;
          contract_address: string | null;
          decimals: number;
          launched_at: string | null;
          market_cap_usd: number | null;
          peg_price: number;
        };
      };
      risk_scores: {
        Row: {
          id: string;
          stablecoin_id: string;
          rating: string;
          score_numeric: number;
          reserve_subscore: number | null;
          issuer_subscore: number | null;
          peg_subscore: number | null;
          regulatory_subscore: number | null;
          sentiment_subscore: number | null;
          updated_at: string;
        };
      };
      risk_score_history: {
        Row: {
          id: string;
          stablecoin_id: string;
          rating: string;
          score_numeric: number;
          reason_summary: string | null;
          recorded_at: string;
        };
      };
      alerts: {
        Row: {
          id: string;
          stablecoin_id: string;
          severity: "info" | "warning" | "critical";
          message: string;
          triggered_at: string;
          resolved_at: string | null;
        };
      };
      oracle_publications: {
        Row: {
          id: string;
          stablecoin_id: string;
          tx_hash: string | null;
          contract_address: string;
          network: string;
          published_rating: string;
          published_at: string;
          status: "pending" | "confirmed" | "failed";
        };
      };
    };
  };
}
