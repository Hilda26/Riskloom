// siwe-verify: verifies a signed SIWE message, links the wallet to a
// Supabase auth identity, and returns a session.
import { createClient } from "npm:@supabase/supabase-js@2";
import { SiweMessage } from "npm:siwe@2";
import { corsHeaders } from "../_shared/cors.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { message, signature } = await req.json();
    if (!message || !signature) {
      return new Response(
        JSON.stringify({ error: "message and signature are required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    const siwe = new SiweMessage(message);
    const { data: fields } = await siwe.verify({ signature });
    const address = fields.address.toLowerCase();

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    // Nonce must exist, be unconsumed, and unexpired
    const { data: nonceRow, error: nonceErr } = await supabase
      .from("siwe_nonces")
      .select("*")
      .eq("address", address)
      .eq("nonce", fields.nonce)
      .is("consumed_at", null)
      .gt("expires_at", new Date().toISOString())
      .single();

    if (nonceErr || !nonceRow) {
      throw new Error("invalid or expired nonce");
    }

    await supabase
      .from("siwe_nonces")
      .update({ consumed_at: new Date().toISOString() })
      .eq("id", nonceRow.id);

    // Upsert wallet
    const { data: wallet, error: walletErr } = await supabase
      .from("wallets")
      .upsert(
        { address, chain_id: fields.chainId, last_login_at: new Date().toISOString() },
        { onConflict: "address" },
      )
      .select()
      .single();
    if (walletErr) throw walletErr;

    // Find or create the auth user + profile bound to this wallet
    const email = `${address}@wallet.stableshield.local`;
    let userId: string;

    const { data: existing } = await supabase
      .from("profiles")
      .select("id")
      .eq("wallet_id", wallet.id)
      .maybeSingle();

    if (existing) {
      userId = existing.id;
    } else {
      const { data: created, error: createErr } =
        await supabase.auth.admin.createUser({
          email,
          email_confirm: true,
          user_metadata: { wallet_address: address },
        });
      if (createErr) throw createErr;
      userId = created.user.id;

      const { error: profileErr } = await supabase.from("profiles").insert({
        id: userId,
        wallet_id: wallet.id,
      });
      if (profileErr) throw profileErr;
    }

    const { data: link, error: linkErr } =
      await supabase.auth.admin.generateLink({
        type: "magiclink",
        email,
      });
    if (linkErr) throw linkErr;

    // Return the bare hashed_token instead of properties.action_link.
    // action_link points at GoTrue's own hosted /auth/v1/verify
    // endpoint on the *Supabase* domain, which then 302-redirects to
    // the project's Site URL with the session in a URL hash fragment -
    // that depends on Site URL being correctly configured AND on some
    // page reading window.location.hash, neither of which our
    // /auth/callback route (which expects ?token_hash=&type= query
    // params per Supabase's documented SSR/PKCE pattern) does. Using
    // hashed_token directly with our own same-origin /auth/callback
    // keeps the whole redirect on whatever domain the user is
    // actually on, independent of the Site URL setting.
    return new Response(
      JSON.stringify({
        address,
        userId,
        tokenHash: link.properties.hashed_token,
        type: "magiclink",
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 401,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
