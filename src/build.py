"""Builds the Howlback site pages from shared pieces.

Run from the repo root:  python3 src/build.py
Edit words in src/parts.json, src/posts.json, or the page templates below, then rebuild.
"""
import json, os, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "src/parts.json")))
POSTS = json.load(open(os.path.join(ROOT, "src/posts.json")))
SITE = "https://howlback.app"

NAV = [("/lost-found/", "Lost & found"), ("/help/", "Local help"), ("/clinics/", "Clinics"), ("/rescues/", "Rescues"),
       ("/blog/", "Blog"), ("/places/", "Dog-friendly places"), ("/must-haves/", "Foster must-haves"), ("/app/", "The app"), ("/share/", "Share a story"),
       ("/install/", "Add to home screen")]

TABS = [("/", "Home", '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>'),
        ("/help/", "Help", '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M5.6 5.6l3.6 3.6M14.8 14.8l3.6 3.6M18.4 5.6l-3.6 3.6M9.2 14.8l-3.6 3.6"/>'),
        ("/clinics/", "Clinics", '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'),
        ("/blog/", "Blog", '<path d="M5 4h14v16H5zM9 8h6M9 12h6M9 16h3"/>'),
        ("/app/", "App", '<rect x="7" y="2" width="10" height="20" rx="3"/><path d="M11 18h2"/>')]

def tabbar(active):
    out = ""
    for h, t, icon in TABS:
        on = (h == active) or (h != "/" and active.startswith(h))
        cur = ' aria-current="page"' if on else ""
        out += f'<a href="{h}"{cur}><svg viewBox="0 0 24 24" aria-hidden="true">{icon}</svg><span>{t}</span></a>'
    return f'<nav class="tabbar" aria-label="App">{out}</nav>\n'


def fix_paths(t):
    t = t.replace('src="img/', 'src="/img/')
    t = t.replace('href="#join"', 'href="#join"')
    t = t.replace('href="#featured"', 'href="/share/"')
    return t

def isrc(i):
    return i if i.startswith("http") else f"/img/{i}"

def head(title, desc, path, img="/img/street-dog.jpg", schema=None):
    full = title if title == "Howlback" else f"{title} | Howlback"
    ld = "" if not schema else '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("</", "<\\/") + '</script>\n' 
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{img if img.startswith("http") else SITE + img}">
<meta property="og:url" content="{SITE}{path}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/img/favicon-48.png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#3d6b73">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Howlback">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/style.css">
{ld}<script data-goatcounter="https://howlback.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</head>
<body>
<div class="shell">
"""

def header(active):
    ACTIVE[0] = active
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if h == active else ""}>{t}</a>' for h, t in NAV)
    return f"""<header class="top">
  <div class="wrap">
    <a class="logo" href="/">howl<i>back</i></a>
    <nav aria-label="Main" id="site-nav">{links}</nav>
    <div class="right">
      <a class="icon-btn" href="#join" data-focus-email aria-label="Get updates"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21h4"/></svg></a>
      <button class="icon-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </div>
</header>
<main id="top">
"""

ACTIVE = ["/"]
def foot():
    return ("\n" + fix_paths(P["join"]) + "\n</main>\n\n" + fix_paths(P["footer"]) + "\n" + tabbar(ACTIVE[0]) +
            '</div>\n<script src="/site.js"></script>\n</body>\n</html>\n')

def page_head(h1, lead):
    return f"""  <div class="wrap page-head"><div class="head"><h1 style="font-size:clamp(36px,5vw,56px)">{h1}</h1><p class="lead">{lead}</p></div></div>
"""

import hashlib
def _h(*files):
    m = hashlib.md5()
    for f in files: m.update(open(os.path.join(ROOT, f), "rb").read())
    return m.hexdigest()[:8]
VER = {"/site.js": _h("site.js"), "/lf.js": _h("lf.js"), "/places.js": _h("places.js"), "/style.css": _h("src/base.css", "src/extra.css")}

def write(path, content):
    for f, v in VER.items():
        content = content.replace(f'"{f}"', f'"{f}?v={v}"')
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(content)

def card(p):
    img = (f'<img src="{isrc(p["img"])}" alt="{html.escape(p["alt"])}" loading="lazy">' if p["img"]
           else f'<span class="noimg">{html.escape(p["title"])}</span>')
    return (f'<a class="card" href="/blog/{p["slug"]}/">{img}<span class="topic">{p["topic"]}</span>'
            f'<h3>{html.escape(p["title"])}</h3><p class="muted">{html.escape(p["desc"].split(". ")[0].rstrip("."))}.</p></a>')

# ---------- HOME ----------
hero = fix_paths(P["hero"])
hero = hero.replace('class="wrap hero"', 'class="wrap hero home-hero"')
hero = re.sub(r'<a class="where soon-pill"[^>]*>.*?</a>',
              '<a class="where soon-pill" href="/app/">The app is coming soon. Take a peek</a>', hero)
hero = hero.replace('href="#help"', 'href="/help/"').replace('href="#stories"', 'href="/blog/"')

org = {"@context": "https://schema.org", "@type": "Organization", "name": "Howlback", "url": SITE, "logo": f"{SITE}/img/icon-512.png",
       "email": "hello@howlback.app", "areaServed": "Rio Grande Valley, Texas",
       "sameAs": ["https://www.instagram.com/howlback.app", "https://www.facebook.com/profile.php?id=61595201828343"]}
home = head("Howlback", "Local help for street dogs in the Rio Grande Valley: who to call, low-cost vets, vaccine clinics, rescues, and stories from South Texas.", "/", schema=org)
home += header("/") + hero + """
  <div class="wrap hide-installed" style="padding-bottom:8px">
    <a class="install-card" href="/install/"><img src="/img/icon-192.png" alt=""><div><b>Add Howlback to your home screen</b><span>Opens like an app. No download.</span></div><span class="go">How ›</span></a>
  </div>
"""
home += f"""
  <section class="stories" id="stories">
    <div class="wrap">
      <div class="section-top"><h2>Latest on the blog</h2><a class="link" href="/blog/">All posts</a></div>
      <div class="cards">{''.join(card(p) for p in POSTS if p["img"])[:]}</div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="section-top"><h2>Upcoming clinics</h2><a class="link" href="/clinics/">All clinics</a></div>
      <div class="ev" id="ev" data-limit="2"></div>
    </div>
  </section>

  <section style="padding-top:0">
    <div class="wrap">
      <div class="teaser">
        <div class="teaser-copy">
          <span class="pill-dark">Coming soon</span>
          <h2>The Howlback app</h2>
          <p class="lead">Follow foster dogs near you and chip in toward their verified vet bills, food, and supplies.</p>
          <a class="btn" href="/app/" style="align-self:flex-start;background:#fff;color:var(--ink)">See a preview</a>
        </div>
        <img src="/img/app/screen-1.webp" alt="Preview of the Howlback app showing a foster dog's profile" loading="lazy">
      </div>
    </div>
  </section>
"""
home += foot()
write("/", home)

# ---------- LOCAL HELP ----------
pg = head("Local help", "Found a stray in the Rio Grande Valley? What to do first, plus low-cost vets, after-hours vets, pet food help, and pet stores.", "/help/")
pg += header("/help/") + page_head("Local help in the Valley", "What to do when you find a dog, plus low-cost vets, after-hours vets, and pet food help. Hours change often, so call ahead.")
pg += '  <section class="page"><div class="wrap" style="display:flex;flex-direction:column">\n'
pg += P["found"] + P["tools"] + "\n  </div></section>\n" + foot()
write("/help/", pg)

# ---------- CLINICS ----------
import subprocess, datetime
EVENTS = json.loads(subprocess.run(["node", "-e", "const s=require('fs').readFileSync(process.argv[1],'utf8');process.stdout.write(JSON.stringify(new Function(s.split('const $ =')[0]+'; return EVENTS')()))", os.path.join(ROOT, "site.js")], capture_output=True, text=True, check=True).stdout)
today = datetime.date.today().isoformat()
ev_schema = []
for e in EVENTS:
    if not e.get("date") or e["date"] < today:
        continue
    ev_schema.append({"@context": "https://schema.org", "@type": "Event", "name": e["title"],
        "startDate": e["date"], "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": e["where"].split(",")[0], "address": {"@type": "PostalAddress", "streetAddress": e["where"], "addressRegion": "TX", "addressCountry": "US"}},
        "description": "; ".join(e.get("items", [])), "url": e.get("link") or f"{SITE}/clinics/",
        "organizer": {"@type": "Organization", "name": "See event details", "url": e.get("link") or SITE}})
pg = head("Vaccine clinics", "Free and low-cost dog vaccine and microchip clinics coming up around the Rio Grande Valley.", "/clinics/", schema=ev_schema or None)
pg += header("/clinics/") + page_head("Vaccine clinics and pet events", "Free and low-cost clinics around the Valley. Past events drop off on their own.")
pg += """  <section class="page"><div class="wrap">
    <div class="ev" id="ev"></div>
    <p class="muted" style="margin-top:24px">Know of a clinic we missed? Email <a class="link" href="mailto:hello@howlback.app?subject=Clinic%20to%20add">hello@howlback.app</a>.</p>
  </div></section>
""" + foot()
write("/clinics/", pg)

# ---------- RESCUES ----------
pg = head("South Texas rescues", "Rescue groups saving dogs across the Rio Grande Valley and South Texas, with links to reach them.", "/rescues/")
pg += header("/rescues/") + page_head("South Texas rescues", "Local groups saving dogs every day. Most are foster-based and don’t take drop-offs, so reach out online first.")
pg += '  <section class="page"><div class="wrap">\n        <div class="rgrid" id="rg"></div>\n' + fix_paths(P["notebox"]) + "  </div></section>\n" + foot()
write("/rescues/", pg)

# ---------- STORIES ----------
pg = head("Blog", "Rescue stories, Texas animal laws, and local dog guides from the Rio Grande Valley.", "/blog/")
pg += header("/blog/") + page_head("Blog", "Rescue stories, Texas laws, and local guides from the Valley.")
pg += f'  <section class="page"><div class="wrap"><div class="cards">{"".join(card(p) for p in POSTS)}</div></div></section>\n' + foot()
write("/blog/", pg)

for p in POSTS:
    cover = f'<img class="cover" src="{isrc(p["img"])}" alt="{html.escape(p["alt"])}">' if p["img"] else ""
    srcs = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in p["sources"])
    url = f"{SITE}/blog/{p['slug']}/"
    art = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "description": p["desc"],
           "image": (p['img'] if p['img'].startswith('http') else f"{SITE}/img/{p['img'] or 'street-dog.jpg'}"), "datePublished": p.get("date", ""),
           "author": {"@type": "Organization", "name": "Howlback", "url": SITE},
           "publisher": {"@type": "Organization", "name": "Howlback", "logo": {"@type": "ImageObject", "url": f"{SITE}/img/icon-512.png"}},
           "mainEntityOfPage": f"{SITE}/blog/{p['slug']}/"}
    pg = head(p["title"], p["desc"], f"/blog/{p['slug']}/", isrc(p['img'] or 'street-dog.jpg'), schema=art)
    pg += header("/blog/")
    pg += f"""  <article class="wrap article">
    <header>
      <a class="crumb" href="/blog/">‹ All posts</a>
      <span class="topic">{p["topic"]}</span>
      <h1>{html.escape(p["title"])}</h1>
    </header>
    {cover}
    <div class="prose">{p["html"]}
      <p><a href="/app/">See a preview of the app</a>, or sign up below to hear when it launches.</p>
    </div>
    <div class="share-row">
      <a class="btn soft" href="https://www.facebook.com/sharer/sharer.php?u={url}" target="_blank" rel="noopener">Share on Facebook</a>
      <button class="btn soft" type="button" onclick="navigator.clipboard.writeText('{url}');this.textContent='Link copied'">Copy link</button>
    </div>
    <div class="sources"><b>Sources</b><ol>{srcs}</ol></div>
  </article>
"""
    pg += foot()
    write(f"/blog/{p['slug']}/", pg)

# ---------- SHARE ----------
feat = fix_paths(P["feat"]).replace('id="featured"', 'id="featured" style="background:none"')
pg = head("Share a story", "Have a Rio Grande Valley rescue story? Share it with Howlback to be featured in the newsletter.", "/share/")
pg += header("/share/") + '  <div style="padding-top:16px"></div>\n' + feat + "\n" + foot()
write("/share/", pg)

# ---------- APP ----------
pg = head("The Howlback app", "Howlback is a coming-soon app where neighbors follow foster dogs and chip in toward their verified vet bills, food, and supplies.", "/app/", "/img/app/screen-1.webp")
pg += header("/app/")
pg += """  <div class="wrap app-hero">
    <div style="display:flex;flex-direction:column;gap:18px">
      <span class="soon-tag">Coming soon</span>
      <h1 style="font-size:clamp(38px,5.4vw,60px)">Can’t foster? You can still help.</h1>
      <p class="lead">Howlback is an app launching in the Rio Grande Valley, where an estimated 750,000 to 1 million stray animals live on the streets. Fosters get paid back for what they spend on street dogs, and neighbors chip in to help.</p>
      <a class="btn" href="#join" data-focus-email style="align-self:flex-start">Get first word at launch</a>
    </div>
    <div class="phones">
      <img src="/img/app/screen-1.webp" alt="App home screen with a feed of foster dogs near you">
      <img src="/img/app/screen-2.webp" alt="A foster dog's profile with verified receipts">
    </div>
  </div>

  <section class="how" style="background:var(--mint)">
    <div class="wrap">
      <div class="head"><h2>How it will work</h2></div>
      <ol class="app-steps">
        <li><h3>A neighbor fosters a dog</h3><p class="muted">Someone finds a dog on the street and takes them in. They make a profile for the dog with photos and their story: where they were found, what shape they were in, and what they need.</p><p class="muted">Fosters verify their ID once. Every few days they take a quick live photo check-in in the app, so everyone knows the dog is still in their care.</p></li>
        <li><h3>They add their receipts</h3><p class="muted">Every time the foster pays for something, they snap the receipt: vet visits, vaccines, flea and heartworm meds, food, a crate, a leash.</p><p class="muted">Each receipt is checked before it counts, and only receipts from businesses qualify. Bigger vet bills are confirmed directly with the vet clinic. The dog’s total is only what’s already been spent, never a guess or a wish list.</p></li>
        <li><h3>Neighbors chip in</h3><p class="muted">Anyone can follow a dog, cheer them on, and chip in any amount toward their verified costs. You see exactly which receipts your help covers.</p><p class="muted">The foster gets paid back for what they spent, and you get a note when the dog finds a home.</p></li>
      </ol>
    </div>
  </section>

  <section>
    <div class="wrap">
      <div class="feature">
        <div class="fcopy"><h2>Every dollar tied to a receipt</h2><p class="lead">Fosters upload receipts from vets, clinics, and pet stores. Each one is checked before it shows on the dog’s profile, so you can see exactly what your help covers.</p>
          <ul class="checks">
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>Only verified business receipts get paid back</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>Bigger vet bills are confirmed with the vet clinic</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>Store items need a photo of the item next to its receipt</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>Fosters verify their ID before their first payback</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>Live photo check-ins every few days show the dog is still in their care</li>
          </ul></div>
        <div class="fimg" style="display:grid"><img src="/img/app/screen-2.webp" alt="A foster dog's profile showing verified receipts for a vet visit, vaccines, and food" loading="lazy"></div>
      </div>
      <div class="feature flip">
        <div class="fcopy"><h2>Proof they bought it</h2><p class="lead">For food, meds, and supplies, fosters snap the receipt and one photo of the items sitting next to it. The app reads the store, date, and total. Bigger vet bills are confirmed directly with the vet clinic.</p></div>
        <div class="fimg" style="display:grid"><img src="/img/app/screen-6.webp" alt="Add a receipt screen with a receipt photo, a slot for a photo of the items next to the receipt, and the store, date, and total read from it" loading="lazy"></div>
      </div>
      <div class="feature">
        <div class="fcopy"><h2>Proof the dog is still in their care</h2><p class="lead">Every few days, fosters take a live photo check-in inside the app. It’s stamped with the date, time, and place, and it can’t be an old photo from their camera roll. Miss check-ins and the dog’s profile pauses.</p></div>
        <div class="fimg" style="display:grid"><img src="/img/app/screen-5.webp" alt="Check-in screen with a live photo of a puppy stamped with the date, time, and place, and a row of past check-ins" loading="lazy"></div>
      </div>
      <div class="feature flip">
        <div class="fcopy"><h2>Chip in for a dog you care about</h2><p class="lead">Pick a dog, pick an amount, and it goes toward their verified costs. You’ll get their updates, and a note when they find a home.</p><span class="soon-tag">Chipping in opens when the app launches</span></div>
        <div class="fimg" style="display:grid"><img src="/img/app/screen-3.webp" alt="The chip in screen with amount options of 5, 10, and 25 dollars" loading="lazy"></div>
      </div>
      <div class="feature">
        <div class="fcopy"><h2>See dogs near you</h2><p class="lead">Find foster dogs in your part of the Valley, get an alert when a local dog finds a home, and lend a hand on the help board with rides and supplies.</p></div>
        <div class="fimg" style="display:grid"><img src="/img/app/screen-4.webp" alt="Near you screen with an adoption alert, nearby foster dogs, and a help board" loading="lazy"></div>
      </div>
      <p class="disclaim">Screens are an early preview. Names and amounts are examples.</p>
    </div>
  </section>
"""
pg += foot()
write("/app/", pg)


# ---------- INSTALL ----------
pg = head("Add Howlback to your home screen", "Add Howlback to your phone's home screen so it opens like an app. Steps for iPhone and Android.", "/install/", "/img/app/home-screen.webp")
pg += header("/install/")
pg += """  <div class="wrap page-head"><div class="head"><h1>Add Howlback to your home screen</h1><p class="lead">It takes 10 seconds. Howlback gets its own icon and opens full screen, just like an app. No app store needed.</p></div></div>
  <section class="page" style="padding-top:12px"><div class="wrap">
    <div class="install-hero"><img src="/img/app/home-screen.webp" alt="A phone home screen with the Howlback app icon next to other apps"></div>
    <button class="btn" id="install-btn" type="button" hidden style="width:100%;margin:8px 0 4px;padding:15px">Add Howlback to this phone</button>
    <div class="os-tabs" role="tablist" aria-label="Your device">
      <button role="tab" aria-selected="true" data-os="ios">iPhone</button>
      <button role="tab" aria-selected="false" data-os="android">Android</button>
    </div>
    <div data-panel="ios">
      <ol class="howto">
        <li><span>Open <b>howlback.app</b> in <b>Safari</b>.</span></li>
        <li><span>Tap the <span class="kbd"><svg viewBox="0 0 24 24"><path d="M12 3v12M8 7l4-4 4 4M5 12v8h14v-8"/></svg>Share</span> button at the bottom of the screen (on iPad it’s at the top).</span></li>
        <li><span>Scroll down and tap <b>Add to Home Screen</b>.</span></li>
        <li><span>Tap <b>Add</b>. Howlback now opens from your home screen, full screen.</span></li>
      </ol>
      <p class="muted" style="margin-top:18px">Want it in Safari favorites too? Tap <span class="kbd"><svg viewBox="0 0 24 24"><path d="M12 3v12M8 7l4-4 4 4M5 12v8h14v-8"/></svg>Share</span>, then <b>Add to Favorites</b>.</p>
    </div>
    <div data-panel="android" hidden>
      <ol class="howto">
        <li><span>Open <b>howlback.app</b> in <b>Chrome</b>.</span></li>
        <li><span>Tap the <span class="kbd"><svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="12" cy="19" r="1.4"/></svg>menu</span> (three dots, top right).</span></li>
        <li><span>Tap <b>Add to home screen</b> or <b>Install app</b>.</span></li>
        <li><span>Tap <b>Install</b>. Howlback shows up with your other apps.</span></li>
      </ol>
      <p class="muted" style="margin-top:18px">To bookmark it instead, tap <span class="kbd"><svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="12" cy="19" r="1.4"/></svg>menu</span>, then the ☆ star.</p>
    </div>
  </div></section>
"""
pg += foot()
write("/install/", pg)


# ---------- LOST & FOUND ----------
CITIES = ["Brownsville", "Harlingen", "San Benito", "Los Fresnos", "Port Isabel", "South Padre Island", "Rio Hondo",
          "Raymondville", "Mercedes", "Weslaco", "Donna", "Alamo", "San Juan", "Pharr", "McAllen", "Edinburg",
          "Mission", "Palmview", "La Joya", "Rio Grande City", "Roma", "Other RGV"]
city_opts = "".join(f'<option>{c}</option>' for c in CITIES)
SCAM = '<p class="lf-scam"><b>Stay safe:</b> never pay someone to return a pet, and meet in a public place. Scammers sometimes contact lost-pet posters asking for money.</p>'

LF_PAGES = ["Brownsville", "Harlingen", "McAllen", "Edinburg", "Mission", "Pharr", "Weslaco", "San Benito", "Mercedes", "Los Fresnos", "Port Isabel", "South Padre Island", "Rio Grande City", "San Juan", "Donna", "Raymondville"]
def slug(c): return c.lower().replace(" ", "-")
LF_LOCAL = {
    "Brownsville": "If your dog was picked up in Brownsville, check the Brownsville Animal Regulation &amp; Care Center in person: 416 FM 511, (956) 544-7351. Call ahead for hours.",
    "Harlingen": "If your dog was picked up in Harlingen, check the Harlingen Animal Shelter in person: 1106 Markowsky Ave, (956) 216-5250, Tuesday to Saturday, 1 to 6 PM. Strays are held at least 72 hours.",
}
city_links = " · ".join(f'<a href="/lost-found/{slug(c)}/">{c}</a>' for c in LF_PAGES)
def lf_board(city=None):
    opts = "".join(f'<option{" selected" if c == city else ""}>{c}</option>' for c in CITIES)
    extra = f'<p class="lf-local">{LF_LOCAL[city]}</p>' if city in LF_LOCAL else ""
    path = f"/lost-found/{slug(city)}/" if city else "/lost-found/"
    if city:
        pg = head(f"Lost and found dogs in {city}, TX", f"Lost or found a dog in {city}, Texas? See lost and found dogs in {city} and nearby, or post one free. Every post is checked before it goes live.", path)
    else:
        pg = head("Lost and found dogs in the RGV", "Lost or found a dog in the Rio Grande Valley? See lost and found dogs in Brownsville, Harlingen, McAllen, and across the Valley, or post one for free.", "/lost-found/")
    pg += header("/lost-found/")
    if city:
        pg += page_head(f"Lost and found dogs in {city}", f"Lost dogs and found strays in {city} and across the Rio Grande Valley. Free to post. Every post is checked before it goes up.")
    else:
        pg += page_head("Lost and found dogs", "Lost dogs and found strays across the Rio Grande Valley. Free to post. Every post is checked before it goes up.")
    pg += f"""  <section class="page" style="padding-top:8px"><div class="wrap lf">
        <a class="btn lf-post lf-red" href="/lost-found/post/">Post a lost or found dog</a>
        <div class="lf-filters">
          <div class="os-tabs" role="tablist" aria-label="Show">
            <button type="button" data-kind="all" aria-selected="true">All</button>
            <button type="button" data-kind="lost" aria-selected="false">Lost</button>
            <button type="button" data-kind="found" aria-selected="false">Found</button>
          </div>
          <select id="lf-city" aria-label="City"><option value="">All cities</option>{opts}</select>
        </div>
        <div id="lf-list" class="lf-list"><p class="muted lf-empty">Loading...</p></div>
        {SCAM}
        {extra}
    <p class="muted">Found a dog? See <a href="/help/">what to do first</a>. Lost your dog? Read <a href="/blog/lost-dog-rgv/">what to do first</a>.</p>
    <p class="lf-cities muted">Lost and found by city: {city_links}</p>
      </div></section>
      <dialog id="lf-msg" class="lf-dialog"><form method="dialog">
        <h3>Message the poster</h3>
        <p class="muted">Howlback passes your message along. Your contact info goes only to the poster.</p>
        <input type="hidden" name="post_id">
        <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <label>Your name<input name="from_name" maxlength="80"></label>
        <label>Your phone or email<input name="from_contact" required maxlength="120"></label>
        <label>Message<textarea name="message" required minlength="5" maxlength="1000" rows="4" placeholder="I think I saw this dog near..."></textarea></label>
        <p class="lf-note" aria-live="polite"></p>
        <div class="lf-act"><button class="btn" type="submit">Send</button><button class="btn soft" type="button" data-close>Cancel</button></div>
      </form></dialog>
    """
    pg += foot().replace('<script src="/site.js"></script>', '<script src="/site.js"></script>\n<script src="/lf.js"></script>')
    write(path, pg)
lf_board()
for _c in LF_PAGES:
    lf_board(_c)

pg = head("Post a lost or found dog", "Post a lost or found dog in the Rio Grande Valley for free. Add a photo, where and when, and how to reach you.", "/lost-found/post/")
pg += header("/lost-found/")
pg += page_head("Post a lost or found dog", "Free. It takes 2 minutes. We check every post before it goes live, usually the same day.")
pg += f"""  <section class="page" style="padding-top:8px"><div class="wrap lf">
    <form id="lf-form" class="lf-form" novalidate>
      <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <fieldset class="lf-kind"><legend>This dog is</legend>
        <label><input type="radio" name="kind" value="lost" required> Lost (my dog is missing)</label>
        <label><input type="radio" name="kind" value="found" checked> Found (I found a dog)</label>
      </fieldset>
      <label>Photo of the dog<input type="file" name="photo" accept="image/*" required></label>
      <div id="lf-preview" class="lf-preview"></div>
      <p class="muted small">Please crop out faces, house numbers, and license plates.</p>
      <label><span data-for="lost">Dog's name</span><span data-for="found">Dog's name (if you know it)</span><input name="dog_name" maxlength="60"></label>
      <div class="lf-only" data-only="lost">
        <div class="lf-two"><label>Breed or mix<input name="breed" maxlength="60" placeholder="Shepherd mix"></label>
        <label>Age<input name="age" maxlength="30" placeholder="About 3 years"></label></div>
        <div class="lf-two"><label>Wearing a collar?<select name="collar_lost"><option value="">Choose</option><option value="yes">Yes</option><option value="no">No</option><option value="not_sure">Not sure</option></select></label>
        <label>Microchipped?<select name="chip_lost"><option value="">Choose</option><option value="yes">Yes</option><option value="no">No</option><option value="not_sure">Not sure</option></select></label></div>
      </div>
      <div class="lf-only" data-only="found">
        <fieldset class="lf-kind"><legend>Where is the dog now?</legend>
          <label><input type="radio" name="with_finder" value="with_me"> Safe with me</label>
          <label><input type="radio" name="with_finder" value="loose"> Still loose in the area</label>
        </fieldset>
        <div class="lf-two"><label>Collar or tag?<select name="collar_found"><option value="">Choose</option><option value="yes">Yes</option><option value="no">No</option></select></label>
        <label>Scanned for a microchip?<select name="chip_found"><option value="">Choose</option><option value="yes">Yes</option><option value="no">No</option><option value="not_sure">Not sure</option></select></label></div>
        <label>Anything written on the collar or tag?<input name="tag_text" maxlength="120"></label>
        <label>Does the dog seem hurt?<select name="hurt"><option value="">Choose</option><option value="no">No</option><option value="yes">Yes</option><option value="not_sure">Not sure</option></select></label>
      </div>
      <label>Friendly or scared?<select name="temperament"><option value="">Choose</option><option value="friendly">Friendly, comes to people</option><option value="scared">Scared, may run</option><option value="not_sure">Not sure</option></select></label>
      <label>City<select name="city" required><option value="">Choose a city</option>{city_opts}</select></label>
      <label><span data-for="lost">Last seen near</span><span data-for="found">Found near</span><input name="area" maxlength="120" placeholder="Near Boca Chica and Central"></label>
      <p class="muted small">Cross streets or a landmark. Don't put an exact home address.</p>
      <label><span data-for="lost">Date last seen</span><span data-for="found">Date found</span><input type="date" name="seen_on"></label>
      <label>Anything else?<textarea name="description" required minlength="10" maxlength="1000" rows="4" placeholder="Color, size, markings, how they act"></textarea></label>
      <h3>How can people reach you?</h3>
      <label>Your name<input name="contact_name" maxlength="80"></label>
      <label>Phone<input type="tel" name="contact_phone" maxlength="30"></label>
      <label>Email<input type="email" name="contact_email" maxlength="120"></label>
      <label class="lf-check"><input type="checkbox" name="show_phone"> Show my phone number on the post</label>
      <p class="muted small">If you leave this unchecked, your number stays hidden and people message you through Howlback.</p>
      {SCAM}
      <p id="lf-status" class="lf-note" aria-live="polite"></p>
      <button class="btn" type="submit">Submit for review</button>
    </form>
    <div id="lf-done" class="lf-done" hidden>
      <h2>Thanks! Your post is in. 🐾</h2>
      <p>We check every post before it goes live, usually the same day. Meanwhile, post in your city's lost and found group too.</p>
      <div class="lf-save"><b>Save this link.</b> When your dog is home (or the found dog is back with their family), open it and tap <b>Reunited</b>. Screenshot it or copy it somewhere safe.
        <input id="lf-link" readonly aria-label="Your private link"><button class="btn soft" id="lf-copy-link" type="button">Copy my link</button></div>
      <a class="btn" href="/lost-found/">See lost and found dogs</a>
    </div>
  </div></section>
"""
pg += foot().replace('<script src="/site.js"></script>', '<script src="/site.js"></script>\n<script src="/lf.js"></script>')
write("/lost-found/post/", pg)

pg = head("Update your post", "Mark your lost or found dog post as reunited.", "/lost-found/update/").replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"')
pg += header("/lost-found/")
pg += page_head("Is your dog home?", "Tap below and your post will say REUNITED for 24 hours, then it comes down.")
pg += """  <section class="page" style="padding-top:8px"><div class="wrap lf" id="lf-update">
    <button class="btn lf-post" id="lf-reunite" type="button">Yes, mark it Reunited 🎉</button>
    <p id="lf-upd-note" class="lf-note" aria-live="polite"></p>
    <a href="/lost-found/">Back to lost and found</a>
  </div></section>
"""
pg += foot().replace('<script src="/site.js"></script>', '<script src="/site.js"></script>\n<script src="/lf.js"></script>')
write("/lost-found/update/", pg)

pg = head("Admin", "Howlback admin", "/admin/").replace('<meta name="description"', '<meta name="robots" content="noindex, nofollow">\n<meta name="description"')
pg += """<main id="lf-admin" class="wrap lf" style="padding:28px 20px 60px">
  <h1 style="font-size:30px!important">Lost &amp; found admin</h1>
  <form id="lf-login" hidden><p>Log in with a one-time link sent to hello@howlback.app.</p><button class="btn" type="submit">Email me a login link</button><p class="lf-note" aria-live="polite"></p></form>
  <div id="lf-panel" hidden>
    <h2>Waiting for review (<span id="lf-count">0</span>)</h2><div id="lf-pending" class="lf-list"></div>
    <h2>Messages to forward</h2><div id="lf-msgs"></div>
    <h2>Live posts</h2><div id="lf-live" class="lf-list"></div>
    <button class="btn soft" id="lf-logout" type="button">Log out</button>
  </div>
</main>
</div>
<script src="/lf.js"></script>
</body>
</html>
"""
write("/admin/", pg)


# ---------- MUST-HAVES (affiliate page) ----------
SHOP = json.load(open(os.path.join(ROOT, "src/shop.json")))
def shop_item(it, checklist):
    name, why, link = html.escape(it["name"]), html.escape(it["why"]), it.get("link", "")
    if checklist:
        btn = f'<a class="btn soft sm" href="{link}" target="_blank" rel="sponsored noopener">View on Amazon</a>' if link else ""
        return f'<li class="chk"><div><b>{name}</b><span>{why}</span></div>{btn}</li>\n'
    code = it.get("code", "")
    deal = html.escape(it.get("deal", ""))
    codebox = (f'<button class="code" type="button" data-copy="{html.escape(code)}">Code <b>{html.escape(code)}</b><small>Tap to copy</small></button>' if code else "")
    btn = f'<a class="btn" href="{link}" target="_blank" rel="sponsored noopener">Shop {name}</a>' if link else ""
    img = f'<img class="prod-img" src="{it["img"]}" alt="{html.escape(it.get("alt",""))}" loading="lazy">' if it.get("img") else ""
    return (f'<li class="prod">{img}<div class="prod-top"><b>{name}</b>{f"<span class=deal>{deal}</span>" if deal else ""}</div>'
            f'<p>{why}</p><div class="prod-act">{btn}{codebox}</div></li>\n')

pg = head("New to fostering? Must-haves", "Everything you need when you foster or take in a dog in the Rio Grande Valley: day one basics, food, grooming, and calming picks, with discount codes.", "/must-haves/", "/img/rescue-dog.jpg")
pg += header("/must-haves/")
pg += page_head("New to fostering? Must-haves", "What to have ready when a dog comes home with you, plus discount codes on brands we like.")
disclose = "Some links on this page earn Howlback a small commission, at no extra cost to you."
if SHOP.get("amazon_tag"):
    disclose += " As an Amazon Associate, Howlback earns from qualifying purchases."
pg += f'  <section class="page" style="padding-top:8px"><div class="wrap shop">\n    <p class="disclose">{disclose}</p>\n'
for s in SHOP["sections"]:
    chk = s.get("checklist", False)
    items = [i for i in s["items"] if chk or (i.get("show", True) and (i.get("link") or i.get("code")))]
    if not items:
        continue
    pg += f'    <div class="shop-sec"><h2>{html.escape(s["title"])}</h2>' + (f'<p class="muted">{html.escape(s["intro"])}</p>' if s.get("intro") else "")
    pg += f'<ul class="{"chklist" if chk else "prods"}">\n' + "".join(shop_item(i, chk) for i in items) + '</ul></div>\n'
pg += '    <div class="shop-sec vetnote"><h2>Get these from a vet</h2><p>Vaccines, dewormer, and flea, tick, and heartworm prevention are cheapest at low-cost clinics. See <a href="/clinics/">upcoming clinics</a>, or read <a href="/blog/cost-to-foster-a-dog-rgv/">what it costs to foster a dog in the RGV</a>.</p></div>\n'
pg += '  </div></section>\n'
pg += foot()
write("/must-haves/", pg)


# ---------- PLACES (dog-friendly map) ----------
PLACES = json.load(open(os.path.join(ROOT, "src/places.json")))
pg = head("Dog-friendly places in the RGV", "Dog-friendly trails, beaches, dog parks, and patios in Brownsville, South Padre Island, Harlingen, San Benito, and Los Fresnos, on one map. Trails list parking, distance, and if they're paved.", "/places/", "/img/rescue-dog.jpg")
pg = pg.replace('<link rel="stylesheet" href="/style.css">', '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">\n<link rel="stylesheet" href="/style.css">')
pg += header("/places/")
pg += page_head("Dog-friendly places", "Trails, beaches, dog parks, and patios around the Valley. Tap a pin or a card for details and directions. Policies change, so call ahead before you go.")
cities = ["Brownsville", "South Padre Island", "Harlingen", "San Benito", "Los Fresnos"]
types = [("trail", "🥾 Trails"), ("dogpark", "🐕 Dog parks"), ("beach", "🏖️ Beaches"), ("park", "🌳 Parks"), ("food", "🍔 Food & drinks")]
pg += '  <section class="page" style="padding-top:8px"><div class="wrap places">\n'
pg += '    <div class="pl-filters"><div class="pl-row" id="pl-city"><button type="button" class="on" data-v="">All cities</button>' + "".join(f'<button type="button" data-v="{c}">{c}</button>' for c in cities) + '</div>\n'
pg += '    <div class="pl-row" id="pl-type"><button type="button" class="on" data-v="">Everything</button>' + "".join(f'<button type="button" data-v="{k}">{t}</button>' for k, t in types) + '</div></div>\n'
pg += '    <div id="pl-map" role="region" aria-label="Map of dog-friendly places"></div>\n    <p class="muted pl-count" id="pl-count"></p>\n    <ul class="pl-list" id="pl-list"></ul>\n'
pg += '    <p class="muted pl-foot">Know a spot we missed? Email <a href="mailto:hello@howlback.app">hello@howlback.app</a>. Always leash up, bring water, and skip hot pavement midday.</p>\n'
pg += '  </div></section>\n'
pg += '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>\n<script>window.PLACES=' + json.dumps(PLACES) + ';</script>\n<script src="/places.js"></script>\n'
pg += foot()
write("/places/", pg)

# ---------- LINKS (link in bio) ----------
latest = sorted(enumerate(POSTS), key=lambda x: (x[1]["date"], x[0]))[-1][1]
LINKS = [
    ("/lost-found/", "🚨 Lost or found a dog? 🚨", "Post it free so the whole Valley can help get them home", "sos"),
    ("/", "Visit howlback.app", "Local help, clinics, and rescues across the RGV", "main"),
    (f"/blog/{latest['slug']}/", "New on the blog", latest["title"], False),
    ("/blog/", "All blog posts", "Laws, local guides, and RGV dog news", False),
    ("/clinics/", "Clinics and events", "Low-cost shots, spay and neuter, adoption days", False),
    ("/help/", "Found a dog?", "Who to call in your city", False),
    ("/places/", "Dog-friendly places", "Trails, beaches, dog parks, and patios on a map", False),
    ("/must-haves/", "New to fostering? Must-haves", "Day one basics, food, and discount codes", False),
    ("/#join", "Get app updates", "One email or text when the app launches", False),
    ("/app/", "The Howlback app", "Coming soon to the RGV", False),
]
SOCIAL = [("https://www.instagram.com/howlback.app", "Instagram"),
          ("https://www.facebook.com/profile.php?id=61595201828343", "Facebook")]
pg = head("Links", "Howlback links: the website, the blog, local help, clinics, and app updates for the Rio Grande Valley.", "/links/")
pg += '<main class="links-page">\n  <div class="links-top"><img src="/img/icon-192.png" alt="" width="84" height="84"><h1>howl<i>back</i></h1><p>Can\'t foster? Help someone who can 🐾<br>Street dog help across the Rio Grande Valley.</p></div>\n  <div class="links-list">\n'
for h, t, s, main in LINKS:
    pg += f'    <a class="lnk{" " + main if main else ""}" href="{h}"><b>{html.escape(t)}</b><span>{html.escape(s)}</span></a>\n'
pg += '  </div>\n  <div class="links-social">' + "".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for u, n in SOCIAL) + '</div>\n</main>\n</div>\n<script src="/site.js"></script>\n</body>\n</html>\n'
write("/links/", pg)


# ---------- SITEMAP + ROBOTS ----------
pages = ["/", "/help/", "/clinics/", "/rescues/", "/blog/", "/lost-found/", "/lost-found/post/", *[f"/lost-found/{slug(c)}/" for c in LF_PAGES], "/must-haves/", "/places/", "/share/", "/app/", "/install/"] + [f"/blog/{p['slug']}/" for p in POSTS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in pages:
    sm += f"  <url><loc>{SITE}{u}</loc></url>\n"
sm += "</urlset>\n"
open(os.path.join(ROOT, "sitemap.xml"), "w").write(sm)
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /lost-found/update/\nSitemap: {SITE}/sitemap.xml\n")


# ---------- GITHUB PAGES EXTRAS ----------
open(os.path.join(ROOT, "CNAME"), "w").write("howlback.app\n")
open(os.path.join(ROOT, ".nojekyll"), "w").write("")
for slug in [p["slug"] for p in POSTS] + [""]:
    target = f"/blog/{slug}/" if slug else "/blog/"
    d = os.path.join(ROOT, "stories", slug) if slug else os.path.join(ROOT, "stories")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{SITE}{target}"><meta http-equiv="refresh" content="0; url={target}"><a href="{target}">This page moved</a>\n')
nf = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found | Howlback</title><link rel="stylesheet" href="/style.css"></head><body><div class="shell"><div class="wrap page-head"><div class="head"><h1>Page not found</h1><p class="lead">That page moved or doesn't exist.</p><a class="btn" href="/" style="align-self:flex-start">Go to the homepage</a></div></div></div></body></html>"""
open(os.path.join(ROOT, "404.html"), "w").write(nf.replace('"/style.css"', f'"/style.css?v={VER["/style.css"]}"'))

# ---------- CSS ----------
base = open(os.path.join(ROOT, "src/base.css")).read()
extra = open(os.path.join(ROOT, "src/extra.css")).read()
open(os.path.join(ROOT, "style.css"), "w").write(base + "\n" + extra)
print("built")
