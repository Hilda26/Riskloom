export interface OraclePublication {
  id: string;
  stablecoin_id: string;
  tx_hash: string | null;
  contract_address: string;
  network: string;
  published_rating: string;
  published_at: string;
  status: "pending" | "confirmed" | "failed";
}
