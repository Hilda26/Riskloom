import type { StableScoreGrade } from "@stableshield/shared-types";

export interface RiskScore {
  stablecoin_id: string;
  rating: StableScoreGrade;
  score_numeric: number;
  reserve_subscore: number | null;
  issuer_subscore: number | null;
  peg_subscore: number | null;
  regulatory_subscore: number | null;
  sentiment_subscore: number | null;
  updated_at: string;
}

export interface Stablecoin {
  id: string;
  symbol: string;
  name: string;
  chain: string;
  contract_address: string | null;
  decimals: number;
  market_cap_usd: number | null;
  peg_price: number;
}

export interface StablecoinWithScore extends Stablecoin {
  risk_scores: RiskScore | null;
}

export interface RiskScoreHistoryEntry {
  rating: StableScoreGrade;
  score_numeric: number;
  reason_summary: string | null;
  recorded_at: string;
}

export interface Alert {
  id: string;
  stablecoin_id: string;
  severity: "info" | "warning" | "critical";
  message: string;
  triggered_at: string;
  resolved_at: string | null;
}
