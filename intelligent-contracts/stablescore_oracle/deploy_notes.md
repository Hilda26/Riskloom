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

Contract address: `0xd2d06D078Ab781fEE5DAfE553fb0E4aA2EfcAfAb`
RPC URL: `https://studio.genlayer.com/api`
Chain: `studionet` (chain id 61999), confirmed via the `genlayer-js`
SDK's bundled chain definition.

## Post-deploy integration notes (STEP 10)

`getContractSchema(address)` against the live address above returns
all six methods with the exact param/return types from `contract.gpy`
- the contract is healthy. `get_score("USDC")` correctly returns
`{"error": "USDC is not registered"}` since no stablecoins have been
registered on-chain yet (separate from the Supabase seed data, which
is unaffected).

**Important correction:** the original `publish-to-genlayer` Edge
Function and `lib/genlayer/client.ts` called a hand-rolled JSON-RPC
body (`{"method": "gen_call", "params": [{"to", "function", "args"}]}`)
that does not match GenLayer's real wire format - it returned
`{"error": {"code": -32603, "message": "'type'"}}`. The actual,
documented integration path is the `genlayer-js` npm SDK
(`createClient`, `createAccount`, `client.readContract`,
`client.writeContract`, `client.waitForTransactionReceipt`), confirmed
by installing it locally and reading its real TypeScript type
declarations rather than guessing from prose docs. Both files were
rewritten to use the SDK. A fresh, unfunded service account
(`GENLAYER_PRIVATE_KEY` Edge Function secret) was generated for
`publish-to-genlayer` to sign `update_score` calls with - it has not
yet sent any transaction and may need StudioNet GEN before its first
write succeeds.

Still outstanding: call `register_stablecoin` for the 10 seed symbols
against the live contract (requires an explicit go-ahead - sending
on-chain write transactions is not something to do unprompted).
