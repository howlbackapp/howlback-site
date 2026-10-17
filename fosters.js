// Howlback fosters: foster dashboard, public dog pages, chip-in checkout, admin review.
(() => {
const SB = "https://zgzrnlkffqkjtowziftk.supabase.co";
const KEY = "sb_publishable_2xvvHFjLuvY_z1ewBIdwPw_hzlMXIhQ";
const PAY_LIVE = false;            // flips to true once Stripe is connected
const FEE_FLAT = 100, FEE_MIN_PCT = 8;
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const money = c => "$" + (c / 100).toFixed(2).replace(/\.00$/, "");
const money2 = c => "$" + (c / 100).toFixed(2);
const pub = (b, p) => `${SB}/storage/v1/object/public/${b}/${p}`;
const CAT = {vet: "🩺 Vet visit", meds: "💊 Medication", food: "🥣 Food", supplies: "🛏️ Supplies", toys: "🧸 Toys", grooming: "🛁 Grooming", other: "📦 Other"};
const fee = (amt, pct) => FEE_FLAT + Math.round(amt * pct / 100);
const store = {get: k => { try { return localStorage.getItem(k); } catch (_) { return null; } },
  set: (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (_) {} }};

async function api(path, opts = {}, token) {
  const headers = Object.assign({apikey: KEY}, opts.headers || {});
  if (token) headers.Authorization = "Bearer " + token;
  const r = await fetch(SB + path, Object.assign({}, opts, {headers}));
  if (!r.ok) { const t = await r.text(); const e = new Error(t || r.statusText); e.status = r.status; throw e; }
  const ct = r.headers.get("content-type") || "";
  return ct.includes("json") ? r.json() : r.text();
}
const json = (method, body, extra) => ({method, headers: Object.assign({"Content-Type": "application/json", Prefer: "return=representation"}, extra || {}), body: JSON.stringify(body)});

async function shrink(file) {
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise((ok, bad) => { const i = new Image(); i.onload = () => ok(i); i.onerror = bad; i.src = url; });
    const s = Math.min(1, 1800 / Math.max(img.naturalWidth, img.naturalHeight));
    const c = document.createElement("canvas");
    c.width = Math.round(img.naturalWidth * s); c.height = Math.round(img.naturalHeight * s);
    c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
    return await new Promise(ok => c.toBlob(ok, "image/jpeg", 0.85));
  } finally { URL.revokeObjectURL(url); }
}
const bar = (got, need) => { const p = need ? Math.min(100, Math.round(got / need * 100)) : 0;
  return `<div class="fb-bar" role="progressbar" aria-valuenow="${p}" aria-valuemin="0" aria-valuemax="100"><span style="width:${p}%"></span></div>`; };

// ---------- sign-in session (fosters) ----------
const sess = {
  read() {
    const h = new URLSearchParams(location.hash.slice(1));
    if (h.get("access_token")) {
      store.set("fb_at", h.get("access_token")); store.set("fb_rt", h.get("refresh_token"));
      store.set("fb_exp", String(Date.now() + (+h.get("expires_in") || 3600) * 1000));
      history.replaceState(null, "", location.pathname + location.search);
    }
  },
  async token() {
    const at = store.get("fb_at"), rt = store.get("fb_rt"), exp = +store.get("fb_exp") || 0;
    if (!at) return null;
    if (Date.now() < exp - 60000) return at;
    if (!rt) return null;
    try {
      const r = await api("/auth/v1/token?grant_type=refresh_token", json("POST", {refresh_token: rt}));
      store.set("fb_at", r.access_token); store.set("fb_rt", r.refresh_token); store.set("fb_exp", String(Date.now() + r.expires_in * 1000));
      return r.access_token;
    } catch (_) { sess.clear(); return null; }
  },
  clear() { ["fb_at", "fb_rt", "fb_exp"].forEach(k => store.set(k, null)); },
  uid(t) { try { return JSON.parse(atob(t.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))).sub; } catch (_) { return null; } }
};

// ---------- foster dashboard ----------
const dash = $("#fb-dash");
if (dash) {
  sess.read();
  const show = id => dash.querySelectorAll("[data-step]").forEach(el => { el.hidden = el.dataset.step !== id; });
  const login = $("#fb-login");
  login.addEventListener("submit", async e => {
    e.preventDefault();
    const note = login.querySelector(".fb-note"), email = login.email.value.trim();
    if (!email) return;
    note.textContent = "Sending...";
    try {
      await api("/auth/v1/otp?redirect_to=" + encodeURIComponent(location.origin + "/foster/"), json("POST", {email, create_user: true}));
      note.textContent = `Check ${email} for your sign-in link. It works for 1 hour. Check spam too.`;
    } catch (err) { note.textContent = /rate/i.test(err.message) ? "Too many tries. Wait a few minutes and try again." : "Couldn’t send the link. Check your email and try again."; }
  });
  $("#fb-logout").addEventListener("click", () => { sess.clear(); location.reload(); });

  let T, uid, me, dogs = [], exps = [];
  async function load() {
    T = await sess.token();
    if (!T) { show("login"); return; }
    uid = sess.uid(T);
    try {
      [me] = await api(`/rest/v1/fosters?id=eq.${uid}&select=*`, {}, T);
      if (!me) { show("profile"); return; }
      dogs = await api(`/rest/v1/dogs?foster_id=eq.${uid}&select=*&order=created_at.desc`, {}, T);
      exps = await api(`/rest/v1/expenses?foster_id=eq.${uid}&select=*&order=created_at.desc`, {}, T);
      draw(); show("home");
    } catch (err) {
      if (err.status === 401) { sess.clear(); show("login"); return; }
      dash.insertAdjacentHTML("afterbegin", '<p class="fb-note">Couldn’t load your dashboard. Refresh to try again.</p>');
    }
  }

  const prof = $("#fb-profile");
  prof.addEventListener("submit", async e => {
    e.preventDefault();
    const note = prof.querySelector(".fb-note"), b = prof.querySelector("[type=submit]");
    if (!prof.agree.checked) { note.textContent = "Please agree to the terms to continue."; return; }
    b.disabled = true; note.textContent = "Saving...";
    try {
      await api("/rest/v1/fosters", json("POST", {id: uid, name: prof.name.value.trim(), city: prof.city.value,
        phone: prof.phone.value.trim() || null, about: prof.about.value.trim() || null}), T);
      load();
    } catch (err) { note.textContent = "Couldn’t save. Check your name and city and try again."; b.disabled = false; }
  });

  const ST = {pending: "Waiting for review", live: "Live", adopted: "Adopted 🎉", rejected: "Not approved", hidden: "Hidden", approved: "Verified ✓"};
  function draw() {
    $("#fb-hello").textContent = `Hi ${me.name.split(" ")[0]}!`;
    $("#fb-status").innerHTML = me.status === "approved"
      ? (me.payouts_ready ? '<span class="fb-ok">✓ Approved. Payouts are set up.</span>' : '<span class="fb-ok">✓ Approved.</span> Next: connect your bank so you can get paid back.')
      : me.status === "pending" ? "We’re reviewing your profile, usually within a day. You can add your dog and receipts now."
      : "Your profile wasn’t approved. Email hello@howlback.app with questions.";
    $("#fb-bank").hidden = me.status !== "approved" || me.payouts_ready;
    const raised = exps.reduce((s, x) => s + x.funded_cents, 0), owed = exps.reduce((s, x) => s + x.funded_cents - x.paid_out_cents, 0);
    $("#fb-totals").innerHTML = `<div><b>${money(raised)}</b><span>raised so far</span></div><div><b>${money(owed)}</b><span>on the way to you</span></div>`;
    const sel = $("#fb-receipt").dog_id;
    sel.innerHTML = dogs.map(d => `<option value="${d.id}">${esc(d.name)}</option>`).join("");
    $("#fb-receipt-box").hidden = !dogs.length;
    $("#fb-dogs").innerHTML = dogs.length ? dogs.map(d => {
      const ex = exps.filter(x => x.dog_id === d.id);
      return `<article class="fb-dog" data-dog="${d.id}">
        <img src="${pub("dogs", d.photo_path)}" alt="${esc(d.name)}">
        <div class="fb-dog-body">
          <h3>${esc(d.name)} <span class="fb-st ${d.status}">${ST[d.status]}</span></h3>
          <p class="muted">${esc([d.age, d.breed, d.city].filter(Boolean).join(" · "))}</p>
          ${d.status === "live" ? `<p><a href="/dogs/view/?id=${d.id}">See ${esc(d.name)}’s public page</a> · <button type="button" class="fb-link" data-adopt>Mark adopted</button></p>` : ""}
          <ul class="fb-exps">${ex.length ? ex.map(x => `<li><span>${CAT[x.category]} · ${esc(x.business_name)} · ${money2(x.amount_cents)}</span>
            <span class="fb-st ${x.status}">${ST[x.status]}</span>${x.status === "approved" ? bar(x.funded_cents, x.amount_cents) + `<small>${money(x.funded_cents)} of ${money(x.amount_cents)} covered</small>` : ""}
            ${x.status === "rejected" && x.review_note ? `<small>Note: ${esc(x.review_note)}</small>` : ""}</li>`).join("") : '<li class="muted">No receipts yet.</li>'}</ul>
        </div></article>`;
    }).join("") : '<p class="muted">No dogs yet. Add the dog you’re fostering below.</p>';
  }
  $("#fb-dogs").addEventListener("click", async e => {
    if (!e.target.closest("[data-adopt]")) return;
    const id = e.target.closest("[data-dog]").dataset.dog;
    if (!confirm("Mark this dog as adopted? Their page will say Adopted.")) return;
    await api(`/rest/v1/dogs?id=eq.${id}`, json("PATCH", {status: "adopted"}), T); load();
  });

  const dogF = $("#fb-dog");
  dogF.photo.addEventListener("change", () => { const f = dogF.photo.files[0]; $("#fb-dog-prev").innerHTML = f ? `<img src="${URL.createObjectURL(f)}" alt="">` : ""; });
  dogF.addEventListener("submit", async e => {
    e.preventDefault();
    const note = dogF.querySelector(".fb-note"), b = dogF.querySelector("[type=submit]"), f = dogF.photo.files[0];
    if (!f) { note.textContent = "Please add a photo."; return; }
    if (dogF.story.value.trim().length < 20) { note.textContent = "Tell people a little more about them (a couple sentences)."; return; }
    b.disabled = true; note.textContent = "Uploading photo...";
    try {
      const path = `${uid}/${crypto.randomUUID()}.jpg`;
      await api(`/storage/v1/object/dogs/${path}`, {method: "POST", headers: {"Content-Type": "image/jpeg"}, body: await shrink(f)}, T);
      await api("/rest/v1/dogs", json("POST", {foster_id: uid, name: dogF.name.value.trim(), sex: dogF.sex.value || null,
        age: dogF.age.value.trim() || null, breed: dogF.breed.value.trim() || null, city: dogF.city.value,
        story: dogF.story.value.trim(), photo_path: path}), T);
      dogF.reset(); $("#fb-dog-prev").innerHTML = ""; note.textContent = "Added! We’ll review their profile soon.";
      dogF.closest("details").open = false; load();
    } catch (err) { note.textContent = "Something went wrong. Check the photo (JPG or PNG under 8 MB) and try again."; }
    b.disabled = false;
  });

  const recF = $("#fb-receipt");
  recF.addEventListener("submit", async e => {
    e.preventDefault();
    const note = recF.querySelector(".fb-note"), b = recF.querySelector("[type=submit]"), f = recF.file.files[0];
    const amt = Math.round(parseFloat(recF.amount.value) * 100);
    if (!f) { note.textContent = "Please add a photo or PDF of the receipt."; return; }
    if (!(amt >= 100)) { note.textContent = "Enter the receipt total (at least $1)."; return; }
    b.disabled = true; note.textContent = "Uploading receipt...";
    try {
      const pdf = f.type === "application/pdf";
      const path = `${uid}/${crypto.randomUUID()}.${pdf ? "pdf" : "jpg"}`;
      await api(`/storage/v1/object/receipts/${path}`, {method: "POST", headers: {"Content-Type": pdf ? "application/pdf" : "image/jpeg"}, body: pdf ? f : await shrink(f)}, T);
      await api("/rest/v1/expenses", json("POST", {dog_id: recF.dog_id.value, foster_id: uid, category: recF.category.value,
        business_name: recF.business.value.trim(), amount_cents: amt, spent_on: recF.spent_on.value,
        note: recF.note.value.trim() || null, receipt_path: path}), T);
      recF.reset(); note.textContent = "Sent! We’ll check the receipt, then it goes live for supporters.";
      load();
    } catch (err) { note.textContent = "Something went wrong. Check the file (photo or PDF under 10 MB) and try again."; }
    b.disabled = false;
  });

  $("#fb-bank-btn").addEventListener("click", async () => {
    const note = $("#fb-bank .fb-note");
    if (!PAY_LIVE) { note.textContent = "Bank connection opens soon. We’ll email you when it’s ready."; return; }
    note.textContent = "Opening Stripe...";
    try { const r = await api("/functions/v1/connect-onboard", json("POST", {}), T); location.href = r.url; }
    catch (_) { note.textContent = "Couldn’t open Stripe. Try again in a minute."; }
  });
  load();
}

// ---------- public: browse dogs ----------
const grid = $("#fb-grid");
if (grid) {
  const city = $("#fb-city");
  let rows = [];
  const draw = () => {
    const c = city.value, r = rows.filter(d => !c || d.city === c);
    grid.innerHTML = r.length ? r.map(d => `
      <a class="fb-card" href="/dogs/view/?id=${d.id}">
        <img src="${pub("dogs", d.photo_path)}" alt="${esc(d.name)}, a foster dog in ${esc(d.city)}" loading="lazy">
        <div class="fb-card-body">
          ${d.status === "adopted" ? '<span class="fb-st adopted">Adopted 🎉</span>' : ""}
          <h3>${esc(d.name)}</h3>
          <p class="muted">${esc([d.age, d.city].filter(Boolean).join(" · "))} · Fostered by ${esc(d.foster_first_name)}</p>
          ${d.needed_cents ? bar(d.funded_cents, d.needed_cents) + `<p class="fb-raised"><b>${money(d.funded_cents)}</b> of ${money(d.needed_cents)} in verified receipts covered</p>` : '<p class="muted">No receipts yet</p>'}
        </div></a>`).join("") : `<p class="muted">No dogs${c ? " in " + esc(c) : ""} yet. Fosters are joining now.</p>`;
  };
  city.addEventListener("change", draw);
  api("/rest/v1/dogs_public?select=*&order=created_at.desc&limit=200")
    .then(r => { rows = r.sort((a, b) => (a.status === "adopted") - (b.status === "adopted")); draw(); })
    .catch(() => { grid.innerHTML = '<p class="muted">Couldn’t load dogs. Try again in a minute.</p>'; });
}

// ---------- public: one dog + chip in ----------
const view = $("#fb-view");
if (view) {
  const id = new URLSearchParams(location.search).get("id");
  const dlg = $("#fb-chip");
  let dog, exps = [], cur;
  (async () => {
    try {
      [dog] = await api(`/rest/v1/dogs_public?id=eq.${encodeURIComponent(id)}&select=*`);
      if (!dog) throw 0;
      exps = await api(`/rest/v1/expenses_public?dog_id=eq.${dog.id}&select=*&order=spent_on.desc`);
      const sup = await api(`/rest/v1/contributions_public?dog_id=eq.${dog.id}&select=*&order=created_at.desc&limit=30`);
      document.title = `Help ${dog.name} | Howlback`;
      const open = exps.filter(x => x.funded_cents < x.amount_cents);
      view.innerHTML = `
        <div class="fb-hero"><img src="${pub("dogs", dog.photo_path)}" alt="${esc(dog.name)}">
          <div><span class="fb-st ${dog.status}">${dog.status === "adopted" ? "Adopted 🎉" : "In foster care"}</span>
          <h1>${esc(dog.name)}</h1>
          <p class="muted">${esc([{male: "Boy", female: "Girl"}[dog.sex], dog.age, dog.breed, dog.city].filter(Boolean).join(" · "))}</p>
          <p>Fostered by <b>${esc(dog.foster_first_name)}</b></p>
          ${dog.needed_cents ? bar(dog.funded_cents, dog.needed_cents) + `<p class="fb-raised"><b>${money(dog.funded_cents)}</b> of ${money(dog.needed_cents)} covered</p>` : ""}
          ${open.length ? `<a class="btn" href="#fb-needs">Help cover ${esc(dog.name)}’s bills</a>` : ""}
          <button class="btn soft" type="button" id="fb-share">Share ${esc(dog.name)}</button></div></div>
        <div class="fb-story"><h2>${esc(dog.name)}’s story</h2><p>${esc(dog.story).replace(/\n/g, "<br>")}</p></div>
        <div id="fb-needs"><h2>Verified receipts</h2>
          <p class="muted">Every receipt is checked by Howlback before it shows here. The money goes to ${esc(dog.foster_first_name)} to pay them back.</p>
          ${exps.length ? `<ul class="fb-needs">${exps.map(x => `<li>
            <div class="fb-need-top"><span>${CAT[x.category]}</span><span class="fb-ver">✓ Verified receipt</span></div>
            <p class="fb-biz"><b>${esc(x.business_name)}</b><span class="muted">${new Date(x.spent_on + "T12:00").toLocaleDateString("en-US", {month: "short", day: "numeric", year: "numeric"})}</span></p>
            ${x.note ? `<p class="muted">${esc(x.note)}</p>` : ""}
            ${bar(x.funded_cents, x.amount_cents)}
            <p class="fb-raised"><b>${money(x.funded_cents)}</b> of ${money2(x.amount_cents)}</p>
            ${x.funded_cents < x.amount_cents ? `<button class="btn" type="button" data-chip="${x.id}">Chip in</button>` : '<span class="fb-ok">Fully covered 🎉</span>'}
          </li>`).join("")}</ul>` : '<p class="muted">No receipts yet.</p>'}
        </div>
        ${sup.length ? `<div class="fb-sup"><h2>Supporters</h2><ul>${sup.map(s => `<li><b>${esc(s.supporter_name)}</b> covered ${money(s.amount_cents)}${s.supporter_note ? `: “${esc(s.supporter_note)}”` : ""}</li>`).join("")}</ul></div>` : ""}`;
      $("#fb-share").addEventListener("click", async () => {
        const data = {title: `Help ${dog.name}`, text: `${dog.name} is in foster care in ${dog.city}. Help cover their verified vet and care bills on Howlback.`, url: location.href};
        try { if (navigator.share) await navigator.share(data); else { await navigator.clipboard.writeText(location.href); $("#fb-share").textContent = "Link copied!"; } } catch (_) {}
      });
    } catch (_) { view.innerHTML = '<p class="muted">We couldn’t find that dog. <a href="/dogs/">See all dogs</a>.</p>'; }
  })();

  const f = dlg.querySelector("form");
  const amtIn = f.amount, pctIn = f.pct;
  const left = () => cur.amount_cents - cur.funded_cents;
  function calc() {
    const a = Math.round(parseFloat(amtIn.value || "0") * 100), p = Math.max(FEE_MIN_PCT, parseFloat(pctIn.value || FEE_MIN_PCT));
    const fe = a ? fee(a, p) : 0, ok = a >= 100 && a <= left();
    $("#fb-sum").innerHTML = a ? `<div><span>To ${esc(dog.name)}’s ${esc(cur.business_name)} bill</span><b>${money2(a)}</b></div>
      <div><span>Howlback fee ($1 + ${p}%)</span><b>${money2(fe)}</b></div>
      <div class="fb-total"><span>Total</span><b>${money2(a + fe)}</b></div>` : "";
    f.querySelector("[type=submit]").disabled = !ok;
    $("#fb-chip-note").textContent = a && a > left() ? `This bill only needs ${money2(left())} more.` : a && a < 100 ? "The smallest chip-in is $1." : "";
    return {a, p, fe, ok};
  }
  view.addEventListener("click", e => {
    const b = e.target.closest("[data-chip]"); if (!b) return;
    cur = exps.find(x => x.id === b.dataset.chip);
    $("#fb-chip-title").textContent = `Chip in for ${dog.name}`;
    $("#fb-chip-sub").textContent = `${CAT[cur.category]} at ${cur.business_name}. ${money2(left())} still needed.`;
    f.reset(); f.querySelectorAll("[data-amt]").forEach(x => x.classList.remove("on"));
    f.querySelector('[data-amt="rest"]').textContent = `All of it (${money(left())})`;
    f.querySelectorAll("[data-pct]").forEach(x => x.classList.toggle("on", x.dataset.pct === "8"));
    pctIn.value = 8; pctIn.closest("label").hidden = true; calc(); dlg.showModal();
  });
  f.addEventListener("click", e => {
    const a = e.target.closest("[data-amt]"), p = e.target.closest("[data-pct]");
    if (a) { f.querySelectorAll("[data-amt]").forEach(x => x.classList.toggle("on", x === a));
      amtIn.value = a.dataset.amt === "rest" ? (left() / 100).toFixed(2) : Math.min(+a.dataset.amt, left() / 100); calc(); }
    if (p) { f.querySelectorAll("[data-pct]").forEach(x => x.classList.toggle("on", x === p));
      pctIn.closest("label").hidden = p.dataset.pct !== "custom"; if (p.dataset.pct !== "custom") pctIn.value = p.dataset.pct; else { pctIn.value = 20; pctIn.focus(); } calc(); }
  });
  amtIn.addEventListener("input", () => { f.querySelectorAll("[data-amt]").forEach(x => x.classList.remove("on")); calc(); });
  pctIn.addEventListener("input", calc);
  pctIn.addEventListener("change", () => { if (+pctIn.value < FEE_MIN_PCT) pctIn.value = FEE_MIN_PCT; calc(); });
  dlg.querySelector("[data-close]").addEventListener("click", () => dlg.close());
  f.addEventListener("submit", async e => {
    e.preventDefault();
    const {a, p, ok} = calc(); if (!ok) return;
    const note = $("#fb-chip-note"), b = f.querySelector("[type=submit]");
    if (!PAY_LIVE) { note.textContent = "Chip-ins open very soon! We’re finishing secure checkout. Share this page in the meantime 🧡"; return; }
    b.disabled = true; note.textContent = "Opening secure checkout...";
    try {
      const r = await api("/functions/v1/checkout", json("POST", {expense_id: cur.id, amount_cents: a, fee_percent: p,
        name: f.sname.value.trim() || null, note: f.snote.value.trim() || null}));
      location.href = r.url;
    } catch (_) { note.textContent = "Couldn’t open checkout. Try again in a minute."; b.disabled = false; }
  });
}

// ---------- admin: fosters, dogs, receipts ----------
const adm = $("#fb-admin");
if (adm) {
  const token = () => sessionStorage.getItem("lf_token");
  const load = async () => {
    if (!token()) return;
    try {
      const [fos, dg, ex] = await Promise.all([
        api("/rest/v1/fosters?status=eq.pending&select=*&order=created_at", {}, token()),
        api("/rest/v1/dogs?status=eq.pending&select=*,fosters(name,status)&order=created_at", {}, token()),
        api("/rest/v1/expenses?status=eq.pending&select=*,dogs(name),fosters(name)&order=created_at", {}, token())]);
      adm.hidden = false;
      $("#fb-a-count").textContent = fos.length + dg.length + ex.length;
      $("#fb-a-fosters").innerHTML = fos.length ? fos.map(x => `<div class="fb-a" data-t="fosters" data-id="${x.id}">
        <b>${esc(x.name)}</b> · ${esc(x.city)} · ${esc(x.phone || "no phone")}<p>${esc(x.about || "")}</p>
        <button class="btn" data-ok="approved">Approve foster</button> <button class="btn soft" data-ok="rejected">Reject</button></div>`).join("") : '<p class="muted">None waiting.</p>';
      $("#fb-a-dogs").innerHTML = dg.length ? dg.map(x => `<div class="fb-a" data-t="dogs" data-id="${x.id}">
        <img src="${pub("dogs", x.photo_path)}" alt=""><div><b>${esc(x.name)}</b> · ${esc(x.city)} · foster: ${esc(x.fosters?.name)} (${esc(x.fosters?.status)})
        <p>${esc(x.story)}</p><button class="btn" data-ok="live">Approve dog</button> <button class="btn soft" data-ok="rejected">Reject</button></div></div>`).join("") : '<p class="muted">None waiting.</p>';
      $("#fb-a-receipts").innerHTML = ex.length ? ex.map(x => `<div class="fb-a" data-t="expenses" data-id="${x.id}" data-path="${esc(x.receipt_path)}">
        <b>${money2(x.amount_cents)}</b> · ${CAT[x.category]} · ${esc(x.business_name)} · ${esc(x.spent_on)}<br>
        For <b>${esc(x.dogs?.name)}</b>, foster ${esc(x.fosters?.name)}${x.note ? `<p>${esc(x.note)}</p>` : ""}
        <p><button class="btn soft" data-view>Open receipt</button></p>
        <p class="muted">Check: real business, date, total matches, it’s for a dog.</p>
        <button class="btn" data-ok="approved">Verify receipt</button> <button class="btn soft" data-ok="rejected">Reject</button></div>`).join("") : '<p class="muted">None waiting.</p>';
    } catch (_) {}
  };
  adm.addEventListener("click", async e => {
    const row = e.target.closest("[data-id]"); if (!row) return;
    if (e.target.closest("[data-view]")) {
      const w = window.open("", "_blank");
      try { const r = await api(`/storage/v1/object/sign/receipts/${row.dataset.path}`, json("POST", {expiresIn: 600}), token());
        w.location = SB + "/storage/v1" + r.signedURL; } catch (_) { w.close(); alert("Couldn’t open the receipt."); }
      return;
    }
    const ok = e.target.closest("[data-ok]"); if (!ok) return;
    const body = {status: ok.dataset.ok, reviewed_at: new Date().toISOString()};
    if (row.dataset.t === "expenses" && ok.dataset.ok === "rejected") { const n = prompt("Short note for the foster (why it wasn’t verified):", ""); if (n === null) return; body.review_note = n.slice(0, 300); }
    ok.disabled = true;
    await api(`/rest/v1/${row.dataset.t}?id=eq.${row.dataset.id}`, json("PATCH", body, {Prefer: "return=minimal"}), token());
    load();
  });
  load();
}
})();
