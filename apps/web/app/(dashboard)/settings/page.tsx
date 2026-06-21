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
      <p style={{ color: "var(--text2)", marginTop: "1.5rem", maxWidth: "540px" }}>
        API key issuance for the Risk Intelligence API (exchanges, fintechs,
        institutions) is managed server-side via the api_keys table. Self-serve
        key generation UI ships alongside the billing/business-model work.
      </p>
    </>
  );
}
