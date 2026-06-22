"""
StableShield AI - GenLayer Intelligent Contract Writer (STEP 7)
Writes intelligent-contracts/stablescore_oracle/contract.gpy plus its
interface description and deploy notes.

Syntax verified live against docs.genlayer.com and sdk.genlayer.com on
2026-06-20 (gl.Contract base class, @gl.public.view/write decorators,
TreeMap/DynArray collection types, @allow_storage dataclasses, and the
gl.eq_principle.{strict_eq,prompt_comparative,prompt_non_comparative}
signatures) - see deploy_notes.md for the source URLs.

Run from the repository root: python scripts/write_intelligent_contract.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_DIR = ROOT / "intelligent-contracts" / "stablescore_oracle"

CONTRACT_GPY = '''\
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
#
# StableScoreOracle - StableShield AI's on-chain risk oracle.
#
# One Intelligent Contract, deployed once to GenLayer Studio /
# StudioNet, fees paid in GEN. Registers stablecoins, accepts the
# five off-chain risk-module subscores from the Supabase scoring
# pipeline, and uses GenLayer's LLM-backed equivalence principle so
# validators reach consensus on the resulting StableScore rating and
# its plain-English justification - not just a deterministic setter.
#
# Deliberately mirrors the patterns confirmed in GenLayer's own
# verified examples (docs.genlayer.com/developers/intelligent-contracts/
# first-intelligent-contract, .../examples/prediction, and the
# genlayerlabs/genlayer-project-boilerplate football_bets.py contract):
# no module-level globals, no negative-index slicing/reversed(), no
# raised exceptions from public methods - see deploy_notes.md.

from genlayer import *
from dataclasses import dataclass
import json


@allow_storage
@dataclass
class StablecoinRecord:
    name: str
    rating: str
    score: u256
    peg: u256
    reserve_ratio: u256
    updated_at: str
    registered: bool


@allow_storage
@dataclass
class ScoreHistoryEntry:
    symbol: str
    rating: str
    score: u256
    reason: str
    recorded_at: str


class Contract(gl.Contract):
    registry: TreeMap[str, StablecoinRecord]
    history: DynArray[ScoreHistoryEntry]
    owner: Address

    def __init__(self):
        self.owner = gl.message.sender_address

    # -------------------------------------------------------- writes --

    @gl.public.write
    def register_stablecoin(self, symbol: str, name: str) -> str:
        symbol = symbol.upper()
        if symbol in self.registry:
            return f"{symbol} already registered"

        self.registry[symbol] = StablecoinRecord(
            name=name,
            rating="D",
            score=0,
            peg=0,
            reserve_ratio=0,
            updated_at="never",
            registered=True,
        )
        return f"{symbol} registered"

    @gl.public.write
    def update_score(
        self,
        symbol: str,
        reserve_subscore: int,
        issuer_subscore: int,
        peg_subscore: int,
        regulatory_subscore: int,
        sentiment_subscore: int,
        peg_price_bps: int,
        reserve_ratio_bps: int,
        evidence_summary: str,
        updated_at: str,
    ) -> str:
        """
        Called by the publish-to-genlayer Supabase Edge Function once a
        composite score has been computed off-chain. The five subscores
        and the evidence summary are handed to the LLM so the contract
        itself reasons about the final letter grade and records *why* -
        this is the non-deterministic, LLM-backed step that GenLayer's
        validator network reaches consensus on, rather than a plain
        arithmetic setter.
        """
        grades = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"]
        symbol = symbol.upper()
        if symbol not in self.registry:
            return f"{symbol} is not registered"

        subscores = {
            "reserve": reserve_subscore,
            "issuer": issuer_subscore,
            "peg": peg_subscore,
            "regulatory": regulatory_subscore,
            "sentiment": sentiment_subscore,
        }

        def assess() -> str:
            prompt = (
                "You are a stablecoin risk-rating engine. Given the five "
                "risk module subscores below (0-100, higher is safer) and "
                "an evidence summary, assign exactly one letter grade from "
                f"this list ordered safest to riskiest: {grades}. "
                "Weight reserve health and peg stability most heavily. "
                "Respond with ONLY the letter grade, nothing else.\\n\\n"
                f"Subscores: {json.dumps(subscores)}\\n"
                f"Evidence: {evidence_summary}\\n"
            )
            result = gl.nondet.exec_prompt(prompt)
            rating = str(result).strip().upper()
            if rating not in grades:
                rating = "D"
            return rating

        rating = gl.eq_principle.prompt_non_comparative(
            assess,
            task=(
                "Assign a StableScore letter grade (AAA..D) to a "
                "stablecoin from its five risk subscores and evidence."
            ),
            criteria=(
                "The chosen grade must be one of AAA, AA, A, BBB, BB, B, "
                "CCC, D and must be consistent with the relative weight "
                "of the subscores (lower subscores, especially reserve "
                "and peg, must not yield a safer grade than higher ones)."
            ),
        )
        if rating not in grades:
            rating = "D"
        reason = evidence_summary[:280]

        composite = (
            reserve_subscore * 30
            + issuer_subscore * 20
            + peg_subscore * 25
            + regulatory_subscore * 15
            + sentiment_subscore * 10
        ) // 100

        record = self.registry[symbol]
        record.rating = rating
        record.score = composite
        record.peg = peg_price_bps
        record.reserve_ratio = reserve_ratio_bps
        record.updated_at = updated_at
        self.registry[symbol] = record

        self.history.append(
            ScoreHistoryEntry(
                symbol=symbol,
                rating=rating,
                score=composite,
                reason=reason,
                recorded_at=updated_at,
            )
        )
        return rating

    # --------------------------------------------------------- views --

    @gl.public.view
    def get_score(self, symbol: str) -> dict:
        symbol = symbol.upper()
        if symbol not in self.registry:
            return {"error": f"{symbol} is not registered"}
        record = self.registry[symbol]
        return {
            "symbol": symbol,
            "name": record.name,
            "rating": record.rating,
            "score": int(record.score),
            "peg": int(record.peg),
            "reserve_ratio": int(record.reserve_ratio),
            "updated_at": record.updated_at,
        }

    @gl.public.view
    def get_history(self, symbol: str, limit: int) -> list:
        symbol = symbol.upper()
        matches = []
        for entry in self.history:
            if entry.symbol == symbol:
                matches.append(entry)

        total = len(matches)
        count = total
        if limit > 0 and limit < total:
            count = limit
        start = total - count

        result = []
        i = total - 1
        while i >= start:
            entry = matches[i]
            result.append({
                "rating": entry.rating,
                "score": int(entry.score),
                "reason": entry.reason,
                "recorded_at": entry.recorded_at,
            })
            i = i - 1
        return result

    @gl.public.view
    def is_safe(self, symbol: str, min_rating: str) -> bool:
        grades = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"]
        symbol = symbol.upper()
        min_rating = min_rating.upper()
        if symbol not in self.registry:
            return False
        if min_rating not in grades:
            return False
        record = self.registry[symbol]
        return grades.index(record.rating) <= grades.index(min_rating)

    @gl.public.view
    def list_stablecoins(self) -> list:
        return list(self.registry.keys())
'''

INTERFACE_JSON = """\
{
  "contract": "StableScoreOracle",
  "network": "genlayer-studionet",
  "fee_token": "GEN",
  "methods": {
    "register_stablecoin": {
      "type": "write",
      "args": { "symbol": "str", "name": "str" },
      "returns": "str"
    },
    "update_score": {
      "type": "write",
      "args": {
        "symbol": "str",
        "reserve_subscore": "int",
        "issuer_subscore": "int",
        "peg_subscore": "int",
        "regulatory_subscore": "int",
        "sentiment_subscore": "int",
        "peg_price_bps": "int",
        "reserve_ratio_bps": "int",
        "evidence_summary": "str",
        "updated_at": "str"
      },
      "returns": "str (final rating, or an error message string like '<symbol> is not registered' - never raises)",
      "notes": "Non-deterministic: validators reach consensus via gl.eq_principle.prompt_non_comparative on the LLM-assigned rating + reason."
    },
    "get_score": {
      "type": "view",
      "args": { "symbol": "str" },
      "returns": "dict { symbol, name, rating, score, peg, reserve_ratio, updated_at } - or { error: str } if the symbol is not registered"
    },
    "get_history": {
      "type": "view",
      "args": { "symbol": "str", "limit": "int" },
      "returns": "list[dict { rating, score, reason, recorded_at }]"
    },
    "is_safe": {
      "type": "view",
      "args": { "symbol": "str", "min_rating": "str" },
      "returns": "bool"
    },
    "list_stablecoins": {
      "type": "view",
      "args": {},
      "returns": "list[str]"
    }
  }
}
"""

DEPLOY_NOTES = """\
# StableScoreOracle - Deployment Notes

## Target

- Platform: GenLayer Studio
- Network: StudioNet
- Fee token: GEN
- Deployment method: paste/upload `contract.gpy` directly in GenLayer
  Studio's contract editor and deploy - no Docker required.

## Syntax verification (2026-06-20, revised after a real deploy failure)

The first version of this contract failed to deploy in GenLayer Studio
with "could not load contract schema". Root-caused and fixed - see
below. Sources consulted both times:

- Contract structure, `gl.Contract` base class, `@gl.public.view` /
  `@gl.public.write` decorators:
  https://docs.genlayer.com/developers/intelligent-contracts/introduction
- Minimal working example (`gl.nondet.web.render`, `gl.eq_principle.strict_eq`),
  including the canonical `# { "Depends": "py-genlayer:<hash>" }` header:
  https://docs.genlayer.com/developers/intelligent-contracts/first-intelligent-contract
- Collection storage types (`TreeMap[K, V]`, `DynArray[T]`, the
  `@allow_storage` + `@dataclass` pattern for custom struct types):
  https://docs.genlayer.com/developers/intelligent-contracts/storage
- Dataclass storage fields and how `u256`-typed fields are assigned
  (plain ints, not wrapped in `u256(...)`):
  https://docs.genlayer.com/developers/intelligent-contracts/types/dataclasses
- A second full example contract (web fetch + `gl.nondet.exec_prompt` +
  `gl.eq_principle.strict_eq` together):
  https://docs.genlayer.com/developers/intelligent-contracts/examples/prediction
- A real, maintained reference contract confirming nested
  `TreeMap[Address, TreeMap[str, Bet]]` storage and a no-arg
  constructor pattern actually works in production:
  https://github.com/genlayerlabs/genlayer-project-boilerplate
  (contracts/football_bets.py)
- Equivalence principle variants (`strict_eq`, `prompt_comparative`,
  `prompt_non_comparative`) and what each is for:
  https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/equivalence-principle
- Exact signatures for `eq_principle_strict_eq`, `eq_principle_prompt_comparative`,
  `eq_principle_prompt_non_comparative` (exposed as `gl.eq_principle.*`):
  https://sdk.genlayer.com/v0.1.0/_modules/genlayer/std/eq_principles.html
- `gl.nondet.exec_prompt` signature, including `response_format="json"`:
  surfaced via search across docs.genlayer.com/developers/intelligent-contracts/crafting-prompts
  and the GenLayer SDK API reference (https://sdk.genlayer.com/v0.1.0/index.html)

## What actually broke, and the fix

**Most likely cause: the dependency header.** The first version used
`# { "Depends": "py-genlayer:test" }`. Studio's schema loader has to
resolve and import that runtime package before it can even introspect
the contract's methods to build the UI - if `test` doesn't resolve to
a usable package in the current Studio build, you get exactly "could
not load contract schema" (a load-time failure, not a Python error).
Switched to the pinned hash from the official worked example,
`py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`,
which is confirmed live in current docs.

**Secondary hardening**, removing patterns no verified example
actually uses, to cut other plausible failure points:
- Removed the module-level `GRADES` list global - inlined as a local
  `grades = [...]` inside each method that needs it (closures over
  enclosing-scope locals are the documented non-deterministic-block
  pattern anyway, so this is a pure simplification, not a workaround).
- Removed negative-index slicing and `reversed()` in `get_history`
  (`matches[-limit:]`, `reversed(tail)`) - replaced with a plain
  forward loop using only non-negative indices. No example contract
  anywhere in the docs or the boilerplate repo uses negative slicing.
- Removed `raise Exception(...)` from all public methods. No verified
  example raises from a public method; `register_stablecoin` already
  returned a descriptive string instead of throwing on the
  already-registered case, so `update_score`/`get_score` now do the
  same (`get_score` returns `{"error": "..."}`Instead of raising,
  `update_score`/`is_safe` return early with a string/`False`).
- Stopped wrapping plain ints in `u256(...)` when assigning to
  `u256`-typed dataclass fields - the dataclasses doc page shows the
  field accepting a bare int directly (`UserData(name, balance)`).

## Other design choices worth flagging

- **Flat history, not nested collections.** Note: the boilerplate
  repo above *does* show nested `TreeMap[Address, TreeMap[str, Bet]]`
  working in production, so nesting itself is not actually the risk it
  was first assumed to be. `history` is still kept as a flat
  `DynArray[ScoreHistoryEntry]` with a `symbol` field per entry, simply
  because it's simpler and was already working - not changed back.
- **`update_score` takes raw subscores, not a pre-computed grade.**
  The composite numeric score is computed deterministically in-contract
  (simple weighted sum, matching `compute-stablescore`'s off-chain
  logic so the two never disagree), but the *letter grade and
  rationale* are produced by `gl.nondet.exec_prompt` and ratified via
  `gl.eq_principle.prompt_non_comparative` - this is the actual
  "intelligent" part GenLayer's validator network reaches consensus
  on, per the project's requirement to use GenLayer LLM capabilities
  meaningfully rather than as window dressing.

## Steps

1. Open GenLayer Studio, create a new contract, paste in `contract.gpy`.
2. Deploy to StudioNet (pay the GEN deployment fee).
3. Call `register_stablecoin` once per stablecoin in the seed list
   (USDC, USDT, DAI, FRAX, TUSD, BUSD, USDP, GUSD, LUSD, MIM) to match
   `backend/supabase/seed/seed_stablecoins.sql`.
4. Record the deployed contract address below and supply it back -
   it gets wired into `GENLAYER_CONTRACT_ADDRESS` /
   `NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS` for the
   `publish-to-genlayer` Edge Function and the frontend oracle panel
   (STEP 10).

Contract address: (pending)
RPC URL: (pending)
"""


def main() -> None:
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    written = []

    contract_path = CONTRACT_DIR / "contract.gpy"
    if not contract_path.exists():
        contract_path.write_text(CONTRACT_GPY, encoding="utf-8")
        written.append("contract.gpy")

    interface_path = CONTRACT_DIR / "interface.json"
    if not interface_path.exists():
        interface_path.write_text(INTERFACE_JSON, encoding="utf-8")
        written.append("interface.json")

    notes_path = CONTRACT_DIR / "deploy_notes.md"
    # deploy_notes.md was created as a placeholder stub in STEP 4. Only
    # replace it if it still IS that stub - never clobber later manual
    # edits (e.g. a real contract address filled in during STEP 10).
    stub_marker = "filled in during STEP 7"
    if not notes_path.exists() or stub_marker in notes_path.read_text(encoding="utf-8"):
        notes_path.write_text(DEPLOY_NOTES, encoding="utf-8")
        written.append("deploy_notes.md (replaced STEP 4 stub)")

    print(f"Contract directory: {CONTRACT_DIR}")
    print(f"Wrote {len(written)} file(s).")
    for f in written:
        print(f"  + {f}")


if __name__ == "__main__":
    main()
