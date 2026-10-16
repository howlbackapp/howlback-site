// Howlback lost & found: board, post form, admin. Talks to Supabase over plain fetch.
(() => {
const SB = "https://zgzrnlkffqkjtowziftk.supabase.co";
const KEY = "sb_publishable_2xvvHFjLuvY_z1ewBIdwPw_hzlMXIhQ";
const BUCKET = "lost-found";
const photo = p => `${SB}/storage/v1/object/public/${BUCKET}/${p}`;
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmtDate = d => d ? new Date(d + (d.length === 10 ? "T12:00:00" : "")).toLocaleDateString("en-US", {month: "short", day: "numeric"}) : "";
const $ = s => document.querySelector(s);

async function api(path, opts = {}, token) {
  const headers = Object.assign({apikey: KEY}, opts.headers || {});
  if (token) headers.Authorization = "Bearer " + token;
  const r = await fetch(SB + path, Object.assign({}, opts, {headers}));
  if (!r.ok) { const t = await r.text(); const e = new Error(t || r.statusText); e.status = r.status; throw e; }
  const ct = r.headers.get("content-type") || "";
  return ct.includes("json") ? r.json() : r.text();
}

// shrink + re-encode photos (also strips location data from the file)
async function shrink(file) {
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise((ok, bad) => { const i = new Image(); i.onload = () => ok(i); i.onerror = bad; i.src = url; });
    const max = 1600, s = Math.min(1, max / Math.max(img.naturalWidth, img.naturalHeight));
    const c = document.createElement("canvas");
    c.width = Math.round(img.naturalWidth * s); c.height = Math.round(img.naturalHeight * s);
    c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
    return await new Promise(ok => c.toBlob(ok, "image/jpeg", 0.85));
  } finally { URL.revokeObjectURL(url); }
}

// ---------- public board ----------
const list = $("#lf-list");
if (list) {
  let posts = [], kind = "all";
  const city = $("#lf-city");
  const draw = () => {
    const c = city.value;
    const rows = posts.filter(p => (kind === "all" || p.kind === kind) && (!c || p.city === c));
    if (!rows.length) { list.innerHTML = `<p class="muted lf-empty">No ${kind === "all" ? "" : kind + " "}dogs posted${c ? " in " + esc(c) : ""} yet.</p>`; return; }
    list.innerHTML = rows.map(p => `
      <article class="lf-card${p.status === "reunited" ? " reunited" : ""}">
        <img src="${photo(p.photo_path)}" alt="${esc(p.kind)} dog in ${esc(p.city)}" loading="lazy">
        <div class="lf-body">
          ${p.status === "reunited" ? '<span class="lf-reunited">REUNITED 🎉</span>' : `<span class="lf-tag ${p.kind}">${p.kind === "lost" ? "Lost" : "Found"}</span>`}
          <h3>${esc(p.dog_name || (p.kind === "lost" ? "Lost dog" : "Found dog"))}</h3>
          <p class="lf-where">${esc(p.city)}${p.area ? " · " + esc(p.area) : ""}${p.seen_on ? " · " + fmtDate(p.seen_on) : ""}</p>
          <p>${esc(p.description)}</p>
          ${p.status === "reunited" ? "" : `<div class="lf-act">${p.phone ? `<a class="btn" href="tel:${esc(p.phone.replace(/[^0-9+]/g, ""))}">Call ${esc(p.phone)}</a>` : ""}<button class="btn soft" type="button" data-msg="${p.id}">Message the poster</button></div>`}
        </div>
      </article>`).join("");
  };
  document.querySelectorAll("[data-kind]").forEach(b => b.addEventListener("click", () => {
    kind = b.dataset.kind;
    document.querySelectorAll("[data-kind]").forEach(x => x.setAttribute("aria-selected", x === b));
    draw();
  }));
  city.addEventListener("change", draw);
  api("/rest/v1/lost_found_public?select=*&order=created_at.desc&limit=300")
    .then(r => { posts = r; draw(); })
    .catch(() => { list.innerHTML = '<p class="muted lf-empty">Couldn’t load posts. Try again in a minute.</p>'; });

  // message the poster
  const dlg = $("#lf-msg");
  list.addEventListener("click", e => {
    const b = e.target.closest("[data-msg]"); if (!b) return;
    dlg.querySelector("[name=post_id]").value = b.dataset.msg;
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
      await api("/rest/v1/lost_found_messages", {method: "POST", headers: {"Content-Type": "application/json", Prefer: "return=minimal"},
        body: JSON.stringify({post_id: f.post_id.value, from_name: f.from_name.value.trim() || null, from_contact: f.from_contact.value.trim(), message: f.message.value.trim()})});
      note.textContent = "Sent! We’ll pass your message to the poster.";
      f.reset(); setTimeout(() => dlg.close(), 1800);
    } catch (err) { note.textContent = "That didn’t send. Check your message and try again."; }
    btn.disabled = false;
  });
}

// ---------- post form ----------
const form = $("#lf-form");
if (form) {
  const prev = $("#lf-preview"), file = form.querySelector("[name=photo]");
  file.addEventListener("change", () => {
    const f = file.files[0];
    prev.innerHTML = f ? `<img src="${URL.createObjectURL(f)}" alt="Your photo">` : "";
  });
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const note = $("#lf-status"), btn = form.querySelector("button[type=submit]");
    if (form.website.value) return;
    const f = file.files[0];
    const phone = form.contact_phone.value.trim(), email = form.contact_email.value.trim();
    if (!f) { note.textContent = "Please add a photo of the dog."; return; }
    if (!phone && !email) { note.textContent = "Please add a phone number or email so people can reach you."; return; }
    btn.disabled = true; note.textContent = "Uploading photo...";
    try {
      const blob = await shrink(f);
      const id = crypto.randomUUID(), tok = crypto.randomUUID();
      const path = `${new Date().toISOString().slice(0, 10)}/${crypto.randomUUID()}.jpg`;
      await api(`/storage/v1/object/${BUCKET}/${path}`, {method: "POST", headers: {"Content-Type": "image/jpeg", "x-upsert": "false"}, body: blob});
      note.textContent = "Sending your post...";
      await api("/rest/v1/lost_found", {method: "POST", headers: {"Content-Type": "application/json", Prefer: "return=minimal"},
        body: JSON.stringify({
          id, edit_token: tok, kind: form.kind.value, city: form.city.value, area: form.area.value.trim() || null,
          seen_on: form.seen_on.value || null, dog_name: form.dog_name.value.trim() || null,
          description: form.description.value.trim(), photo_path: path,
          contact_name: form.contact_name.value.trim() || null, contact_phone: phone || null,
          contact_email: email || null, show_phone: !!(phone && form.show_phone.checked)})});
      const link = `${location.origin}/lost-found/update/?id=${id}&t=${tok}`;
      $("#lf-link").value = link;
      form.hidden = true; $("#lf-done").hidden = false; window.scrollTo(0, 0);
    } catch (err) {
      note.textContent = /description/.test(err.message) ? "Please write a little more about the dog (at least a sentence)." : "Something went wrong. Check your photo (JPG or PNG under 8 MB) and try again.";
      btn.disabled = false;
    }
  });
}

// ---------- copy private link ----------
const copyLink = $("#lf-copy-link");
if (copyLink) copyLink.addEventListener("click", async () => {
  const v = $("#lf-link").value;
  try { await navigator.clipboard.writeText(v); copyLink.textContent = "Copied!"; } catch (_) { $("#lf-link").select(); }
});

// ---------- poster marks reunited ----------
const upd = $("#lf-update");
if (upd) {
  const q = new URLSearchParams(location.search), note = $("#lf-upd-note"), b = $("#lf-reunite");
  if (!q.get("id") || !q.get("t")) { b.hidden = true; note.textContent = "This link is missing some info. Use the full link you saved after posting."; }
  b.addEventListener("click", async () => {
    b.disabled = true; note.textContent = "Updating...";
    try {
      const ok = await api("/rest/v1/rpc/lf_mark_reunited", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({p_id: q.get("id"), p_token: q.get("t")})});
      if (ok === true) { b.hidden = true; note.textContent = "🎉 So happy for you! Your post now says REUNITED for 24 hours, then it comes down."; }
      else { note.textContent = "We couldn\u2019t find that post. It may already be marked reunited."; b.disabled = false; }
    } catch (e) { note.textContent = "Something went wrong. Try again in a minute."; b.disabled = false; }
  });
}

// ---------- admin ----------
const admin = $("#lf-admin");
if (admin) {
  const ADMIN = "hello@howlback.app";
  const h = new URLSearchParams(location.hash.slice(1));
  if (h.get("access_token")) {
    sessionStorage.setItem("lf_token", h.get("access_token"));
    history.replaceState(null, "", location.pathname);
  }
  const token = () => sessionStorage.getItem("lf_token");
  const login = $("#lf-login"), panel = $("#lf-panel");

  login.addEventListener("submit", async e => {
    e.preventDefault();
    const note = login.querySelector(".lf-note");
    try {
      await api("/auth/v1/otp?redirect_to=" + encodeURIComponent(location.origin + "/admin/"), {method: "POST",
        headers: {"Content-Type": "application/json"}, body: JSON.stringify({email: ADMIN, create_user: true})});
      note.textContent = "Check your email (" + ADMIN + ") for a login link. It works for 1 hour.";
    } catch (err) { note.textContent = "Couldn’t send the link. Wait a minute and try again."; }
  });

  const caption = p => `${p.kind === "lost" ? "🚨 LOST DOG" : "🐾 FOUND DOG"} · ${p.city}${p.area ? " (" + p.area + ")" : ""}\n\n${p.dog_name ? p.dog_name + ". " : ""}${p.description}${p.seen_on ? "\n\nLast seen: " + fmtDate(p.seen_on) : ""}\n\n${p.show_phone && p.contact_phone ? "Contact: " + p.contact_phone : "Message the poster at howlback.app/lost-found"}\n\nPlease share so this pup gets home 🧡\n#RGV #LostDog #FoundDog #${p.city.replace(/\s+/g, "")}`;

  const card = p => `
    <article class="lf-card" data-id="${p.id}">
      <img src="${photo(p.photo_path)}" alt="">
      <div class="lf-body">
        <span class="lf-tag ${p.kind}">${p.kind}</span> <span class="muted">${new Date(p.created_at).toLocaleString()}</span>
        <h3>${esc(p.dog_name || "(no name)")} · ${esc(p.city)}${p.area ? " · " + esc(p.area) : ""}</h3>
        <p>${esc(p.description)}</p>
        <p class="muted">Seen: ${fmtDate(p.seen_on) || "?"} · ${esc(p.contact_name || "")} ${esc(p.contact_phone || "")} ${esc(p.contact_email || "")} ${p.show_phone ? "(phone public)" : "(phone hidden)"}</p>
        <div class="lf-act">
          ${p.status === "pending" ? `<button class="btn" data-set="approved">Approve</button><button class="btn soft" data-set="rejected">Reject</button>` : ""}
          ${p.status === "approved" ? `<button class="btn soft" data-set="reunited">Mark reunited</button><button class="btn soft" data-copy-cap>Copy Facebook caption</button><a class="btn soft" href="${photo(p.photo_path)}" target="_blank" rel="noopener">Open photo</a>` : ""}
        </div>
      </div>
    </article>`;

  let all = [];
  async function load() {
    if (!token()) { login.hidden = false; panel.hidden = true; return; }
    try {
      all = await api("/rest/v1/lost_found?select=*&order=created_at.desc&limit=300", {}, token());
      const msgs = await api("/rest/v1/lost_found_messages?select=*,lost_found(dog_name,kind,city,contact_name,contact_phone,contact_email)&handled=eq.false&order=created_at.desc", {}, token());
      login.hidden = true; panel.hidden = false;
      const pend = all.filter(p => p.status === "pending"), live = all.filter(p => p.status === "approved");
      $("#lf-pending").innerHTML = pend.length ? pend.map(card).join("") : '<p class="muted">Nothing waiting. 🎉</p>';
      $("#lf-live").innerHTML = live.length ? live.map(card).join("") : '<p class="muted">No live posts yet.</p>';
      $("#lf-count").textContent = pend.length;
      $("#lf-msgs").innerHTML = msgs.length ? msgs.map(m => `
        <div class="lf-m" data-mid="${m.id}"><p><b>${esc(m.from_name || "Someone")}</b> (${esc(m.from_contact)}) about <b>${esc(m.lost_found?.dog_name || m.lost_found?.kind + " dog")}</b> in ${esc(m.lost_found?.city)}:</p>
        <p>${esc(m.message)}</p><p class="muted">Forward to: ${esc(m.lost_found?.contact_name || "")} ${esc(m.lost_found?.contact_phone || "")} ${esc(m.lost_found?.contact_email || "")}</p>
        <button class="btn soft" data-done>Mark handled</button></div>`).join("") : '<p class="muted">No new messages.</p>';
    } catch (err) {
      if (err.status === 401 || /JWT/.test(err.message)) { sessionStorage.removeItem("lf_token"); login.hidden = false; panel.hidden = true; }
      else panel.insertAdjacentHTML("afterbegin", '<p class="lf-note">Couldn’t load. Refresh to try again.</p>');
    }
  }
  panel.addEventListener("click", async e => {
    const art = e.target.closest("[data-id]"), set = e.target.closest("[data-set]");
    if (set && art) {
      set.disabled = true;
      await api(`/rest/v1/lost_found?id=eq.${art.dataset.id}`, {method: "PATCH", headers: {"Content-Type": "application/json", Prefer: "return=minimal"},
        body: JSON.stringify(Object.assign({status: set.dataset.set, reviewed_at: new Date().toISOString()}, set.dataset.set === "reunited" ? {reunited_at: new Date().toISOString()} : {}))}, token());
      load(); return;
    }
    if (e.target.closest("[data-copy-cap]") && art) {
      const p = all.find(x => x.id === art.dataset.id);
      try { await navigator.clipboard.writeText(caption(p)); e.target.textContent = "Copied!"; } catch (_) { prompt("Copy this caption:", caption(p)); }
      return;
    }
    const m = e.target.closest("[data-mid]");
    if (e.target.closest("[data-done]") && m) {
      await api(`/rest/v1/lost_found_messages?id=eq.${m.dataset.mid}`, {method: "PATCH", headers: {"Content-Type": "application/json", Prefer: "return=minimal"}, body: JSON.stringify({handled: true})}, token());
      load();
    }
  });
  $("#lf-logout").addEventListener("click", () => { sessionStorage.removeItem("lf_token"); load(); });
  load();
}
})();
