// Mirrors intelligent-contracts/stablescore_oracle/contract.gpy.
// Kept here so the frontend can render the oracle panel and call
// read methods without re-deriving the contract shape by hand.
export interface StableScoreOracleContract {
  register_stablecoin(symbol: string, name: string): string;
  update_score(args: {
    symbol: string;
    reserve_subscore: number;
    issuer_subscore: number;
    peg_subscore: number;
    regulatory_subscore: number;
    sentiment_subscore: number;
    peg_price_bps: number;
    reserve_ratio_bps: number;
    evidence_summary: string;
    updated_at: string;
  }): string;
  // The contract never raises - an unregistered symbol returns
  // { error } instead of throwing, so callers must narrow this union.
  get_score(symbol: string):
    | {
        symbol: string;
        name: string;
        rating: string;
        score: number;
        peg: number;
        reserve_ratio: number;
        updated_at: string;
      }
    | { error: string };
  get_history(symbol: string, limit: number): Array<{
    rating: string;
    score: number;
    reason: string;
    recorded_at: string;
  }>;
  is_safe(symbol: string, min_rating: string): boolean;
  list_stablecoins(): string[];
}

export const STABLESCORE_ORACLE_METHODS = [
  "register_stablecoin",
  "update_score",
  "get_score",
  "get_history",
  "is_safe",
  "list_stablecoins",
] as const;
