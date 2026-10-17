// Chip In by Howlback: Stripe checkout, foster bank onboarding, and Stripe webhook.
// Deploy as one Supabase Edge Function named "chipin" with "Verify JWT" turned OFF
// (it checks foster sign-ins itself). Needs the secret STRIPE_SECRET_KEY.

const STRIPE = Deno.env.get("STRIPE_SECRET_KEY")!;
const SB = Deno.env.get("SUPABASE_URL")!;
function serviceKey() {
  const k = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (k) return k;
  try { const all = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") || "{}"); return all.default || Object.values(all)[0]; } catch (_) { return ""; }
}
const SERVICE = serviceKey() as string;
const svcHeaders = (): Record<string, string> => SERVICE.startsWith("sb_") ? { apikey: SERVICE } : { apikey: SERVICE, Authorization: "Bearer " + SERVICE };
const SITE = "https://howlback.app";
const FEE_FLAT = 100, FEE_MIN_PCT = 8, FEE_MAX_PCT = 50;

const cors = {
  "Access-Control-Allow-Origin": SITE,
  "Access-Control-Allow-Headers": "authorization, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const out = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

// ---- tiny Stripe + database helpers ----
function form(obj: Record<string, unknown>, prefix = "", f = new URLSearchParams()) {
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null) continue;
    const key = prefix ? `${prefix}[${k}]` : k;
    if (typeof v === "object") form(v as Record<string, unknown>, key, f);
    else f.append(key, String(v));
  }
  return f;
}
async function stripe(path: string, body?: Record<string, unknown>) {
  const r = await fetch("https://api.stripe.com/v1/" + path, {
    method: body ? "POST" : "GET",
    headers: { Authorization: "Bearer " + STRIPE, "Content-Type": "application/x-www-form-urlencoded" },
    body: body ? form(body) : undefined,
  });
  const j = await r.json();
  if (!r.ok) throw new Error("stripe: " + (j.error?.message || r.status));
  return j;
}
async function db(path: string, opts: RequestInit = {}) {
  const r = await fetch(SB + "/rest/v1/" + path, {
    ...opts,
    headers: { ...svcHeaders(), "Content-Type": "application/json", Prefer: "return=representation", ...(opts.headers || {}) },
  });
  const t = await r.text();
  if (!r.ok) throw new Error("db: " + t);
  return t ? JSON.parse(t) : null;
}
async function userFrom(req: Request) {
  const tok = (req.headers.get("authorization") || "").replace(/^Bearer /i, "");
  if (!tok) return null;
  const r = await fetch(SB + "/auth/v1/user", { headers: { apikey: SERVICE, Authorization: "Bearer " + tok } });
  return r.ok ? await r.json() : null;
}

// ---- supporter checkout ----
async function checkout(b: any) {
  const amt = Math.round(Number(b.amount_cents)), pct = Math.round(Number(b.fee_percent) * 100) / 100;
  if (!b.expense_id || !(amt >= 100) || !(pct >= FEE_MIN_PCT && pct <= FEE_MAX_PCT)) return out({ error: "bad request" }, 400);
  const [e] = await db(`expenses?id=eq.${encodeURIComponent(b.expense_id)}&select=*,dogs(id,name,status),fosters(status,stripe_account_id,payouts_ready)`);
  if (!e || e.status !== "approved" || e.dogs?.status !== "live" || e.fosters?.status !== "approved") return out({ error: "not available" }, 400);
  if (!e.fosters.stripe_account_id || !e.fosters.payouts_ready) return out({ error: "foster not ready for payouts" }, 400);
  const left = e.amount_cents - e.funded_cents;
  if (amt > left) return out({ error: "too much", left }, 400);
  const fee = FEE_FLAT + Math.round(amt * pct / 100);
  const [c] = await db("contributions", { method: "POST", body: JSON.stringify({
    expense_id: e.id, amount_cents: amt, fee_cents: fee, total_cents: amt + fee, fee_percent: pct,
    supporter_name: (b.name || "").toString().slice(0, 60) || null, supporter_note: (b.note || "").toString().slice(0, 200) || null }) });
  const back = `${SITE}/dogs/view/?id=${e.dogs.id}`;
  const s = await stripe("checkout/sessions", {
    mode: "payment",
    success_url: back + "&paid=1",
    cancel_url: back,
    submit_type: "pay",
    line_items: {
      0: { quantity: 1, price_data: { currency: "usd", unit_amount: amt,
        product_data: { name: `Chip in for ${e.dogs.name}`, description: `Toward a verified receipt from ${e.business_name}` } } },
      1: { quantity: 1, price_data: { currency: "usd", unit_amount: fee,
        product_data: { name: `Howlback fee ($1 + ${pct}%)` } } },
    },
    payment_intent_data: {
      application_fee_amount: fee,
      transfer_data: { destination: e.fosters.stripe_account_id },
      description: `Chip In for ${e.dogs.name}`,
      metadata: { contribution_id: c.id, expense_id: e.id },
    },
    metadata: { contribution_id: c.id, expense_id: e.id },
  });
  await db(`contributions?id=eq.${c.id}`, { method: "PATCH", body: JSON.stringify({ stripe_session_id: s.id }) });
  return out({ url: s.url });
}

// ---- foster: connect bank through Stripe ----
async function onboard(req: Request) {
  const u = await userFrom(req);
  if (!u) return out({ error: "sign in" }, 401);
  const [f] = await db(`fosters?id=eq.${u.id}&select=*`);
  if (!f || f.status !== "approved") return out({ error: "not approved yet" }, 403);
  let acct = f.stripe_account_id;
  if (!acct) {
    const a = await stripe("accounts", {
      type: "express", country: "US", email: u.email, business_type: "individual",
      capabilities: { transfers: { requested: true } },
      business_profile: { product_description: "Dog foster getting paid back for verified dog care costs through Howlback", url: SITE },
      metadata: { foster_id: f.id },
    });
    acct = a.id;
    await db(`fosters?id=eq.${f.id}`, { method: "PATCH", body: JSON.stringify({ stripe_account_id: acct }) });
  }
  const link = await stripe("account_links", {
    account: acct, type: "account_onboarding",
    refresh_url: `${SITE}/foster/?stripe=retry`, return_url: `${SITE}/foster/?stripe=done`,
  });
  return out({ url: link.url });
}

async function syncAccount(acctId: string) {
  const a = await stripe("accounts/" + acctId);
  const ready = a.capabilities?.transfers === "active" && !!a.payouts_enabled;
  await db(`fosters?stripe_account_id=eq.${acctId}`, { method: "PATCH", body: JSON.stringify({ payouts_ready: ready }) });
  return ready;
}
async function status(req: Request) {
  const u = await userFrom(req);
  if (!u) return out({ error: "sign in" }, 401);
  const [f] = await db(`fosters?id=eq.${u.id}&select=stripe_account_id`);
  if (!f?.stripe_account_id) return out({ ready: false });
  return out({ ready: await syncAccount(f.stripe_account_id) });
}

// ---- Stripe webhook: we re-fetch the event from Stripe, so fake calls can't mark anything paid ----
async function webhook(req: Request) {
  const body = await req.json().catch(() => null);
  if (!body?.id) return new Response("ok");
  const ev = await stripe("events/" + encodeURIComponent(body.id));
  if (ev.type === "checkout.session.completed" || ev.type === "checkout.session.async_payment_succeeded") {
    const s = ev.data.object;
    if (s.payment_status !== "paid") return new Response("ok");
    const id = s.metadata?.contribution_id;
    const [c] = id ? await db(`contributions?id=eq.${id}&select=*`) : [];
    if (c && c.status !== "paid" && c.stripe_session_id === s.id) {
      await db(`contributions?id=eq.${c.id}`, { method: "PATCH", body: JSON.stringify({ status: "paid", stripe_payment_intent: s.payment_intent }) });
      const [e] = await db(`expenses?id=eq.${c.expense_id}&select=funded_cents,paid_out_cents`);
      await db(`expenses?id=eq.${c.expense_id}`, { method: "PATCH", body: JSON.stringify({
        funded_cents: e.funded_cents + c.amount_cents, paid_out_cents: e.paid_out_cents + c.amount_cents }) });
    }
  } else if (ev.type === "checkout.session.expired") {
    const id = ev.data.object.metadata?.contribution_id;
    if (id) await db(`contributions?id=eq.${id}&status=eq.pending`, { method: "PATCH", body: JSON.stringify({ status: "failed" }) });
  } else if (ev.type === "account.updated") {
    await syncAccount(ev.data.object.id);
  }
  return new Response("ok");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    if (new URL(req.url).searchParams.has("webhook")) return await webhook(req);
    const b = await req.json().catch(() => ({}));
    if (b.action === "checkout") return await checkout(b);
    if (b.action === "onboard") return await onboard(req);
    if (b.action === "status") return await status(req);
    return out({ error: "unknown action" }, 400);
  } catch (err) {
    console.error(err);
    return out({ error: "server error" }, 500);
  }
});
