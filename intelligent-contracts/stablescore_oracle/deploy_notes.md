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
rewritten to use the SDK. A fresh service account
(`GENLAYER_PRIVATE_KEY` Edge Function secret,
`0x34998AAE8D4c59A8816B11D28E9a20ca8B979577`) was generated for
`publish-to-genlayer` to sign `update_score` calls with -
**StudioNet did not require any GEN funding**, write transactions
succeeded from a 0-balance account.

All 10 seed stablecoins (USDC, USDT, DAI, FRAX, TUSD, BUSD, USDP,
GUSD, LUSD, MIM) were registered on-chain via `register_stablecoin`.

## Second bug, found from a real transaction trace

The first live `update_score` call (via `publish-to-genlayer`, for
USDC) returned `{"status":"confirmed", "rating":"AAA"}` from our Edge
Function, but reading the contract back afterward showed the score
had **not** actually been written (`rating: "D"`, `updated_at:
"never"`). Pulling the full transaction receipt
(`client.waitForTransactionReceipt`) showed `status_name: "FINALIZED"`
but every validator's `genvm_result` had `execution_result: "ERROR"`:

```
File "/contract.py", line 127, in update_score
    decision = json.loads(raw)
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

The receipt's `eq_outputs` field showed GenVM's non-comparative
equivalence judging had already correctly determined the answer was
`"AAA"` - as a bare value, not our `json.dumps({"rating":...,
"reason":...})` wrapper. `gl.eq_principle.prompt_non_comparative`
does not transparently pass through whatever `assess()` returns; it
re-derives a judged result against `task`/`criteria`, and that result
came back as a plain string, not our JSON envelope. `raw` ended up
empty, and `json.loads("")` is exactly the observed error.

**Fix:** stopped wrapping the LLM's answer in JSON entirely.
`assess()` now returns the bare rating string (using
`gl.nondet.exec_prompt(prompt)` - the plain-text overload, not
`response_format="json"`), and `reason` is now just the deterministic
`evidence_summary` string instead of separately asking the LLM for
free-text rationale. The grade itself is still entirely LLM-derived
and validator-judged via `gl.eq_principle.prompt_non_comparative` -
only the brittle JSON round-trip was removed.

**This requires a redeploy.** GenLayer contracts are immutable once
deployed, so the corrected `contract.gpy` needs a fresh deployment to
a new address, the 10 stablecoins re-registered against it, and the
new address re-wired into `GENLAYER_CONTRACT_ADDRESS` /
`NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS` everywhere.

Contract address (bug #1, do not reuse): `0xd2d06D078Ab781fEE5DAfE553fb0E4aA2EfcAfAb`

## Third bug, also found from a real transaction trace

After redeploying the bug #1 fix to a new address
(`0x6022967eD041daEc68Fe96121900F627DaDa7618`) and re-registering all
10 stablecoins, the leader's `execution_result` finally showed
`SUCCESS` - but the overall transaction `result_name` was
`NO_MAJORITY`. The full receipt showed `last_round.validator_votes_name:
["DISAGREE","DISAGREE","IDLE","DISAGREE","AGREE"]` after exhausting
all 3 leader rotations.

Root cause: each of GenLayer's 5 StudioNet validators runs a
*different* underlying LLM (seen in the receipt's
`node_config.primary_model`: DeepSeek, Gemini, Grok, GPT, GLM).
`gl.eq_principle.prompt_non_comparative` was being used to ask each
validator's model to independently pick 1-of-8 categorical letter
grades from the same five raw numbers - and different LLMs simply
don't reliably converge on a discrete classification like that,
especially near grade boundaries. This is a real protocol-level
consensus failure, not a code bug in the narrow sense - the wrong
*task* was being delegated to multi-model LLM consensus.

**Fix:** the letter grade is now computed **deterministically** in
`update_score`, using the exact same weighted formula and grade
boundaries as the off-chain `compute-stablescore` Edge Function
(`backend/supabase/functions/_shared/scoring.ts`) - guaranteeing
on-chain and off-chain never disagree, and guaranteeing every
validator computes the identical result (zero chance of
`NO_MAJORITY` on the grade itself, since classifying a number into a
band is arithmetic, not a judgment call). The LLM/`prompt_non_comparative`
call is still genuinely used, just for something that naturally
converges across different models: a narrow yes/no question ("does
the evidence text mention an explicit red flag the numeric score
wouldn't capture") that can downgrade the deterministic grade by one
notch. This keeps the contract's LLM-backed consensus step meaningful
(it can actually change the outcome) while removing the failure mode
that caused `NO_MAJORITY`.

**This requires another redeploy** for the same reason as bug #1 -
contracts are immutable.

Contract address (bug #2, do not reuse): `0x6022967eD041daEc68Fe96121900F627DaDa7618`

## Status

All 10 seed stablecoins were registered against both prior (buggy)
addresses as part of debugging - neither should be used going
forward. Once the bug #3 fix is deployed to a new address: re-register
the 10 symbols, re-wire `GENLAYER_CONTRACT_ADDRESS` /
`NEXT_PUBLIC_GENLAYER_CONTRACT_ADDRESS` (Supabase secret + Vercel env
var, already updated twice this session via CLI/API, not the
dashboard), and re-verify with a real `publish-to-genlayer` call
followed by reading `get_score`/`get_history` back to confirm the
write actually landed - confirming `status: "confirmed"` from the
Edge Function alone was not sufficient evidence in either prior
attempt.
