# Risk Intelligence API

Base URL: `https://<your-domain>/api/v1` (proxies to the Supabase
Edge Functions of the same name, so either base URL works).

All endpoints require an `x-api-key` header. Keys are issued per
profile in the `api_keys` table and scoped (e.g. `read:scores`).

## GET /api/v1/scores

Current StableScore ratings for all tracked stablecoins, or a single
symbol.

**Query params**
- `symbol` (optional) - e.g. `USDC`. Omit to return all.

**Response**
```json
{
  "data": [
    {
      "rating": "AAA",
      "score_numeric": 98.25,
      "updated_at": "2026-06-20T12:00:00Z",
      "stablecoins": { "symbol": "USDC", "name": "USD Coin" }
    }
  ]
}
```

## GET /api/v1/history

Historical StableScore ratings for one symbol.

**Query params**
- `symbol` (required) - e.g. `USDC`
- `limit` (optional, default 100, max 500)

**Response**
```json
{
  "data": [
    {
      "rating": "AAA",
      "score_numeric": 98.25,
      "reason_summary": null,
      "recorded_at": "2026-06-20T12:00:00Z"
    }
  ]
}
```

## Errors

| Status | Meaning |
|---|---|
| 401 | Missing `x-api-key` header |
| 403 | Invalid, revoked, or insufficiently-scoped API key |
| 404 | Unknown `symbol` |
| 500 | Internal error |

## On-chain alternative

Anyone can also read scores directly from the `StableScoreOracle`
Intelligent Contract on GenLayer StudioNet via `get_score`,
`get_history`, and `is_safe` - no API key required, fully
decentralized, paid in GEN per call per GenLayer's fee model. See
`intelligent-contracts/stablescore_oracle/interface.json`.
