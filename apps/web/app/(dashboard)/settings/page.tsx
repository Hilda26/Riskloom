import { createClient } from "@/lib/supabase/server";

export const revalidate = 0;

export default async function SettingsPage() {
  const supabase = await createClient();
  const { data: userData } = await supabase.auth.getUser();
  const user = userData?.user;

  let profile = null;
  if (user) {
    const { data } = await supabase
      .from("profiles")
      .select("*, wallets(address)")
      .eq("id", user.id)
      .maybeSingle();
    profile = data;
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "https://<project>.supabase.co";

  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">Settings</div>
          <div className="dm-sub">Account &amp; API access</div>
        </div>
      </div>
      <div className="kpi k1" style={{ maxWidth: "480px" }}>
        <div className="klbl">Connected Wallet</div>
        <div className="knum" style={{ fontSize: "1rem", fontFamily: "var(--mono)" }}>
          {profile?.wallets?.address ?? "Not linked yet"}
        </div>
        <div className="ktrend">Tier: {profile?.tier ?? "free"}</div>
      </div>

      <div className="oracle-lbl" style={{ marginTop: "2rem" }}>Risk Intelligence API</div>
      <p style={{ color: "var(--text2)", marginTop: ".5rem", maxWidth: "560px" }}>
        Live, API-key-gated REST endpoints for exchanges, fintechs, wallets, and
        institutions to consume StableScore&trade; ratings directly. Keys are
        provisioned against the <code>api_keys</code> table with scoped access
        (<code>read:scores</code>, <code>read:history</code>); pass yours in the
        <code> x-api-key</code> header.
      </p>
      <div className="code-block" style={{ marginTop: "1rem", maxWidth: "640px" }}>
        {`# Current StableScore ratings (all coins, or ?symbol=USDC)
curl -H "x-api-key: <YOUR_KEY>" \\
  ${supabaseUrl}/functions/v1/api-v1-scores

# Rating history for one stablecoin
curl -H "x-api-key: <YOUR_KEY>" \\
  ${supabaseUrl}/functions/v1/api-v1-history?symbol=USDC`}
      </div>
    </>
  );
}
