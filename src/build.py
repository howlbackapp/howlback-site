"""Builds the Howlback site pages from shared pieces.

Run from the repo root:  python3 src/build.py
Edit words in src/parts.json, src/posts.json, or the page templates below, then rebuild.
"""
import json, os, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "src/parts.json")))
POSTS = json.load(open(os.path.join(ROOT, "src/posts.json")))
SITE = "https://howlback.app"

NAV = [("/help/", "Local help"), ("/clinics/", "Clinics"), ("/rescues/", "Rescues"),
       ("/blog/", "Blog"), ("/app/", "The app"), ("/share/", "Share a story"),
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

def head(title, desc, path, img="/img/street-dog.jpg"):
    full = title if title == "Howlback" else f"{title} | Howlback"
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
<meta property="og:image" content="{SITE}{img}">
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

def write(path, content):
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(content)

def card(p):
    img = (f'<img src="/img/{p["img"]}" alt="{html.escape(p["alt"])}" loading="lazy">' if p["img"]
           else f'<span class="noimg">{html.escape(p["title"])}</span>')
    return (f'<a class="card" href="/blog/{p["slug"]}/">{img}<span class="topic">{p["topic"]}</span>'
            f'<h3>{html.escape(p["title"])}</h3><p class="muted">{html.escape(p["desc"].split(". ")[0].rstrip("."))}.</p></a>')

# ---------- HOME ----------
hero = fix_paths(P["hero"])
hero = hero.replace('class="wrap hero"', 'class="wrap hero home-hero"')
hero = re.sub(r'<a class="where soon-pill"[^>]*>.*?</a>',
              '<a class="where soon-pill" href="/app/">The app is coming soon. Take a peek</a>', hero)
hero = hero.replace('href="#help"', 'href="/help/"').replace('href="#stories"', 'href="/blog/"')

home = head("Howlback", "Local help for street dogs in the Rio Grande Valley: who to call, low-cost vets, vaccine clinics, rescues, and stories from South Texas.", "/")
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
pg = head("Local help", "Who to call in the Rio Grande Valley: shelters, animal control, low-cost vets, urgent vets, pet food help, and pet stores.", "/help/")
pg += header("/help/") + page_head("Local help in the Valley", "Shelters, animal control, low-cost vets, and pet food help. Hours change often, so call ahead.")
pg += '  <section class="page"><div class="wrap" style="display:flex;flex-direction:column">\n'
pg += P["found"] + P["tools"] + "\n  </div></section>\n" + foot()
write("/help/", pg)

# ---------- CLINICS ----------
pg = head("Vaccine clinics", "Free and low-cost dog vaccine and microchip clinics coming up around the Rio Grande Valley.", "/clinics/")
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
    cover = f'<img class="cover" src="/img/{p["img"]}" alt="{html.escape(p["alt"])}">' if p["img"] else ""
    srcs = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in p["sources"])
    url = f"{SITE}/blog/{p['slug']}/"
    pg = head(p["title"], p["desc"], f"/blog/{p['slug']}/", f"/img/{p['img'] or 'street-dog.jpg'}")
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
      <p class="disclaim">Screens are an early preview. Names and amounts are examples. Photos by Nikki Bee.</p>
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


# ---------- SITEMAP + ROBOTS ----------
pages = ["/", "/help/", "/clinics/", "/rescues/", "/blog/", "/share/", "/app/", "/install/"] + [f"/blog/{p['slug']}/" for p in POSTS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in pages:
    sm += f"  <url><loc>{SITE}{u}</loc></url>\n"
sm += "</urlset>\n"
open(os.path.join(ROOT, "sitemap.xml"), "w").write(sm)
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


# ---------- GITHUB PAGES EXTRAS ----------
open(os.path.join(ROOT, "CNAME"), "w").write("howlback.app\n")
open(os.path.join(ROOT, ".nojekyll"), "w").write("")
for slug in [p["slug"] for p in POSTS] + [""]:
    target = f"/blog/{slug}/" if slug else "/blog/"
    d = os.path.join(ROOT, "stories", slug) if slug else os.path.join(ROOT, "stories")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{SITE}{target}"><meta http-equiv="refresh" content="0; url={target}"><a href="{target}">This page moved</a>\n')
nf = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found | Howlback</title><link rel="stylesheet" href="/style.css"></head><body><div class="shell"><div class="wrap page-head"><div class="head"><h1>Page not found</h1><p class="lead">That page moved or doesn't exist.</p><a class="btn" href="/" style="align-self:flex-start">Go to the homepage</a></div></div></div></body></html>"""
open(os.path.join(ROOT, "404.html"), "w").write(nf)

# ---------- CSS ----------
base = open(os.path.join(ROOT, "src/base.css")).read()
extra = open(os.path.join(ROOT, "src/extra.css")).read()
open(os.path.join(ROOT, "style.css"), "w").write(base + "\n" + extra)
print("built")
