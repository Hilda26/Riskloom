// Read-only verification of the deployed StableScoreOracle on StudioNet.
// Usage: deno run -A scripts/verify_genlayer.ts 0x<address>
import { createClient } from "npm:genlayer-js@1.1.8";
import { studionet } from "npm:genlayer-js@1.1.8/chains";

const address = (Deno.args[0] ?? "").trim() as `0x${string}`;
if (!address) {
  console.error("usage: deno run -A scripts/verify_genlayer.ts 0x<address>");
  Deno.exit(1);
}

const client = createClient({
  chain: studionet,
  endpoint: "https://studio.genlayer.com/api",
});

const SYMBOLS = ["USDC", "USDT", "DAI", "FRAX", "TUSD", "BUSD", "USDP", "GUSD", "LUSD", "MIM"];

console.log(`Contract: ${address}`);
console.log(`Endpoint: https://studio.genlayer.com/api\n`);

// 1. list_stablecoins - what's registered on-chain
try {
  const listed = await client.readContract({
    address,
    functionName: "list_stablecoins",
    args: [],
  });
  console.log("list_stablecoins() ->", listed);
} catch (e) {
  console.log("list_stablecoins() FAILED ->", String(e));
}

console.log("\nper-symbol get_score():");
for (const sym of SYMBOLS) {
  try {
    const score = await client.readContract({
      address,
      functionName: "get_score",
      args: [sym],
    });
    console.log(`  ${sym.padEnd(5)} ->`, JSON.stringify(score));
  } catch (e) {
    console.log(`  ${sym.padEnd(5)} -> ERROR`, String(e));
  }
}
