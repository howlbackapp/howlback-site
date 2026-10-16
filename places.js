// Dog-friendly places map. Data comes from window.PLACES (built from src/places.json).
(function () {
  var P = window.PLACES || [], el = document.getElementById("pl-map");
  if (!el || !window.L) return;
  var ICON = { trail: "🥾", dogpark: "🐕", beach: "🏖️", park: "🌳", food: "🍔" };
  var LABEL = { trail: "Trail", dogpark: "Dog park", beach: "Beach", park: "Park", food: "Food & drinks" };
  var city = "", type = "";
  var esc = function (s) { return String(s || "").replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var dir = function (p) { return "https://www.google.com/maps/dir/?api=1&destination=" + p.lat + "," + p.lng; };

  var map = L.map(el, { scrollWheelZoom: false, tap: true }).setView([26.1, -97.45], 10);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "&copy; OpenStreetMap" }).addTo(map);

  function facts(p) {
    if (p.type !== "trail") return "";
    return '<dl class="pl-facts"><div><dt>Distance</dt><dd>' + esc(p.miles) + '</dd></div><div><dt>Paved?</dt><dd>' + esc(p.surface) +
      '</dd></div><div><dt>Parking</dt><dd>' + esc(p.parking) + '</dd></div></dl>';
  }
  function body(p, full) {
    return '<span class="pl-tag pl-' + p.type + '">' + ICON[p.type] + " " + LABEL[p.type] + " · " + esc(p.city) + '</span>' +
      '<b class="pl-name">' + esc(p.name) + '</b><span class="pl-addr">' + esc(p.addr) + '</span>' +
      (full ? facts(p) : (p.type === "trail" ? '<span class="pl-mini">' + esc(p.miles) + " · " + esc(p.surface) + '</span>' : "")) +
      (p.note ? '<p class="pl-note">' + esc(p.note) + '</p>' : "") +
      '<a class="btn soft sm" href="' + dir(p) + '" target="_blank" rel="noopener">Directions</a>';
  }

  P.forEach(function (p, i) {
    p.i = i;
    p.m = L.marker([p.lat, p.lng], {
      icon: L.divIcon({ className: "pl-pin pl-" + p.type, html: "<span>" + ICON[p.type] + "</span>", iconSize: [34, 34], iconAnchor: [17, 17], popupAnchor: [0, -14] }),
      title: p.name
    }).bindPopup('<div class="pl-pop">' + body(p, false) + '</div>', { maxWidth: 260 });
  });

  var list = document.getElementById("pl-list"), count = document.getElementById("pl-count");
  function render() {
    var shown = P.filter(function (p) { return (!city || p.city === city) && (!type || p.type === type); });
    P.forEach(function (p) { map.removeLayer(p.m); });
    shown.forEach(function (p) { p.m.addTo(map); });
    if (shown.length) map.fitBounds(L.latLngBounds(shown.map(function (p) { return [p.lat, p.lng]; })).pad(0.15), { maxZoom: 14 });
    count.textContent = shown.length + (shown.length === 1 ? " place" : " places");
    list.innerHTML = shown.length ? shown.map(function (p) {
      return '<li class="pl-card" data-i="' + p.i + '">' + body(p, true) + '<button type="button" class="pl-show">Show on map</button></li>';
    }).join("") : '<li class="pl-empty">Nothing here yet. More spots are coming soon.</li>';
  }
  list.addEventListener("click", function (e) {
    var b = e.target.closest(".pl-show"); if (!b) return;
    var p = P[+b.closest(".pl-card").dataset.i];
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    map.setView([p.lat, p.lng], 15); p.m.openPopup();
  });
  function chips(id, set) {
    var row = document.getElementById(id);
    row.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      row.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === b); });
      set(b.dataset.v); render();
    });
  }
  chips("pl-city", function (v) { city = v; });
  chips("pl-type", function (v) { type = v; });
  render();
})();
