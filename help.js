// Howlback help board: rides and supplies. Board, ask form, done link, and admin.
(() => {
const SB = "https://zgzrnlkffqkjtowziftk.supabase.co";
const KEY = "sb_publishable_2xvvHFjLuvY_z1ewBIdwPw_hzlMXIhQ";
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmtDate = d => d ? new Date(d + (d.length === 10 ? "T12:00:00" : "")).toLocaleDateString("en-US", {month: "short", day: "numeric"}) : "";
const $ = s => document.querySelector(s);
const KIND = {ride: ["🚗", "Ride"], supplies: ["📦", "Supplies"], other: ["🤝", "Other"]};
const JSONH = {"Content-Type": "application/json", Prefer: "return=minimal"};

async function api(path, opts = {}, token) {
  const headers = Object.assign({apikey: KEY}, opts.headers || {});
  if (token) headers.Authorization = "Bearer " + token;
  const r = await fetch(SB + path, Object.assign({}, opts, {headers}));
  if (!r.ok) { const t = await r.text(); const e = new Error(t || r.statusText); e.status = r.status; throw e; }
  const ct = r.headers.get("content-type") || "";
  return ct.includes("json") ? r.json() : r.text();
}
const tag = k => `<span class="hb-tag ${k}">${KIND[k][0]} ${KIND[k][1]}</span>`;

// ---------- public board ----------
const list = $("#hb-list");
if (list) {
  let rows = [], kind = "all";
  const city = $("#hb-city");
  const draw = () => {
    const c = city.value;
    const r = rows.filter(p => (kind === "all" || p.kind === kind) && (!c || p.city === c));
    if (!r.length) { list.innerHTML = `<p class="muted lf-empty">No ${kind === "all" ? "" : KIND[kind][1].toLowerCase() + " "}requests${c ? " in " + esc(c) : ""} right now. <a href="/help-board/ask/">Ask for help</a></p>`; return; }
    list.innerHTML = r.map(p => `
      <article class="hb-card${p.status === "done" ? " done" : ""}">
        <div class="hb-top">${p.status === "done" ? '<span class="hb-tag done">✓ Covered, thank you!</span>' : tag(p.kind)}<span class="hb-where">${esc(p.city)}${p.needed_by ? " · by " + fmtDate(p.needed_by) : ""}</span></div>
        <h3>${esc(p.title)}</h3>
        <p>${esc(p.details)}</p>
        ${p.status === "done" ? "" : `<div class="lf-act"><button class="btn" type="button" data-offer="${p.id}">I can help</button>${p.phone ? `<a class="btn soft" href="tel:${esc(p.phone.replace(/[^0-9+]/g, ""))}">Call ${esc(p.phone)}</a>` : ""}</div>`}
      </article>`).join("");
  };
  document.querySelectorAll("[data-hkind]").forEach(b => b.addEventListener("click", () => {
    kind = b.dataset.hkind;
    document.querySelectorAll("[data-hkind]").forEach(x => x.setAttribute("aria-selected", x === b));
    draw();
  }));
  city.addEventListener("change", draw);
  api("/rest/v1/help_public?select=*&order=created_at.desc&limit=300")
    .then(r => { rows = r; draw(); })
    .catch(() => { rows = []; draw(); });

  const dlg = $("#hb-offer");
  list.addEventListener("click", e => {
    const b = e.target.closest("[data-offer]"); if (!b) return;
    const p = rows.find(x => x.id === b.dataset.offer);
    dlg.querySelector("[name=request_id]").value = b.dataset.offer;
    dlg.querySelector(".hb-what").textContent = p ? p.title : "";
    dlg.querySelector(".lf-note").textContent = "";
    dlg.showModal();
  });
  dlg.querySelector("[data-close]").addEventListener("click", () => dlg.close());
  dlg.querySelector("form").addEventListener("submit", async e => {
    e.preventDefault();
    const f = e.target, note = f.querySelector(".lf-note"), btn = f.querySelector("button[type=submit]");
    if (f.website.value) return;
    btn.disabled = true; note.textContent = "Sending...";
    try {
      await api("/rest/v1/help_offers", {method: "POST", headers: JSONH,
        body: JSON.stringify({request_id: f.request_id.value, from_name: f.from_name.value.trim() || null, from_contact: f.from_contact.value.trim(), message: f.message.value.trim()})});
      note.textContent = "Sent! Thank you 🧡 We’ll pass your info to them.";
      f.reset(); setTimeout(() => dlg.close(), 1800);
    } catch (err) { note.textContent = "That didn’t send. Add your phone or email and a short message, then try again."; }
    btn.disabled = false;
  });
}

// ---------- ask form ----------
const form = $("#hb-form");
if (form) {
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const note = $("#hb-status"), btn = form.querySelector("button[type=submit]");
    if (form.website.value) return;
    const phone = form.contact_phone.value.trim(), email = form.contact_email.value.trim();
    if (!form.querySelector("[name=kind]:checked")) { note.textContent = "Pick what you need: a ride, supplies, or other."; return; }
    if (!form.city.value) { note.textContent = "Please choose a city."; return; }
    if (form.title.value.trim().length < 5) { note.textContent = "Add a short title, like “Ride to Harlingen vet Saturday.”"; return; }
    if (form.details.value.trim().length < 10) { note.textContent = "Add a few more details so people know how to help."; return; }
    if (!phone && !email) { note.textContent = "Please add a phone number or email so helpers can reach you."; return; }
    btn.disabled = true; note.textContent = "Sending...";
    const id = crypto.randomUUID(), tok = crypto.randomUUID();
    try {
      await api("/rest/v1/help_requests", {method: "POST", headers: JSONH, body: JSON.stringify({
        id, edit_token: tok, kind: form.querySelector("[name=kind]:checked").value, city: form.city.value,
        title: form.title.value.trim(), details: form.details.value.trim(), needed_by: form.needed_by.value || null,
        contact_name: form.contact_name.value.trim() || null, contact_phone: phone || null, contact_email: email || null,
        show_phone: !!(phone && form.show_phone.checked)})});
      $("#hb-link").value = `${location.origin}/help-board/update/?id=${id}&t=${tok}`;
      form.hidden = true; $("#hb-done").hidden = false; window.scrollTo(0, 0);
    } catch (err) { note.textContent = "Something went wrong. Check the form and try again."; btn.disabled = false; }
  });
}
const copy = $("#hb-copy-link");
if (copy) copy.addEventListener("click", async () => {
  try { await navigator.clipboard.writeText($("#hb-link").value); copy.textContent = "Copied!"; } catch (_) { $("#hb-link").select(); }
});

// ---------- poster marks it covered ----------
const upd = $("#hb-update");
if (upd) {
  const q = new URLSearchParams(location.search), note = $("#hb-upd-note"), b = $("#hb-mark");
  if (!q.get("id") || !q.get("t")) { b.hidden = true; note.textContent = "This link is missing some info. Use the full link you saved after posting."; }
  b.addEventListener("click", async () => {
    b.disabled = true; note.textContent = "Updating...";
    try {
      const ok = await api("/rest/v1/rpc/help_mark_done", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({p_id: q.get("id"), p_token: q.get("t")})});
      if (ok === true) { b.hidden = true; note.textContent = "🎉 So glad you got help! Your request now says Covered for 2 days, then it comes down."; }
      else { note.textContent = "We couldn’t find that request. It may already be marked covered."; b.disabled = false; }
    } catch (e) { note.textContent = "Something went wrong. Try again in a minute."; b.disabled = false; }
  });
}

// ---------- admin (uses the same login as lost & found) ----------
const box = $("#hb-admin");
if (box) {
  const token = () => sessionStorage.getItem("lf_token");
  const card = p => `
    <article class="hb-card" data-hid="${p.id}">
      <div class="hb-top">${tag(p.kind)}<span class="hb-where">${esc(p.city)}${p.needed_by ? " · by " + fmtDate(p.needed_by) : ""} · ${new Date(p.created_at).toLocaleString()}</span></div>
      <h3>${esc(p.title)}</h3><p>${esc(p.details)}</p>
      <p class="muted">${esc(p.contact_name || "")} ${esc(p.contact_phone || "")} ${esc(p.contact_email || "")} ${p.show_phone ? "(phone public)" : "(phone hidden)"}</p>
      <div class="lf-act">
        ${p.status === "pending" ? `<button class="btn" data-hset="approved">Approve</button><button class="btn soft" data-hset="rejected">Reject</button>` : ""}
        ${p.status === "approved" ? `<button class="btn soft" data-hset="done">Mark covered</button>` : ""}
      </div>
    </article>`;
  async function load() {
    if (!token()) return;
    try {
      const all = await api("/rest/v1/help_requests?select=*&status=in.(pending,approved)&order=created_at.desc&limit=200", {}, token());
      const offers = await api("/rest/v1/help_offers?select=*,help_requests(title,city,contact_name,contact_phone,contact_email)&handled=eq.false&order=created_at.desc", {}, token());
      const pend = all.filter(p => p.status === "pending"), live = all.filter(p => p.status === "approved");
      box.hidden = false;
      $("#hb-a-count").textContent = pend.length;
      $("#hb-a-pending").innerHTML = pend.length ? pend.map(card).join("") : '<p class="muted">Nothing waiting. 🎉</p>';
      $("#hb-a-live").innerHTML = live.length ? live.map(card).join("") : '<p class="muted">No live requests.</p>';
      $("#hb-a-offers").innerHTML = offers.length ? offers.map(o => `
        <div class="lf-m" data-oid="${o.id}"><p><b>${esc(o.from_name || "Someone")}</b> (${esc(o.from_contact)}) can help with <b>${esc(o.help_requests?.title)}</b> in ${esc(o.help_requests?.city)}:</p>
        <p>${esc(o.message)}</p><p class="muted">Pass to: ${esc(o.help_requests?.contact_name || "")} ${esc(o.help_requests?.contact_phone || "")} ${esc(o.help_requests?.contact_email || "")}</p>
        <button class="btn soft" data-odone>Mark handled</button></div>`).join("") : '<p class="muted">No new offers.</p>';
    } catch (err) { /* table not set up yet, or logged out: stay hidden */ }
  }
  box.addEventListener("click", async e => {
    const art = e.target.closest("[data-hid]"), set = e.target.closest("[data-hset]");
    if (set && art) {
      set.disabled = true;
      const now = new Date().toISOString();
      await api(`/rest/v1/help_requests?id=eq.${art.dataset.hid}`, {method: "PATCH", headers: JSONH,
        body: JSON.stringify(Object.assign({status: set.dataset.hset, reviewed_at: now}, set.dataset.hset === "done" ? {done_at: now} : {}))}, token());
      load(); return;
    }
    const o = e.target.closest("[data-oid]");
    if (e.target.closest("[data-odone]") && o) {
      await api(`/rest/v1/help_offers?id=eq.${o.dataset.oid}`, {method: "PATCH", headers: JSONH, body: JSON.stringify({handled: true})}, token());
      load();
    }
  });
  load();
}
})();
