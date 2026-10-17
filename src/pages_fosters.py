# Foster dashboard, public dog pages, and policy pages. Exec'd from build.py (shares its helpers).

FB_JS = '<script src="/fosters.js"></script>'
NOINDEX = True  # flip to False at launch
def hide(pg):
    return pg.replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"', 1) if NOINDEX else pg
def with_js(pg):
    pg = hide(pg)
    return pg.replace('<script src="/site.js"></script>', '<script src="/site.js"></script>\n' + FB_JS)
city_opts2 = "".join(f'<option>{c}</option>' for c in CITIES)

# ---------- FOSTER DASHBOARD ----------
pg = head("Chip In for fosters", "Chip In by Howlback: fostering a dog in the Rio Grande Valley? Make a profile for your foster dog, upload receipts, and get paid back by supporters.", "/foster/")
pg += header("/foster/")
pg += f"""  <section class="page" style="padding-top:8px"><div class="wrap fb" id="fb-dash">
    <div data-step="login">
      <div class="fi-hero">
        <div class="fi-copy">
          <span class="soon-tag">Chip In by Howlback · for fosters</span>
          <h1>Fostering a dog? <span style="color:var(--peach-ink)">Get paid back.</span></h1>
          <p class="lead">You’re already paying for the vet, the meds, and the food out of your own pocket. Chip In lets your neighbors help cover it. Add your foster dog, upload your receipts, and people across the Valley chip in to pay you back.</p>
          <a class="btn" href="#fb-signup">Sign up free</a>
        </div>
        <div class="phones fi-phones">
          <img src="/img/app/screen-7.webp" alt="Foster dashboard showing $94 paid back of $129 spent, with a payment on its way to the bank and a list of verified receipts">
          <img src="/img/app/screen-8.webp" alt="Phone lock screen with Howlback alerts: paid back, someone chipped in $10, and receipt verified">
        </div>
      </div>

      <h2 class="fi-h">How it works</h2>
      <div class="fi-steps">
        <figure><img src="/img/app/screen-2.webp" alt="A foster dog's profile with a photo, story, and verified receipts" loading="lazy"><figcaption><b>1. Add your dog</b>A photo and their story: where you found them and what they need.</figcaption></figure>
        <figure><img src="/img/app/screen-6.webp" alt="Add a receipt screen with a photo of the receipt and the store, date, and total" loading="lazy"><figcaption><b>2. Upload receipts</b>Snap the receipt. We check every one before it goes up.</figcaption></figure>
        <figure><img src="/img/app/screen-3.webp" alt="Chip in screen with amount options of 5, 10, and 25 dollars" loading="lazy"><figcaption><b>3. Neighbors chip in</b>Anyone can chip in any amount toward your receipts.</figcaption></figure>
        <figure><img src="/img/app/screen-7.webp" alt="Foster dashboard showing money paid back to the bank" loading="lazy"><figcaption><b>4. Get paid back</b>The money goes straight to your bank through Stripe.</figcaption></figure>
      </div>
      <p class="fi-swipe muted">Swipe to see all 4 →</p>

      <div class="fi-why">
        <div><span>💚</span><b>Free for fosters</b><p>No sign-up fee and nothing taken out of your money. Supporters cover Howlback’s small fee on top.</p></div>
        <div><span>🧾</span><b>What counts</b><p>Vet visits, meds, food, supplies, toys, and grooming for the dog you’re fostering.</p></div>
        <div><span>🏦</span><b>Safe payouts</b><p>Stripe sends the money to your bank. Howlback never sees your bank info.</p></div>
        <div><span>🐾</span><b>Anyone fostering</b><p>You don’t have to be a rescue group. If you took in a dog in the RGV, you can sign up.</p></div>
      </div>

      <details class="fi-faq"><summary>How do I know I’ll get paid back?</summary><p>Each receipt shows how much is covered so far. As people chip in, the money goes to your bank. We share foster dogs on Howlback to help them get seen.</p></details>
      <details class="fi-faq"><summary>What do you check on my receipts?</summary><p>That it shows the business name, date, and total, and that it’s for your foster dog. Big vet bills may be confirmed with the clinic.</p></details>
      <details class="fi-faq"><summary>When can I start?</summary><p>Sign up and add your dog now. Payouts open when Chip In launches, and early sign-ups go first.</p></details>
      <p class="muted" style="font-size:13px;margin-top:10px">App screens are a preview. Names and amounts are examples.</p>

      <h2 class="fi-h" id="fb-signup">Sign up free</h2>
      <form id="fb-login" class="fb-form">
        <label>Your email<input type="email" name="email" required autocomplete="email"></label>
        <button class="btn" type="submit">Email me a sign-in link</button>
        <p class="fb-note" aria-live="polite"></p>
        <p class="muted">Free for fosters. See <a href="/how-it-works/">how it works</a>.</p>
      </form>
    </div>
    <div data-step="profile" hidden>
      <h2>Tell us about you</h2>
      <form id="fb-profile" class="fb-form">
        <label>Your name<input name="name" required maxlength="80" autocomplete="name"></label>
        <label>City<select name="city" required><option value="">Choose a city</option>{city_opts2}</select></label>
        <label>Phone (only Howlback sees this)<input name="phone" type="tel" maxlength="30" autocomplete="tel"></label>
        <label>About you (optional)<textarea name="about" rows="3" maxlength="1000" placeholder="How you started fostering, how many dogs you’ve helped..."></textarea></label>
        <label class="fb-check"><input type="checkbox" name="agree"> I agree to the <a href="/terms/" target="_blank">terms</a> and will only upload real receipts for the dog I’m fostering.</label>
        <button class="btn" type="submit">Save and continue</button>
        <p class="fb-note" aria-live="polite"></p>
      </form>
    </div>
    <div data-step="home" hidden>
      <div class="fb-top"><h2 id="fb-hello"></h2><button class="btn soft sm" id="fb-logout" type="button">Sign out</button></div>
      <p id="fb-status" class="fb-statusline"></p>
      <div id="fb-bank" class="fb-bank" hidden><p><b>Connect your bank to get paid.</b> Stripe handles it securely and checks your ID. Howlback never sees your bank info.</p><button class="btn" id="fb-bank-btn" type="button">Connect my bank</button><p class="fb-note" aria-live="polite"></p></div>
      <div class="fb-totals" id="fb-totals"></div>
      <h2>Your dogs</h2>
      <div id="fb-dogs"></div>
      <details class="fb-add"><summary class="btn soft">+ Add a dog</summary>
        <form id="fb-dog" class="fb-form">
          <label>Photo<input type="file" name="photo" accept="image/*" required></label><div id="fb-dog-prev" class="fb-prev"></div>
          <label>Name<input name="name" required maxlength="60"></label>
          <div class="fb-two"><label>Boy or girl<select name="sex"><option value="">Choose</option><option value="male">Boy</option><option value="female">Girl</option><option value="unknown">Not sure</option></select></label>
          <label>Age<input name="age" maxlength="30" placeholder="About 2 years"></label></div>
          <label>Breed or mix<input name="breed" maxlength="60" placeholder="Shepherd mix"></label>
          <label>City<select name="city" required><option value="">Choose a city</option>{city_opts2}</select></label>
          <label>Their story<textarea name="story" rows="5" required minlength="20" maxlength="2000" placeholder="Where you found them, how they’re doing, what they need, what they’re like..."></textarea></label>
          <button class="btn" type="submit">Add dog</button><p class="fb-note" aria-live="polite"></p>
        </form>
      </details>
      <div id="fb-receipt-box" hidden>
        <h2>Upload a receipt</h2>
        <p class="muted">Vet visits, medication, food, supplies, toys, or grooming. It has to show the business name, date, and total. We check every receipt before supporters see it.</p>
        <form id="fb-receipt" class="fb-form">
          <label>Which dog<select name="dog_id" required></select></label>
          <label>What for<select name="category" required><option value="vet">Vet visit</option><option value="meds">Medication</option><option value="food">Food</option><option value="supplies">Supplies</option><option value="toys">Toys</option><option value="grooming">Grooming</option><option value="other">Other</option></select></label>
          <label>Business name<input name="business" required maxlength="100" placeholder="Boca Chica Animal Hospital"></label>
          <div class="fb-two"><label>Total ($)<input name="amount" type="number" min="1" step="0.01" required inputmode="decimal"></label>
          <label>Date on receipt<input name="spent_on" type="date" required></label></div>
          <label>Note for supporters (optional)<input name="note" maxlength="300" placeholder="Parvo test and first round of shots"></label>
          <label>Receipt photo or PDF<input type="file" name="file" accept="image/*,application/pdf" required></label>
          <button class="btn" type="submit">Send receipt</button><p class="fb-note" aria-live="polite"></p>
        </form>
      </div>
    </div>
  </div></section>
"""
pg += foot()
write("/foster/", with_js(pg))

# ---------- BROWSE DOGS ----------
pg = head("Chip In: foster dogs who need help in the RGV", "Chip In by Howlback. Foster dogs across the Rio Grande Valley with verified vet bills, food, and supply receipts. Chip in any amount to pay their foster back.", "/dogs/")
pg += header("/dogs/")
pg += page_head("Chip In", "<b>by Howlback.</b> Can’t foster? You can still help. Every receipt is verified by Howlback, and your chip-in pays the foster back.")
pg += f"""  <section class="page" style="padding-top:8px"><div class="wrap fb">
    <div class="fb-filters"><select id="fb-city" aria-label="City"><option value="">All cities</option>{city_opts2}</select>
    <a class="btn soft sm" href="/foster/">I’m a foster</a></div>
    <div id="fb-grid" class="fb-grid"><p class="muted">Loading...</p></div>
    <p class="muted">How it works: fosters upload receipts, we verify them, you chip in, and the foster gets paid back. <a href="/how-it-works/">Read more</a>.</p>
  </div></section>
"""
pg += foot()
write("/dogs/", with_js(pg))

# ---------- ONE DOG ----------
pg = head("Help a foster dog", "Help cover a foster dog’s verified vet bills, food, and supplies in the Rio Grande Valley.", "/dogs/view/")
pg += header("/dogs/")
pg += """  <section class="page"><div class="wrap fb"><div id="fb-view"><p class="muted">Loading...</p></div>
    <p class="muted fb-fine">Howlback is a for-profit business. Chip-ins pay a foster back for verified costs and can’t be written off on your taxes. <a href="/how-it-works/">How it works</a> · <a href="/refunds/">Refunds</a></p></div></section>
  <dialog id="fb-chip" class="lf-dialog fb-dialog"><form method="dialog">
    <h3 id="fb-chip-title">Chip in</h3><p class="muted" id="fb-chip-sub"></p>
    <p class="fb-lbl">Amount</p>
    <div class="fb-pills"><button type="button" data-amt="5">$5</button><button type="button" data-amt="10">$10</button><button type="button" data-amt="25">$25</button><button type="button" data-amt="50">$50</button><button type="button" data-amt="rest">All of it</button></div>
    <label class="fb-amt">$<input name="amount" type="number" min="1" step="0.01" inputmode="decimal" placeholder="Other amount"></label>
    <p class="fb-lbl">Howlback fee <span class="muted">($1 + a percentage, keeps the site running)</span></p>
    <div class="fb-pills"><button type="button" data-pct="8" class="on">8%</button><button type="button" data-pct="10">10%</button><button type="button" data-pct="12">12%</button><button type="button" data-pct="15">15%</button><button type="button" data-pct="custom">Other</button></div>
    <label class="fb-amt" hidden><input name="pct" type="number" min="8" max="50" step="1" value="8" aria-label="Fee percent">%</label>
    <label>Your name (optional, shown on the page)<input name="sname" maxlength="60" placeholder="Leave blank to show “Someone”"></label>
    <label>Note for the foster (optional)<input name="snote" maxlength="200"></label>
    <div id="fb-sum" class="fb-sum"></div>
    <p class="lf-note" id="fb-chip-note" aria-live="polite"></p>
    <div class="lf-act"><button class="btn" type="submit">Continue to secure checkout</button><button class="btn soft" type="button" data-close>Cancel</button></div>
    <p class="muted fb-fine">Cards are handled by Stripe. Howlback never sees your card number.</p>
  </form></dialog>
"""
pg += foot()
write("/dogs/view/", with_js(pg))

# ---------- POLICY PAGES ----------
def policy(path, title, desc, body):
    pg = head(title, desc, path)
    pg += header(path)
    pg += page_head(title, '<span class="muted">Last updated October 16, 2026</span>')
    pg += f'  <section class="page" style="padding-top:8px"><div class="wrap post-body policy">{body}</div></section>\n'
    pg += foot()
    write(path, hide(pg) if path == "/how-it-works/" else pg)

policy("/how-it-works/", "How Chip In works", "How Chip In by Howlback works: how fosters get paid back for verified dog care costs, and how supporters chip in on Howlback.", """
<p><b>Chip In by Howlback</b> lets neighbors help pay local fosters back for what they spend caring for street dogs.</p>
<h2>For supporters</h2>
<ol><li><b>Pick a dog.</b> Every dog on Howlback is in the care of a local foster in the Rio Grande Valley.</li>
<li><b>See verified receipts.</b> Fosters upload receipts for vet visits, medication, food, supplies, toys, and grooming. Howlback checks each one before it shows up.</li>
<li><b>Chip in any amount</b> toward a receipt, from $1 up to what’s still needed.</li>
<li><b>The foster gets paid back.</b> Your chip-in goes to the foster’s bank account through Stripe.</li></ol>
<h2>The Howlback fee</h2>
<p>Each chip-in has a Howlback fee of <b>$1 plus 8%</b> of the amount, added on top. You can choose a higher percentage if you’d like to help keep Howlback running. The foster always gets the full amount you chip in toward their receipt.</p>
<table class="policy-table"><tr><th>You chip in</th><th>Fee at 8%</th><th>You pay</th><th>Foster gets</th></tr>
<tr><td>$10</td><td>$1.80</td><td>$11.80</td><td>$10</td></tr>
<tr><td>$25</td><td>$3.00</td><td>$28.00</td><td>$25</td></tr>
<tr><td>$50</td><td>$5.00</td><td>$55.00</td><td>$50</td></tr></table>
<p>The fee covers card processing and the cost of running Howlback, including checking receipts.</p>
<h2>For fosters</h2>
<ol><li><b>Sign up</b> on the <a href="/foster/">foster page</a> with your email. It’s free.</li>
<li><b>Add your foster dog</b> with a photo and their story. We review it, usually within a day.</li>
<li><b>Upload receipts</b> that show the business name, date, and total.</li>
<li><b>Connect your bank</b> through Stripe, which verifies your identity.</li>
<li><b>Get paid back</b> as supporters chip in. Payouts usually reach your bank within a few business days.</li></ol>
<h2>What we check on every receipt</h2>
<ul><li>It’s from a real business, like a vet clinic, pet store, or feed store</li><li>The date and total are clear and match what was entered</li><li>It’s for dog care, not personal items</li><li>It hasn’t already been uploaded or paid back somewhere else</li></ul>
<h2>Good to know</h2>
<ul><li>Howlback is a for-profit business. Chip-ins pay a foster back for verified costs and can’t be written off on your taxes.</li>
<li>Payments are processed by Stripe. Howlback never sees or stores your card number.</li>
<li>Questions? Email <a href="mailto:hello@howlback.app">hello@howlback.app</a>.</li></ul>
<p>See also our <a href="/terms/">terms</a>, <a href="/refunds/">refund policy</a>, and <a href="/privacy/">privacy policy</a>.</p>""")

policy("/terms/", "Terms of use", "Howlback terms of use for supporters and fosters.", """
<p>These terms apply to everyone who uses howlback.app. By using the site, you agree to them. If you don’t agree, please don’t use Howlback.</p>
<h2>1. What Howlback is</h2>
<p>Howlback is a for-profit online service that connects people who foster dogs in the Rio Grande Valley with supporters who want to help pay them back for the cost of care. Howlback is not an animal shelter or rescue and does not take ownership of any animal.</p>
<h2>2. Who can use it</h2>
<p>You must be at least 18 years old to sign up as a foster or to make a payment. Fosters must live in Texas and have a U.S. bank account.</p>
<h2>3. Rules for fosters</h2>
<ul><li>Only list dogs that are actually in your care.</li>
<li>Only upload genuine receipts for costs you paid for that dog: vet care, medication, food, supplies, toys, or grooming.</li>
<li>Don’t upload a receipt that has already been paid back by anyone else, including a rescue, shelter, or another site.</li>
<li>Keep your dog’s profile accurate, and mark them adopted when they find a home.</li>
<li>To receive payouts, you must connect a bank account through Stripe and agree to the <a href="https://stripe.com/connect-account/legal" target="_blank" rel="noopener">Stripe Connected Account Agreement</a>. Stripe may ask for ID to verify who you are.</li>
<li>You’re responsible for any taxes on the money you receive.</li></ul>
<p>If we find a fake or altered receipt, we will remove the listing, cancel pending payouts, refund supporters where possible, and may close the account.</p>
<h2>4. Verification</h2>
<p>Howlback reviews every dog profile and receipt before it goes live. We check that receipts look genuine and match what was entered, but we can’t guarantee every detail. We may reject or remove any listing at any time.</p>
<h2>5. Payments and fees</h2>
<ul><li>Supporters can chip in toward any verified receipt, up to the amount still needed.</li>
<li>Each payment includes a Howlback fee of $1 plus a percentage of the amount (8% minimum), shown before you pay. You can choose a higher percentage.</li>
<li>Payments are processed by Stripe. The amount toward the receipt is sent to the foster’s connected account. The fee goes to Howlback.</li>
<li>Payments are not charitable gifts and are not tax deductions.</li>
<li>Refunds follow our <a href="/refunds/">refund policy</a>.</li></ul>
<h2>6. Lost &amp; found and other posts</h2>
<p>Anything you post must be accurate and yours to share. Don’t post anything illegal, hateful, or misleading. We review posts and may remove them. Never pay anyone to return a pet.</p>
<h2>7. No guarantees</h2>
<p>Howlback is provided as is. We don’t guarantee that any dog will be fully funded, adopted, or reunited, or that the site will always be available. We’re not responsible for what fosters, supporters, or other users do. To the extent the law allows, Howlback’s total liability for any claim is limited to the fees you paid Howlback in the 12 months before the claim.</p>
<h2>8. Changes</h2>
<p>We may update these terms. If we make big changes, we’ll post them here with a new date.</p>
<h2>9. Law</h2>
<p>These terms are governed by the laws of the State of Texas.</p>
<h2>10. Contact</h2>
<p>Email <a href="mailto:hello@howlback.app">hello@howlback.app</a>.</p>""")

policy("/refunds/", "Refund policy", "Howlback refund policy for chip-ins to foster dogs.", """
<h2>Before the foster is paid out</h2>
<p>If you made a mistake, email <a href="mailto:hello@howlback.app">hello@howlback.app</a> within <b>7 days</b> of your payment with the email you used at checkout. If the money hasn’t been paid out to the foster yet, we’ll refund the full amount, including the Howlback fee.</p>
<h2>After the foster is paid out</h2>
<p>Once a foster has been paid back, chip-ins are usually final.</p>
<h2>Fake or altered receipts</h2>
<p>If we find that a receipt was fake, altered, or already paid back somewhere else, we’ll refund supporters for that receipt, including the fee, as far as we’re able to recover the money.</p>
<h2>Charges you don’t recognize</h2>
<p>Email us first at <a href="mailto:hello@howlback.app">hello@howlback.app</a>. We’ll look into it right away.</p>
<p>Refunds go back to the original card and usually show up within 5 to 10 business days.</p>""")

policy("/privacy/", "Privacy policy", "How Howlback collects and uses information.", """
<h2>What we collect</h2>
<ul><li><b>Fosters:</b> name, email, city, optional phone, dog profiles, and receipt images. Stripe collects your bank and ID details directly. Howlback never sees your bank info.</li>
<li><b>Supporters:</b> the name and note you choose to show (optional), and payment details processed by Stripe. Howlback never sees or stores your card number.</li>
<li><b>Lost &amp; found posters:</b> what you enter in the form, including photos and contact info.</li>
<li><b>Email or text sign-ups:</b> your email or phone number, only to send Howlback updates.</li>
<li><b>Site visits:</b> simple visit counts through GoatCounter, which doesn’t use cookies or track you across sites.</li></ul>
<h2>What’s public</h2>
<ul><li>Dog profiles, the foster’s first name, receipt details (business, date, amount, what it was for), and supporter names and notes if you choose to show them.</li>
<li>Receipt images are private. Only the foster and Howlback can see them.</li>
<li>Lost &amp; found posts show your phone number only if you choose to show it. Your email is never shown.</li></ul>
<h2>How we use it</h2>
<p>To run Howlback: review listings, verify receipts, process payments and payouts, prevent fraud, and contact you about your account. We don’t sell your information.</p>
<h2>Who we share it with</h2>
<ul><li><b>Stripe</b>, to process payments and payouts</li><li><b>Supabase</b>, which stores our data</li><li>Law enforcement, only if required by law</li></ul>
<h2>Your choices</h2>
<p>Email <a href="mailto:hello@howlback.app">hello@howlback.app</a> to see, change, or delete your information. Some payment records must be kept for tax and legal reasons.</p>
<h2>Kids</h2>
<p>Howlback isn’t meant for anyone under 18 to sign up or pay.</p>""")
