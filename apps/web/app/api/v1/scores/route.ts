// Thin proxy to the api-v1-scores Supabase Edge Function, so external
// consumers can hit a stable first-party domain instead of the
// Supabase functions URL directly.
export async function GET(request: Request) {
  const url = new URL(request.url);
  const target = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1/api-v1-scores${url.search}`;

  const res = await fetch(target, {
    headers: { "x-api-key": request.headers.get("x-api-key") ?? "" },
  });
  const body = await res.text();

  return new Response(body, {
    status: res.status,
    headers: { "Content-Type": "application/json" },
  });
}
