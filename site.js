const RES = [
 // [name, type, city, address, phone, note]
 ["Brownsville Animal Regulation and Care Center (BARC)","Shelter & animal control","Brownsville","416 FM 511, Olmito","(956) 544-7351",""],
 ["City of Harlingen Animal Shelter","Shelter & animal control","Harlingen","1106 Markowsky Ave","(956) 216-5250",""],
 ["Cameron County Animal Shelter","Shelter & animal control","San Benito","26981 FM 510","(956) 361-8206",""],
 ["San Benito Animal Control","Shelter & animal control","San Benito","401 N Sam Houston Blvd","(956) 361-3804",""],
 ["Palm Valley Animal Society, Laurie P. Andrews Center","Shelter & animal control","Edinburg","2451 N Expressway 281","(956) 720-4563","Has a foster program and monthly low-cost clinics"],
 ["Palm Valley Animal Society, Trenton Center","Shelter & animal control","Edinburg","2501 W Trenton Rd","(956) 686-1141",""],
 ["McAllen Animal Care Services","Shelter & animal control","McAllen","311 N 15th St","(956) 681-1919",""],
 ["Edinburg Animal Care Services","Shelter & animal control","Edinburg","1301 N Doolittle Rd","(956) 316-2185",""],
 ["Pharr Animal Control","Shelter & animal control","Pharr","1015 E Ferguson Ave","(956) 402-4350",""],
 ["Mission Animal Shelter","Shelter & animal control","Mission","227 Abelino Farias St","(956) 580-8741",""],
 ["Weslaco Animal Care Services","Shelter & animal control","Weslaco","1912 Joe Stephens Ave","(956) 447-3406",""],
 ["Hidalgo County Animal Control","Shelter & animal control","Edinburg","1304 S 25th Ave","(956) 383-0111","For areas outside city limits"],
 ["Brownsville Spay Neuter Clinic","Low-cost vet & vaccines","Brownsville","1050 MacKintosh Dr, Ste A","(956) 550-8366",""],
 ["Laguna Madre Humane Society","Low-cost vet & vaccines","Port Isabel","417 1/2 E Maxan St","(956) 266-3140","Low-cost clinic for the island and Laguna Vista area"],
 ["Rio Grande Valley Humane Society","Low-cost vet & vaccines","Harlingen","18038 Garrett Rd","(956) 556-5885","Monthly low-cost vaccine clinic and spay/neuter"],
 ["RGV Low Cost Spay/Neuter Clinic","Low-cost vet & vaccines","McAllen","500 E Hackberry Ave, Ste 100 B","(956) 687-7728",""],
 ["Texas Wellness Spay and Neuter Clinic","Low-cost vet & vaccines","McAllen","901 N Ware Rd","(956) 638-2970",""],
 ["YMR Veterinary Services","Low-cost vet & vaccines","McAllen","1912 Beaumont Ave","(956) 306-8868",""],
 ["Ram Spay & Neuter Wellness Clinic","Low-cost vet & vaccines","McAllen","800 E Dove Ave, Ste L","(956) 322-3877",""],
 ["Pet Doctor 911","Urgent & after-hours vet","McAllen","7017 N 10th St","(956) 683-7387","Open 24/7"],
 ["McAllen Urgent Vet","Urgent & after-hours vet","McAllen","101 E Expressway 83, Ste 140","(956) 803-0191",""],
 ["Harlingen Urgent Vet","Urgent & after-hours vet","Harlingen","6710 W Expressway 83, Ste 105","(956) 654-4887",""],
 ["WeekendVET","Urgent & after-hours vet","Brownsville","2908 W Alton Gloor Blvd","(956) 370-3600","Open weekends"],
 ["Boca Chica Animal Hospital","Urgent & after-hours vet","Brownsville","1245 Frontage Rd","(956) 441-2287",""],
 ["RGVHS Pet Pantry","Pet food help","Harlingen","1106 Markowsky Ave","(956) 425-7297","Free pet food when donations allow. Call ahead"],
 ["Food for Hunger WME","Pet food help","Alton","1115 S Maryland St","(956) 585-9966",""],
 ["San Benito Food Pantry","Pet food help","San Benito","2007 E Expressway","(956) 399-1659",""],
 ["PetSmart","Pet supplies","Brownsville","585 Morrison Rd","(956) 350-0608",""],
 ["The Paw Pantry","Pet supplies","Harlingen","707 N 77 Sunshine Strip","(956) 412-7297",""],
 ["Pet Supplies Plus","Pet supplies","McAllen","5800 N 10th St, Ste 800","(956) 331-8451","Self-serve dog wash"],
 ["Pet-Max","Pet supplies","McAllen","520 S 10th St","(956) 322-3237",""],
 ["Paw Organic","Pet supplies","McAllen","1109 W Nolana Ave, Ste 303","(956) 522-1795",""],
 ["SBCQueen Bully and Pet Supplies","Pet supplies","Alamo","835 US 83 Frontage Rd S","(956) 648-9412",""],
];
const EVENTS = [
 {date:"2026-10-17", title:"Free dog vaccines and microchips", where:"Bert Ogden Arena parking lot, Edinburg", time:"Starts 8 AM, first 100 dogs", items:["Rabies and DAPPv vaccines, plus microchips","Dogs 12 weeks and up, leashed, max 3 per family","Hosted by Yaqui Animal Rescue and Bert Ogden Subaru"], link:"https://foxrgv.tv/free-dog-vaccination-and-microchip-clinic-scheduled-in-edinburg-on-october-17th/", linkText:"Event details"},
 {date:"2026-10-17", title:"Howlin' Harvest fall festival", where:"Laurie P. Andrews Center, 2451 N US Expressway 281, Edinburg", time:"5 to 9 PM", items:["Family games and pet-friendly activities","Helps the animals at Palm Valley Animal Society"], link:"https://www.pvastx.org/events", linkText:"Event details"},
 {date:"2026-10-24", title:"Community vaccine clinic", where:"Palm Valley Animal Society, Edinburg", time:"Line starts at 9 AM", items:["Low-cost vaccines and microchips for dogs and cats","Up to 4 pets per vehicle, 2 per handler","Card payment only"], link:"https://www.pvastx.org/communityclinic", linkText:"Clinic info"},
 {date:"2026-10-25", title:"Barktoberfest", where:"Hopper Haus, 418 E Queen Isabella Blvd, Port Isabel", time:"Starts 1 PM", items:["Pet costume contests, raffles, and food specials","Benefits Laguna Madre Humane Society"], link:"https://business.spichamber.com/events/details/barktoberfest-2026-17543", linkText:"Event details"},
 {date:"2026-10-31", title:"Low-cost vaccine clinic", where:"RGV Humane Society, 18038 Garrett Rd, Harlingen", time:"9 to 11:30 AM, pre-registration required", items:["Rabies $13, DHPPV $16, microchip $11","Flea, tick, and heartworm meds available","Pets must ride inside the vehicle"], link:"https://www.rgvhs.org/monthly-clinic", linkText:"Register"},
 {date:"2026-11-06", title:"Toast to Tails gala", where:"Brownsville Events Center, 1 Event Center, Brownsville", time:"6 to 11 PM, tickets $100", items:["Dinner, entertainment, and an auction","Día de los Muertos theme, festive attire encouraged","Benefits the Brownsville Animal Regulation and Care Center"], link:"https://allevents.in/brownsville/2026-barcc-toast-to-tails-gala/100001992443871254", linkText:"Event details"},
 {date:"", title:"Monthly community clinic", where:"Palm Valley Animal Society, Edinburg", time:"Monthly, call for dates", items:["Low-cost vaccines and microchips","Open to all pets, not just adoptions","Card payment only"], link:"https://www.pvastx.org/communityclinic", linkText:"Clinic info"},
 {date:"", title:"Weekend adoptions in McAllen", where:"PetSmart and Petco near 10th St and Trenton Rd, McAllen", time:"Sundays 12:30 to 5:30 PM", items:["Meet adoptable dogs from Palm Valley Animal Society"], link:"https://www.pvastx.org/events", linkText:"Event details"},
];
const RESCUES = [
 ["A Long Walk Home Rescue","Rio Grande Valley","facebook.com/ALongWalkHome956"],
 ["Ana's Safe Haven Rescue","Harlingen","anassafehavenrescue.org"],
 ["Answering a Stray Dog's Prayer","Edinburg","answeringastraydogsprayer.org"],
 ["Bee's Animal Safe Haven","Rio Grande Valley","facebook.com/beesanimalsafehaven"],
 ["Border Paws of the RGV","Rio Grande Valley","linktr.ee/borderpawsrgv"],
 ["Brownsville Animal Defense","Brownsville","brownsvilleanimaldefense.org"],
 ["Cinderella Pet Rescue","Peñitas","cinderella-pet-rescue.org"],
 ["Donja's Dogs","Harlingen","donjasdogs.com"],
 ["Forgotten Friends Texas Rescue","Mission","forgotten-friends.org"],
 ["Friends of Animal Rescue","South Padre Island","spifriendsofanimalrescue.com"],
 ["Harley's Hounds","Harlingen","harleyshoundsinc.com"],
 ["Lucky's Legacy Animal Rescue","Weslaco","facebook.com/LuckysLegacyAR"],
 ["Luv Us Mutts","Mission","luvusmutts.com"],
 ["No-Kill RGV Coalition","San Juan","nkrgvcoalition.org"],
 ["Paws and Strides Rescue","San Benito","pawsandstridesrescue.org"],
 ["Paws Fur Help","McAllen","pawsfurhelp.org"],
 ["PawStories","Mission","pawstories.pet"],
 ["Recycled Rovers & Friends","Donna","recycledroversrgv.com"],
 ["RGV Paws Huellitas del Valle","Mission","facebook.com/RGVPawsHuellitasDelValle"],
 ["Sanctuary Park Rescue","Brownsville","sanctuaryparkrescue.org"],
 ["South Texas Rescue Network","San Benito","facebook.com/SouthTexasRescueandNetwork"],
 ["Texas Pet Rescue","Brownsville","texaspetrescue.net"],
 ["Valley Paws Animal Rescue","Weslaco","facebook.com/valleypawsrgv"],
 ["Yaqui Animal Rescue","Sullivan City","yaquianimalrescue.com"],
];

const $ = s => document.querySelector(s);
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* mobile menu */
const mbtn = $("#menu-btn");
if (mbtn) mbtn.addEventListener("click", () => {
  const open = mbtn.getAttribute("aria-expanded") !== "true";
  mbtn.setAttribute("aria-expanded", open); $("#site-nav").classList.toggle("open", open);
});

/* signup: email or text */
document.querySelectorAll(".sw button").forEach(b => b.addEventListener("click", () => {
  const m = b.dataset.mode;
  document.querySelectorAll(".sw button").forEach(x => x.setAttribute("aria-pressed", x === b));
  $("#mode-email").hidden = m !== "email"; $("#mode-text").hidden = m !== "text";
  (m === "email" ? $("#email") : $("#phone")).focus();
}));
if ($("#textform")) $("#textform").addEventListener("submit", async e => {
  e.preventDefault();
  const f = e.target, btn = f.querySelector("button");
  btn.disabled = true; $("#text-err").hidden = true;
  try {
    const r = await fetch("/", {method:"POST", headers:{"Content-Type":"application/x-www-form-urlencoded"}, body:new URLSearchParams(new FormData(f)).toString()});
    if (r.status >= 500) throw 0;
    f.hidden = true; $("#text-ok").hidden = false;
  } catch { $("#text-err").hidden = false; btn.disabled = false; }
});
document.querySelectorAll("[data-focus-email]").forEach(a => a.addEventListener("click", () => setTimeout(() => $("#email") && $("#email").focus({preventScroll:true}), 450)));

/* resources */
if ($("#res")) {
  const CATS = ["All", ...new Set(RES.map(r => r[1]))];
  const CITIES = ["All cities", ...[...new Set(RES.map(r => r[2]))].sort()];
  let cat = "All", all = false;
  $("#city").innerHTML = CITIES.map(c => `<option>${esc(c)}</option>`).join("");
  $("#cats").innerHTML = CATS.map(c => `<button type="button" aria-pressed="${c===cat}">${esc(c)}</button>`).join("");
  const draw = () => {
    const q = $("#q").value.trim().toLowerCase(), city = $("#city").value;
    const list = RES.filter(r => (cat==="All" || r[1]===cat) && (city==="All cities" || r[2]===city) && (!q || (r[0]+" "+r[2]+" "+r[3]).toLowerCase().includes(q)));
    const shown = (all || q) ? list : list.slice(0, 10);
    $("#showall").hidden = shown.length === list.length;
    $("#showall").textContent = `Show all ${list.length}`;
    $("#res").innerHTML = list.length ? shown.map(r => `
      <div class="row"><b>${esc(r[0])}</b>
        <a class="ph" href="tel:${r[4].replace(/\D/g,"")}">${esc(r[4])}</a>
        <span class="sub">${esc(r[3])}, ${esc(r[2])}${r[5] ? ". " + esc(r[5]) : ""}</span>
        <span class="kind">${esc(r[1])}</span></div>`).join("")
      : `<p class="empty">Nothing matches that search. Try another city or type.</p>`;
  };
  $("#cats").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    cat = b.textContent; all = false;
    [...$("#cats").children].forEach(x => x.setAttribute("aria-pressed", x === b));
    draw();
  });
  $("#showall").addEventListener("click", () => { all = true; draw(); });
  $("#q").addEventListener("input", draw);
  $("#city").addEventListener("change", () => { all = false; draw(); });
  draw();
}

/* events */
if ($("#ev")) {
  const MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const today = new Date(); today.setHours(0,0,0,0);
  const upcoming = EVENTS.filter(e => !e.date || new Date(e.date+"T23:59:59") >= today);
  const lim = +($("#ev").dataset.limit || 99);
  $("#ev").innerHTML = upcoming.slice(0, lim).map(e => {
    let d = `<div class="cal"><span>Monthly</span></div>`;
    if (e.date){ const [y,m,dd] = e.date.split("-").map(Number); const wd = new Date(y,m-1,dd).toLocaleDateString("en-US",{weekday:"short"}); d = `<div class="cal"><b>${dd}</b><span>${MON[m-1]}, ${wd}</span></div>`; }
    return `<article class="e">${d}<div class="e-body"><h3>${esc(e.title)}</h3><p><b style="font-weight:600">${esc(e.where)}</b></p><p class="muted">${esc(e.time)}</p>
      <ul>${e.items.map(i=>`<li>${esc(i)}</li>`).join("")}</ul>
      <a class="link" href="${e.link}" target="_blank" rel="noopener">${esc(e.linkText)}</a></div></article>`;
  }).join("") || `<p class="empty">No clinics on the calendar right now. Check back soon.</p>`;
}

/* rescues */
if ($("#rg")) $("#rg").innerHTML = RESCUES.map(r => `<div class="r"><b>${esc(r[0])}</b><small>${esc(r[1])}</small><a href="https://${r[2]}" target="_blank" rel="noopener">${esc(r[2])}</a></div>`).join("");

/* copy email */
if ($("#copy")) $("#copy").addEventListener("click", async () => {
  const b = $("#copy");
  try { await navigator.clipboard.writeText("hello@howlback.app"); b.textContent = "Copied"; }
  catch { const r = document.createRange(); r.selectNodeContents($("#addr")); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = "Selected"; }
  setTimeout(() => b.textContent = "Copy address", 1800);
});

/* install page: device tabs + Android install button */
const osTabs = document.querySelectorAll(".os-tabs button");
if (osTabs.length) {
  const show = os => {
    osTabs.forEach(b => b.setAttribute("aria-selected", b.dataset.os === os));
    document.querySelectorAll("[data-panel]").forEach(p => p.hidden = p.dataset.panel !== os);
  };
  osTabs.forEach(b => b.addEventListener("click", () => show(b.dataset.os)));
  const ua = navigator.userAgent;
  show(/android/i.test(ua) ? "android" : "ios");
}
let deferredInstall;
window.addEventListener("beforeinstallprompt", e => {
  e.preventDefault(); deferredInstall = e;
  if ($("#install-btn")) $("#install-btn").hidden = false;
});
if ($("#install-btn")) $("#install-btn").addEventListener("click", async () => {
  if (!deferredInstall) return;
  deferredInstall.prompt(); await deferredInstall.userChoice; deferredInstall = null; $("#install-btn").hidden = true;
});

/* offline support */
if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("/sw.js").catch(() => {});
