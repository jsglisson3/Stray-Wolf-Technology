"""Builds the Stray Wolf website into docs/.

Sources live in src/ (not published):
  src/layout.html                the shell every page shares: head, header, footer ({{...}} slots are filled below)
  src/home.html                  the homepage
  src/pages.py                   the inner pages (Work, About, Start a project, thanks, privacy, 404)
  src/sites.py                   the list of websites shown on the Work page and in the homepage carousel
  src/partials/intake-form.html  the six questions (the Start a project page)
  src/partials/sprite.html       the icons

Run from the project folder:  python3 tools/build.py
"""
import pathlib, re, subprocess, sys, importlib.util, datetime, html as htmlesc

# ---- Launch settings ------------------------------------------------------------
DOMAIN = 'straywolftech.com'  # the site's address. docs/CNAME must say the same thing
LAUNCHED = True               # True on launch day: removes the draft banner and the noindex tag from public pages
HIDDEN = {'404.html', 'thanks.html', 'contact.html', 'brand.html'}   # never listed for search engines
PUBLIC = ['index.html', 'work.html', 'pricing.html', 'reviews.html', 'about.html', 'start.html', 'privacy.html', 'terms.html']   # listed in sitemap.xml
VERSION = '39'                 # bump when docs/css/site.css or docs/js/site.js change, so visitors get the new files

# ---- Contact details: fill these in when they exist, then rebuild ------------------
# Anything left empty is simply left off the site (no placeholder text is ever shown).
EMAIL = 'info@straywolftech.com'                    # the public address (Google Workspace alias of jeremy@); shows in the footer, on Start and in the legal pages
PHONE = ''                    # e.g. '(469) 555-0123'            (same places; tap to call on phones)
BOOKING_URL = ''              # e.g. a Cal.com or Calendly link for "Book a 15-minute call"
HEADSHOT = False              # True once docs/images/jeremy.webp is a real photo (4:3 or square, 1200px wide or more); used on the About page
WEB3FORMS_KEY = '0cf93fa5-b765-42a7-9364-2d5a1517d084'            # the access key from web3forms.com; until then the form opens a pre-filled email
FALLBACK_EMAIL = 'info@straywolftech.com'   # where the pre-filled email goes if the form service is ever unreachable

# ---- Prices (Nov 9 2026: Jeremy took the first draft down about 15%, rounded; change the numbers here and rebuild) ----------
STARTER_FROM = '1,500'        # a starter site, up to five pages ("from $...")
LARGER_FROM = '3,000'         # a larger site: more pages, booking, a menu, a gallery, a small shop
FIX_FROM = '125'              # smaller jobs on a site that already exists: a fix ...
PAGE_FROM = '350'             # ... one new page ...
REFRESH_FROM = '750'          # ... new photos and words across the pages you have
MOCKUP_FROM = '50'            # a mockup of the homepage before anyone commits, $50 to $100 depending on what's in it; ...
MOCKUP_TO = '100'             # ... and it comes off the price if the full site goes ahead
# No monthly fees, ever (Jeremy, Nov 9 2026): the care plan is gone; care.html now sends people to pricing.html.
# -----------------------------------------------------------------------------------

# ---- Reviews: real words only, with the client's OK to quote them by name. Empty = the page says "coming soon". ----
REVIEWS = [
    # ('The words the client wrote, as written.', 'First Last', 'Business name', 'https://their-site.com'),   # url can be ''
]

# ---- Google Analytics 4 (Jeremy, Nov 10 2026: on, no cookie banner; the privacy page says so). Empty = no analytics at all,
# and then also put the "no cookies, no tracking" lines back in src/layout.html, src/pages.py (Start and Privacy). ----
GA4_ID = 'G-K661V9VYG2'       # the Measurement ID from GA4 > Admin > Data streams (not the GTM-... container ID, which isn't used)

# ---- Google Search Console: paste the content value from the "HTML tag" method here, then rebuild ----
SEARCH_CONSOLE = ''           # e.g. 'AbCdEf123...' from <meta name="google-site-verification" content="...">  (not needed if verified by DNS in Cloudflare)
BING_VERIFY = ''              # optional: the content value of Bing Webmaster Tools' <meta name="msvalidate.01" ...> tag (or just import from Search Console)
# ---- Profiles that are really yours (Google Business Profile share link, LinkedIn, Facebook...). Tells Google they're the same business. ----
SAME_AS = [
    'https://g.page/r/CfdnwlRHO5SNEBM',   # the Business Profile's own address (the review link without /review)
    # 'https://www.linkedin.com/company/...',   (GOOGLE_PROFILE_URL below is added on its own, no need to repeat it here)
]

# ---- Google Business Profile (Nov 11 2026: created as a service business, links filled in). Empty = nothing Google-related shows.
#   GOOGLE_PROFILE_URL: the profile's public link. Business Profile > Share > copy the link (https://maps.app.goo.gl/... or https://g.page/...)
#   GOOGLE_REVIEW_URL:  the "ask for reviews" link. Business Profile > Ask for reviews > copy (https://g.page/r/.../review)
# With them set: the Reviews page gets the "Review us on Google" button, the footer and Thanks page get "See us on Google",
# the structured data names the profile (sameAs), and straywolftech.com/review/ forwards to the review form (a short link
# for emails, invoices and a QR code). Until then /review/ forwards to the Reviews page, so a printed link never breaks.
GOOGLE_PROFILE_URL = 'https://share.google/uQjBeT1gwU9UAhhyP'   # the Share link from the profile (Nov 11 2026)
GOOGLE_REVIEW_URL = 'https://g.page/r/CfdnwlRHO5SNEBM/review'   # from Ask for reviews (Nov 11 2026)
SERVICE_AREAS = [('Dallas', 'TX'), ('The Colony', 'TX'), ('Chattanooga', 'TN')]   # the same areas as the Business Profile

TAGLINE = 'Bespoke websites, by referral, for owner-run businesses. Bold, different and built around yours.'
HOME_DESC = 'Bespoke websites for owner-run businesses, by referral. Design, domain, hosting and email, with one price in writing before anything starts.'   # the homepage's line in search results
YEAR = str(datetime.date.today().year)
ROBOTS_META = '  <meta name="robots" content="noindex, nofollow">\n'
BANNER = '  <aside class="draft-banner" aria-label="Draft notice">Draft preview. Not yet public.</aside>\n'
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
DOCS = ROOT / 'docs'
P = SRC / 'partials'


def esc(s):
    return htmlesc.escape(s, quote=True)


def read(name):
    return (P / name).read_text(encoding='utf-8')


def viewbox(svg_text):
    x, y, w, h = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg_text).groups()
    return str(round(float(w))), str(round(float(h)))


# ---- Contact pieces, built from the settings above --------------------------------
tel = re.sub(r'[^\d+]', '', PHONE)
if tel and not tel.startswith('+'):
    tel = '+1' + tel[-10:]
EMAIL_LINK = f'<a href="mailto:{esc(EMAIL)}">{esc(EMAIL)}</a>' if EMAIL else ''
PHONE_LINK = f'<a href="tel:{tel}">{esc(PHONE)}</a>' if PHONE else ''
BOOKING_LINK = f'<a href="{esc(BOOKING_URL)}" target="_blank" rel="noopener">Book a 15-minute call<span class="visually-hidden"> (opens in a new tab)</span></a>' if BOOKING_URL else ''
WAYS = [x for x in (EMAIL_LINK, PHONE_LINK, BOOKING_LINK) if x]


def reach_block():
    """The footer's contact lines. Until an email or phone exists, the form is the way in."""
    if WAYS:
        g = google_profile_link('')
        return '<ul class="reach" role="list">' + ''.join(f'<li>{x}</li>' for x in WAYS + ([g] if g else [])) + '</ul>'
    return '<p class="muted">The quickest way is the <a href="start.html">Start a project</a> page. You\'ll hear back within five days.</p>'


def google_profile_link(cls='g-profile'):
    """'See us on Google': a plain text link to the Business Profile (no Google logo: their brand rules don't allow it here). '' while unset."""
    if not GOOGLE_PROFILE_URL:
        return ''
    cls_attr = f' class="{cls}"' if cls else ''
    return (f'<a{cls_attr} href="{esc(GOOGLE_PROFILE_URL)}" rel="noopener" target="_blank">'
            f'<svg class="icon" aria-hidden="true"><use href="#i-star"/></svg><span>See us on Google</span>'
            f'<span class="visually-hidden"> (opens in a new tab)</span></a>')


def google_review_badge(lead='Worked with Stray Wolf?'):
    """The "Review us on Google" button: five outline stars (an invitation, not a rating) and plain text. '' while unset."""
    if not GOOGLE_REVIEW_URL:
        return ''
    stars = ''.join('<svg class="icon" aria-hidden="true"><use href="#i-star"/></svg>' for _ in range(5))
    return (f'<a class="g-review" href="{esc(GOOGLE_REVIEW_URL)}" rel="noopener" target="_blank">'
            f'<span class="g-review-stars" aria-hidden="true">{stars}</span>'
            f'<span class="g-review-t"><small>{lead}</small><strong>Review us on Google</strong></span>'
            f'<svg class="icon g-review-go" aria-hidden="true"><use href="#i-arrow-out"/></svg>'
            f'<span class="visually-hidden"> (opens Google in a new tab)</span></a>')


def photo_or_mark(dark=True):
    """Jeremy's photo once HEADSHOT is True; the logo until then. Never a grey box."""
    if HEADSHOT:
        return '<img src="images/jeremy.webp" width="1200" height="900" loading="lazy" decoding="async" alt="Jeremy, who runs Stray Wolf Technology.">'
    name = 'stray-wolf-logo-stacked-reverse.svg' if dark else 'stray-wolf-logo-stacked-color.svg'
    return f'<img src="images/brand/{name}" width="200" height="190" loading="lazy" decoding="async" alt="">'


# ---- Small helpers for the components below -----------------------------------------
def icon(name, cls='icon'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


ARROW = icon('arrow')


def words(s, start=0):
    """Each word in its own span, so the headline can rise a word at a time (motion.css)."""
    return ' '.join(f'<span class="w" style="--i:{start + i}">{w}</span>' for i, w in enumerate(s.split()))


# ---- Hero: the headline on the left; the lead, the buttons and a small "Recently built" thumbnail on the right ----
H1_A = 'A website built around'
H1_B = 'your needs.'
H1 = f'{H1_A} {H1_B}'
LEAD = 'Websites that don’t look like everyone else’s.'
PROMISES = [('craft', 'Made for you', 'No templates or page builders'),
            ('key', 'Yours to keep', 'Your domain, your site'),
            ('calendar', 'About 30 days', 'From answers to launch')]


def hero():
    """The words. V34 (Nov 10 2026, Jeremy): the wolf stops at a small pool, lowers its head and drinks, then howls (every 16 seconds,
    the howl still in step with the header moon); the cactuses have ribs, spines and blooms; soft clouds drift and two small flocks
    of birds cross the sky (the .hero-sky layer, between the desert and the words).
    V24 (Nov 10 2026): the wolf on the ridge lifts its head and howls every 16 seconds, in step with the moon
    at the top right of the header (the cross-fade between the level and the howling silhouette, as in the footer).
    V22 (Nov 10 2026, final polish): the sun is a soft filled disc with a glow, half behind the far hills, and on load
    the wolf runs in from the left and stops on the ridge, once (it stands still for anyone with reduced motion).
    V21 (Nov 10 2026, Jeremy: the right-hand column "looks bolted on"): the headline runs wide across the top,
    then one ruled row under it, the sentence on the left and the two buttons on the right. The "Recently built" thumbnail is gone;
    Work is in the menu.
    V19 (Nov 9 2026, Jeremy picked "Horizon" of three): a paper-cut desert runs along the bottom edge, daytime tones, the wolf standing
    on the near ridge (the wolf and cactus shapes are the footer's, reused with <use>), cacti in cactus green, a thin orange sun."""
    return f'''    <section class="hero has-facets" aria-labelledby="hero-h">
      <div class="wrap hero-grid">
        <h1 id="hero-h" class="hero-h1">{words(H1_A)} <em>{words(H1_B, len(H1_A.split()))}</em></h1>
        <div class="hero-text">
          <p class="hero-lead">{LEAD}</p>
          <div class="button-row">
            <a class="button button-lg" href="start.html">Start a project{ARROW}</a>
            <a class="button button-quiet button-lg" href="#how">How it works</a>
          </div>
        </div>
      </div>
      <!-- V34 (Jeremy: "some birds flying around", "some clouds as well", "subtle but cool"): soft clouds drift and two small flocks cross the sky. Decoration only. -->
      <div class="hero-sky" aria-hidden="true">
        <svg class="sky-cloud sky-cloud-1" viewBox="0 0 120 44" focusable="false"><g class="sky-cl-back" transform="translate(0 3.2)"><rect x="6" y="23" width="108" height="15" rx="7.5"/><circle cx="33" cy="23" r="13"/><circle cx="59" cy="17" r="17"/><circle cx="85" cy="24" r="11.5"/></g><g class="sky-cl"><rect x="6" y="23" width="108" height="15" rx="7.5"/><circle cx="33" cy="23" r="13"/><circle cx="59" cy="17" r="17"/><circle cx="85" cy="24" r="11.5"/></g></svg><svg class="sky-cloud sky-cloud-2" viewBox="0 0 120 44" focusable="false"><g class="sky-cl-back" transform="translate(0 3.2)"><rect x="6" y="23" width="108" height="15" rx="7.5"/><circle cx="33" cy="23" r="13"/><circle cx="59" cy="17" r="17"/><circle cx="85" cy="24" r="11.5"/></g><g class="sky-cl"><rect x="6" y="23" width="108" height="15" rx="7.5"/><circle cx="33" cy="23" r="13"/><circle cx="59" cy="17" r="17"/><circle cx="85" cy="24" r="11.5"/></g></svg><svg class="sky-cloud sky-cloud-3" viewBox="0 0 120 44" focusable="false"><g class="sky-cl-back" transform="translate(0 3.2)"><rect x="6" y="23" width="108" height="15" rx="7.5"/><circle cx="33" cy="23" r="13"/><circle cx="59" cy="17" r="17"/><circle cx="85" cy="24" r="11.5"/></g><g class="sky-cl"><rect x="6" y="23" width="108" height="15" rx="7.5"/><circle cx="33" cy="23" r="13"/><circle cx="59" cy="17" r="17"/><circle cx="85" cy="24" r="11.5"/></g></svg>
        <div class="sky-flock sky-flock-1"><svg class="sky-bird sky-bird-1" viewBox="0 0 24 12" focusable="false"><path d="M1.5 7 Q6.5 0.5 12 6.5 Q17.5 0.5 22.5 7"/></svg><svg class="sky-bird sky-bird-2" viewBox="0 0 24 12" focusable="false"><path d="M1.5 7 Q6.5 0.5 12 6.5 Q17.5 0.5 22.5 7"/></svg><svg class="sky-bird sky-bird-3" viewBox="0 0 24 12" focusable="false"><path d="M1.5 7 Q6.5 0.5 12 6.5 Q17.5 0.5 22.5 7"/></svg><svg class="sky-bird sky-bird-4" viewBox="0 0 24 12" focusable="false"><path d="M1.5 7 Q6.5 0.5 12 6.5 Q17.5 0.5 22.5 7"/></svg></div><div class="sky-flock sky-flock-2"><svg class="sky-bird sky-bird-1" viewBox="0 0 24 12" focusable="false"><path d="M1.5 7 Q6.5 0.5 12 6.5 Q17.5 0.5 22.5 7"/></svg><svg class="sky-bird sky-bird-2" viewBox="0 0 24 12" focusable="false"><path d="M1.5 7 Q6.5 0.5 12 6.5 Q17.5 0.5 22.5 7"/></svg></div>
        <!-- V36: a hawk circles high over the desert (its shadow crosses the sand in the scene below) -->
        <div class="sky-hawk"><div class="sky-hawk-orbit"><svg class="sky-hawk-bird" viewBox="-17 -22 34 44" focusable="false"><path d="M12.0 0.0 L11.2 1.2 L9.0 1.8 L6.0 2.4 L5.8 6.0 L5.2 10.0 L4.4 14.0 L3.6 16.5 L2.8 20.2 L1.6 17.6 L1.0 20.4 L0.0 17.6 L-0.9 20.0 L-1.6 17.2 L-2.8 19.2 L-3.2 16.4 L-4.4 17.6 L-5.0 15.0 L-6.4 11.0 L-7.0 7.0 L-6.6 4.0 L-6.2 2.4 L-7.6 2.6 L-12.5 5.2 L-14.2 3.6 L-14.8 0.0 L-14.2 -3.6 L-12.5 -5.2 L-7.6 -2.6 L-6.2 -2.4 L-6.6 -4.0 L-7.0 -7.0 L-6.4 -11.0 L-5.0 -15.0 L-4.4 -17.6 L-3.2 -16.4 L-2.8 -19.2 L-1.6 -17.2 L-0.9 -20.0 L0.0 -17.6 L1.0 -20.4 L1.6 -17.6 L2.8 -20.2 L3.6 -16.5 L4.4 -14.0 L5.2 -10.0 L5.8 -6.0 L6.0 -2.4 L9.0 -1.8 L11.2 -1.2 Z"/></svg></div></div>
      </div>
      <svg class="hero-scene" viewBox="0 0 1200 150" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
        <defs><radialGradient id="hs-glow"><stop offset=".4" stop-color="#E0763A" stop-opacity=".22"/><stop offset=".6" stop-color="#E0763A" stop-opacity=".08"/><stop offset="1" stop-color="#E0763A" stop-opacity="0"/></radialGradient>
          <clipPath id="hs-pool-clip"><ellipse cx="536" cy="134.4" rx="74" ry="4.9"/></clipPath>
          <!-- V34: the head going down to drink, three steps from #wolf-level (generated; see PICKUP.md V34) -->
          <g id="hs-dip-1"><path d="M-10.0 -104.0 C-16.7 -101.2 -30.7 -101.8 -40.0 -101.0 C-49.3 -100.2 -58.7 -100.3 -66.0 -99.0 C-73.3 -97.7 -78.7 -95.5 -84.0 -93.0 C-89.3 -90.5 -93.7 -89.2 -98.0 -84.0 C-102.3 -78.8 -107.7 -69.3 -110.0 -62.0 C-112.3 -54.7 -112.7 -46.7 -112.0 -40.0 C-111.3 -33.3 -106.0 -22.0 -106.0 -22.0 C-106.0 -22.0 -100.3 -32.0 -98.0 -38.0 C-95.7 -44.0 -94.0 -52.3 -92.0 -58.0 C-90.0 -63.7 -86.0 -72.0 -86.0 -72.0 C-86.0 -72.0 -90.3 -63.7 -92.0 -58.0 C-93.7 -52.3 -96.3 -44.7 -96.0 -38.0 C-95.7 -31.3 -91.3 -24.0 -90.0 -18.0 C-88.7 -12.0 -88.0 -2.0 -88.0 -2.0 C-88.0 -2.0 -72.0 0.0 -72.0 0.0 C-72.0 0.0 -74.3 -10.3 -76.0 -16.0 C-77.7 -21.7 -83.3 -29.0 -82.0 -34.0 C-80.7 -39.0 -72.0 -42.7 -68.0 -46.0 C-64.0 -49.3 -62.0 -51.7 -58.0 -54.0 C-54.0 -56.3 -51.7 -58.7 -44.0 -60.0 C-36.3 -61.3 -22.0 -62.3 -12.0 -62.0 C-2.0 -61.7 11.3 -61.7 16.0 -58.0 C20.7 -54.3 16.0 -46.7 16.0 -40.0 C16.0 -33.3 16.0 -24.3 16.0 -18.0 C16.0 -11.7 16.0 -2.0 16.0 -2.0 C16.0 -2.0 30.0 0.0 30.0 0.0 C30.0 0.0 29.5 -12.7 30.0 -20.0 C30.5 -27.3 32.0 -36.7 33.0 -44.0 C34.0 -51.3 34.2 -57.7 36.0 -64.0 C37.8 -70.3 42.0 -76.0 44.0 -82.0 C53.7 -87.1 64.3 -87.8 75.4 -92.5 C79.5 -92.5 84.1 -90.1 89.0 -89.2 C93.9 -88.3 100.1 -87.2 105.0 -87.4 C109.9 -87.5 118.1 -90.4 118.1 -90.4 C118.1 -90.4 111.1 -99.6 106.8 -103.4 C102.6 -107.2 96.9 -110.2 92.7 -113.0 C88.5 -115.7 84.6 -118.0 82.0 -119.7 C79.3 -121.4 77.0 -119.1 76.6 -123.0 C76.2 -126.9 79.4 -142.9 79.4 -142.9 C79.4 -142.9 69.1 -129.0 64.9 -125.9 C60.8 -122.7 58.7 -125.6 54.3 -124.3 C42.7 -121.5 20.8 -114.6 -10.0 -104.0 Z"/><g transform="translate(86.3 -107.8)"><g class="wolf-eye"><circle r="3.2"/><circle class="wolf-glint" cx="1.1" cy="-1.1" r="1.05"/></g></g></g>
          <g id="hs-dip-2"><path d="M-10.0 -104.0 C-16.7 -101.2 -30.7 -101.8 -40.0 -101.0 C-49.3 -100.2 -58.7 -100.3 -66.0 -99.0 C-73.3 -97.7 -78.7 -95.5 -84.0 -93.0 C-89.3 -90.5 -93.7 -89.2 -98.0 -84.0 C-102.3 -78.8 -107.7 -69.3 -110.0 -62.0 C-112.3 -54.7 -112.7 -46.7 -112.0 -40.0 C-111.3 -33.3 -106.0 -22.0 -106.0 -22.0 C-106.0 -22.0 -100.3 -32.0 -98.0 -38.0 C-95.7 -44.0 -94.0 -52.3 -92.0 -58.0 C-90.0 -63.7 -86.0 -72.0 -86.0 -72.0 C-86.0 -72.0 -90.3 -63.7 -92.0 -58.0 C-93.7 -52.3 -96.3 -44.7 -96.0 -38.0 C-95.7 -31.3 -91.3 -24.0 -90.0 -18.0 C-88.7 -12.0 -88.0 -2.0 -88.0 -2.0 C-88.0 -2.0 -72.0 0.0 -72.0 0.0 C-72.0 0.0 -74.3 -10.3 -76.0 -16.0 C-77.7 -21.7 -83.3 -29.0 -82.0 -34.0 C-80.7 -39.0 -72.0 -42.7 -68.0 -46.0 C-64.0 -49.3 -62.0 -51.7 -58.0 -54.0 C-54.0 -56.3 -51.7 -58.7 -44.0 -60.0 C-36.3 -61.3 -22.0 -62.3 -12.0 -62.0 C-2.0 -61.7 11.3 -61.7 16.0 -58.0 C20.7 -54.3 16.0 -46.7 16.0 -40.0 C16.0 -33.3 16.0 -24.3 16.0 -18.0 C16.0 -11.7 16.0 -2.0 16.0 -2.0 C16.0 -2.0 30.0 0.0 30.0 0.0 C30.0 0.0 29.5 -12.7 30.0 -20.0 C30.5 -27.3 32.0 -36.7 33.0 -44.0 C34.0 -51.3 34.2 -57.7 36.0 -64.0 C37.8 -70.3 42.0 -76.0 44.0 -82.0 C53.4 -74.4 66.4 -64.5 79.9 -60.3 C83.9 -59.4 87.8 -55.9 92.3 -53.9 C96.9 -51.9 102.7 -49.4 107.5 -48.4 C112.3 -47.4 120.9 -48.2 120.9 -48.2 C120.9 -48.2 116.2 -58.8 113.0 -63.5 C109.8 -68.2 104.9 -72.5 101.5 -76.2 C98.1 -79.8 94.9 -83.0 92.7 -85.2 C90.5 -87.5 87.7 -85.9 88.3 -89.7 C88.8 -93.6 95.6 -108.4 95.6 -108.4 C95.6 -108.4 82.4 -97.3 77.6 -95.2 C72.8 -93.2 71.5 -96.5 66.9 -96.2 C58.6 -112.7 29.7 -113.3 -10.0 -104.0 Z"/><g transform="translate(94.1 -72.7)"><g class="wolf-eye"><circle r="3.2"/><circle class="wolf-glint" cx="1.1" cy="-1.1" r="1.05"/></g></g></g>
          <g id="hs-dip-3"><path d="M-10.0 -104.0 C-16.7 -101.2 -30.7 -101.8 -40.0 -101.0 C-49.3 -100.2 -58.7 -100.3 -66.0 -99.0 C-73.3 -97.7 -78.7 -95.5 -84.0 -93.0 C-89.3 -90.5 -93.7 -89.2 -98.0 -84.0 C-102.3 -78.8 -107.7 -69.3 -110.0 -62.0 C-112.3 -54.7 -112.7 -46.7 -112.0 -40.0 C-111.3 -33.3 -106.0 -22.0 -106.0 -22.0 C-106.0 -22.0 -100.3 -32.0 -98.0 -38.0 C-95.7 -44.0 -94.0 -52.3 -92.0 -58.0 C-90.0 -63.7 -86.0 -72.0 -86.0 -72.0 C-86.0 -72.0 -90.3 -63.7 -92.0 -58.0 C-93.7 -52.3 -96.3 -44.7 -96.0 -38.0 C-95.7 -31.3 -91.3 -24.0 -90.0 -18.0 C-88.7 -12.0 -88.0 -2.0 -88.0 -2.0 C-88.0 -2.0 -72.0 0.0 -72.0 0.0 C-72.0 0.0 -74.3 -10.3 -76.0 -16.0 C-77.7 -21.7 -83.3 -29.0 -82.0 -34.0 C-80.7 -39.0 -72.0 -42.7 -68.0 -46.0 C-64.0 -49.3 -62.0 -51.7 -58.0 -54.0 C-54.0 -56.3 -51.7 -58.7 -44.0 -60.0 C-36.3 -61.3 -22.0 -62.3 -12.0 -62.0 C-2.0 -61.7 11.3 -61.7 16.0 -58.0 C20.7 -54.3 16.0 -46.7 16.0 -40.0 C16.0 -33.3 16.0 -24.3 16.0 -18.0 C16.0 -11.7 16.0 -2.0 16.0 -2.0 C16.0 -2.0 30.0 0.0 30.0 0.0 C30.0 0.0 29.5 -12.7 30.0 -20.0 C30.5 -27.3 32.0 -36.7 33.0 -44.0 C34.0 -51.3 34.2 -57.7 36.0 -64.0 C44.0 -48.0 57.8 -32.8 72.5 -24.0 C76.2 -22.2 79.2 -18.0 83.3 -15.0 C87.3 -12.0 92.4 -8.3 96.8 -6.2 C101.2 -4.2 109.8 -3.1 109.8 -3.1 C109.8 -3.1 107.6 -14.5 105.6 -19.8 C103.5 -25.1 99.7 -30.3 97.2 -34.7 C94.6 -39.0 92.2 -42.7 90.5 -45.4 C88.9 -48.1 85.8 -47.2 87.2 -50.8 C88.6 -54.5 98.5 -67.4 98.5 -67.4 C98.5 -67.4 83.1 -59.5 78.0 -58.5 C72.9 -57.6 72.3 -61.1 67.8 -61.9 C70.8 -89.9 38.0 -112.0 -10.0 -104.0 Z"/><g transform="translate(89.1 -32.9)"><g class="wolf-eye"><circle r="3.2"/><circle class="wolf-glint" cx="1.1" cy="-1.1" r="1.05"/></g></g></g>
          <!-- V34: ribs, spines and blooms, drawn over #cactus -->
          <g id="hs-cactus-detail"><path class="hs-rib" d="M-2.5 -4 V-123 M2.5 -4 V-123 M-37 -60 V-99 M-28 -53 H-10 M34 -76 V-105 M10 -71 H24"/><path class="hs-spine" d="M-7 -12 l-4.5 -2.6 M-7 -22 l-4.5 -2.6 M-7 -32 l-4.5 -2.6 M-7 -42 l-4.5 -2.6 M-7 -52 l-4.5 -2.6 M-7 -62 l-4.5 -2.6 M-7 -72 l-4.5 -2.6 M-7 -82 l-4.5 -2.6 M-7 -92 l-4.5 -2.6 M-7 -102 l-4.5 -2.6 M-7 -112 l-4.5 -2.6 M7 -17 l4.5 -2.6 M7 -27 l4.5 -2.6 M7 -37 l4.5 -2.6 M7 -47 l4.5 -2.6 M7 -57 l4.5 -2.6 M7 -67 l4.5 -2.6 M7 -77 l4.5 -2.6 M7 -87 l4.5 -2.6 M7 -97 l4.5 -2.6 M7 -107 l4.5 -2.6 M7 -117 l4.5 -2.6 M-44 -64 l-4.5 -2.6 M-44 -74 l-4.5 -2.6 M-44 -84 l-4.5 -2.6 M-44 -94 l-4.5 -2.6 M-30 -70 l4 -2.6 M-30 -81 l4 -2.6 M-30 -92 l4 -2.6 M-36 -46 l-1.5 4.5 M-22 -46 l0 4.5 M-41 -101 l-3.6 -3.4 M40 -82 l4.5 -2.6 M40 -91 l4.5 -2.6 M40 -100 l4.5 -2.6 M28 -86 l-4 -2.6 M28 -95 l-4 -2.6 M30 -64 l1.5 4.5 M16 -64 l0 4.5 M38 -107 l3.6 -3.4"/><circle class="hs-bloom" cx="-4.2" cy="-130.5" r="3.1"/><circle class="hs-bloom" cx="4.4" cy="-131" r="2.8"/><circle class="hs-bud" cx="0.2" cy="-134.2" r="3"/><circle class="hs-fruit" cx="-6.5" cy="-122" r="1.7"/><circle class="hs-bloom" cx="-40" cy="-104.5" r="2.6"/><circle class="hs-bud" cx="-35" cy="-106.4" r="2.5"/><circle class="hs-bud" cx="31.6" cy="-111.6" r="2.5"/><circle class="hs-bloom" cx="36.8" cy="-110.6" r="2.6"/><circle class="hs-fruit" cx="39.5" cy="-99" r="1.6"/></g>
          <!-- V36: the jackrabbit, sitting up (facing the wolf) and two bounding poses -->
          <g id="hs-hare-sit"><path d="M-27.0 0.0 C-27.8 -2.0 -24.9 -8.0 -24.5 -12.0 C-24.1 -16.0 -24.1 -20.5 -24.5 -24.0 C-24.9 -27.5 -26.0 -30.3 -27.0 -33.0 C-28.0 -35.7 -29.2 -38.1 -30.5 -40.0 C-31.8 -41.9 -33.3 -43.5 -35.0 -44.6 C-36.7 -45.7 -39.1 -45.6 -40.5 -46.6 C-41.9 -47.6 -43.1 -49.0 -43.2 -50.4 C-43.3 -51.8 -42.5 -53.5 -41.0 -55.0 C-39.5 -56.5 -36.4 -57.8 -34.5 -59.6 C-32.6 -61.4 -30.6 -62.3 -29.5 -66.0 C-28.4 -69.7 -28.8 -76.8 -28.0 -82.0 C-27.2 -87.2 -25.9 -93.8 -24.8 -97.0 C-23.7 -100.2 -22.3 -101.7 -21.4 -101.0 C-20.5 -100.3 -19.7 -97.2 -19.4 -93.0 C-19.1 -88.8 -19.6 -80.8 -19.8 -76.0 C-20.0 -71.2 -20.9 -65.5 -20.5 -64.0 C-20.1 -62.5 -18.6 -64.3 -17.5 -67.0 C-16.4 -69.7 -15.3 -75.3 -14.0 -80.0 C-12.7 -84.7 -10.7 -91.8 -9.5 -95.0 C-8.3 -98.2 -7.3 -99.8 -6.6 -99.5 C-5.9 -99.2 -5.0 -96.9 -5.4 -93.0 C-5.8 -89.1 -7.9 -81.3 -9.0 -76.0 C-10.1 -70.7 -12.3 -64.8 -12.0 -61.0 C-11.7 -57.2 -9.7 -55.4 -7.0 -53.0 C-4.3 -50.6 0.2 -48.5 4.0 -46.5 C7.8 -44.5 12.2 -42.9 16.0 -41.0 C19.8 -39.1 23.8 -37.5 27.0 -35.0 C30.2 -32.5 33.1 -29.3 35.0 -26.0 C36.9 -22.7 37.2 -17.2 38.5 -15.0 C39.8 -12.8 42.0 -13.8 42.5 -12.5 C43.0 -11.2 42.3 -8.8 41.5 -7.5 C40.7 -6.2 38.8 -6.2 37.5 -5.0 C36.2 -3.8 36.9 -1.4 34.0 -0.6 C31.1 0.2 25.0 -0.1 20.0 0.0 C15.0 0.1 7.5 0.8 4.0 0.0 C0.5 -0.8 1.0 -3.3 -1.0 -5.0 C-3.0 -6.7 -5.7 -9.5 -8.0 -10.0 C-10.3 -10.5 -13.2 -9.2 -15.0 -8.0 C-16.8 -6.8 -17.8 -4.3 -18.5 -3.0 C-19.2 -1.7 -18.1 -0.5 -19.5 0.0 C-20.9 0.5 -26.2 2.0 -27.0 0.0 Z"/><circle class="hs-hare-eye" cx="-33" cy="-53" r="1.8"/></g>
          <g id="hs-hare-a"><path d="M47.5 -31.0 C47.2 -32.5 44.2 -35.2 42.0 -36.5 C39.8 -37.8 37.0 -37.2 34.0 -38.5 C31.0 -39.8 28.7 -41.6 24.0 -44.0 C19.3 -46.4 10.3 -51.2 6.0 -53.0 C1.7 -54.8 -2.0 -55.4 -2.0 -54.5 C-2.0 -53.6 2.3 -49.9 6.0 -47.5 C9.7 -45.1 19.0 -41.5 20.0 -40.0 C21.0 -38.5 16.0 -38.8 12.0 -38.5 C8.0 -38.2 1.3 -38.5 -4.0 -38.0 C-9.3 -37.5 -15.5 -36.8 -20.0 -35.5 C-24.5 -34.2 -28.7 -30.8 -31.0 -30.5 C-33.3 -30.2 -32.9 -33.6 -34.0 -33.5 C-35.1 -33.4 -35.8 -31.5 -37.5 -30.0 C-39.2 -28.5 -41.4 -26.5 -44.0 -24.5 C-46.6 -22.5 -49.8 -19.9 -53.0 -18.0 C-56.2 -16.1 -61.4 -14.3 -63.0 -13.0 C-64.6 -11.7 -64.4 -10.0 -62.6 -10.0 C-60.8 -10.0 -55.1 -12.4 -52.0 -13.2 C-48.9 -14.0 -46.8 -14.1 -44.0 -14.8 C-41.2 -15.5 -39.0 -17.0 -35.0 -17.6 C-31.0 -18.2 -25.2 -18.3 -20.0 -18.6 C-14.8 -18.9 -9.0 -19.3 -4.0 -19.4 C1.0 -19.5 6.3 -19.6 10.0 -19.0 C13.7 -18.4 14.7 -17.9 18.0 -16.0 C21.3 -14.1 26.0 -9.6 30.0 -7.4 C34.0 -5.2 39.7 -3.3 42.0 -2.6 C44.3 -1.9 45.1 -2.2 43.6 -3.4 C42.1 -4.6 35.9 -7.6 33.0 -9.6 C30.1 -11.6 26.3 -13.5 26.0 -15.4 C25.7 -17.3 29.0 -19.5 31.0 -21.0 C33.0 -22.5 35.9 -23.4 38.0 -24.5 C40.1 -25.6 41.9 -26.4 43.5 -27.5 C45.1 -28.6 47.8 -29.5 47.5 -31.0 Z"/><circle class="hs-hare-eye" cx="35.5" cy="-33.5" r="1.6"/></g>
          <g id="hs-hare-b"><path d="M41.0 -26.0 C40.7 -27.3 38.2 -30.2 36.0 -31.5 C33.8 -32.8 31.2 -32.6 28.0 -34.0 C24.8 -35.4 21.7 -37.7 17.0 -40.0 C12.3 -42.3 4.0 -46.5 0.0 -48.0 C-4.0 -49.5 -7.0 -49.9 -7.0 -49.0 C-7.0 -48.1 -3.5 -44.7 0.0 -42.5 C3.5 -40.3 13.3 -36.7 14.0 -36.0 C14.7 -35.3 7.7 -38.0 4.0 -38.5 C0.3 -39.0 -4.2 -39.6 -8.0 -39.0 C-11.8 -38.4 -16.0 -37.1 -19.0 -35.0 C-22.0 -32.9 -24.2 -27.8 -26.0 -26.5 C-27.8 -25.2 -29.2 -28.8 -29.5 -27.5 C-29.8 -26.2 -29.1 -22.1 -28.0 -19.0 C-26.9 -15.9 -25.0 -11.8 -23.0 -9.0 C-21.0 -6.2 -19.8 -3.8 -16.0 -2.4 C-12.2 -1.0 -4.7 -0.8 0.0 -0.4 C4.7 -0.0 9.9 0.1 12.0 -0.2 C14.1 -0.5 15.5 -1.5 12.8 -2.2 C10.1 -2.9 -1.1 -3.1 -4.0 -4.4 C-6.9 -5.7 -5.7 -8.3 -4.5 -10.0 C-3.3 -11.7 1.1 -14.0 3.0 -14.5 C4.9 -15.0 7.2 -14.4 7.0 -13.0 C6.8 -11.6 2.6 -7.7 1.5 -6.2 C0.4 -4.7 0.2 -4.6 0.5 -4.2 C0.8 -3.8 1.6 -2.8 3.5 -4.0 C5.4 -5.2 8.9 -9.2 12.0 -11.5 C15.1 -13.8 18.7 -16.4 22.0 -18.0 C25.3 -19.6 29.3 -20.1 32.0 -21.0 C34.7 -21.9 36.5 -22.7 38.0 -23.5 C39.5 -24.3 41.3 -24.7 41.0 -26.0 Z"/><circle class="hs-hare-eye" cx="30" cy="-29" r="1.6"/></g>
        </defs>
        <circle cx="980" cy="70" r="66" fill="url(#hs-glow)"/>
        <circle cx="980" cy="70" r="28" class="hs-sun"/>
        <path class="hs-far" d="M0 150 V92 L90 84 L180 90 L260 76 L330 80 L420 70 L520 84 L600 72 L700 80 L800 66 L900 78 L1000 70 L1100 82 L1200 74 V150Z"/>
        <!-- V36 ("Stray from the pack"): now and then a small pack lopes along the far ridge, the other way, while the wolf keeps to its oasis -->
        <g class="hs-pack"><g class="hs-packer hs-p1"><g transform="scale(-0.076 0.076)"><g class="run-body"><use href="#wolf-run"/><use class="gait-1" href="#wolf-legs-1"/><use class="gait-2" href="#wolf-legs-2"/><use class="gait-3" href="#wolf-legs-3"/><use class="gait-4" href="#wolf-legs-4"/></g></g></g><g class="hs-packer hs-p2"><g transform="scale(-0.072 0.072)"><g class="run-body"><use href="#wolf-run"/><use class="gait-1" href="#wolf-legs-1"/><use class="gait-2" href="#wolf-legs-2"/><use class="gait-3" href="#wolf-legs-3"/><use class="gait-4" href="#wolf-legs-4"/></g></g></g><g class="hs-packer hs-p3"><g transform="scale(-0.078 0.078)"><g class="run-body"><use href="#wolf-run"/><use class="gait-1" href="#wolf-legs-1"/><use class="gait-2" href="#wolf-legs-2"/><use class="gait-3" href="#wolf-legs-3"/><use class="gait-4" href="#wolf-legs-4"/></g></g></g><g class="hs-packer hs-p4"><g transform="scale(-0.066 0.066)"><g class="run-body"><use href="#wolf-run"/><use class="gait-1" href="#wolf-legs-1"/><use class="gait-2" href="#wolf-legs-2"/><use class="gait-3" href="#wolf-legs-3"/><use class="gait-4" href="#wolf-legs-4"/></g></g></g></g>
        <g transform="translate(250 112) scale(0.2)" class="hs-cactus-far"><use href="#cactus"/><use href="#hs-cactus-detail"/></g>
        <path class="hs-mid" d="M0 150 V116 L120 106 L240 118 L380 102 L500 114 L620 104 L760 118 L880 108 L1020 120 L1200 110 V150Z"/>
        <g transform="translate(760 130) scale(0.3)" class="hs-cactus"><use href="#cactus"/><use href="#hs-cactus-detail"/></g>
        <g transform="translate(900 128) scale(0.42)" class="hs-cactus"><use href="#cactus"/><use href="#hs-cactus-detail"/></g>
        <g transform="translate(1110 132) scale(0.26)" class="hs-cactus"><use href="#cactus"/><use href="#hs-cactus-detail"/></g>
        <g transform="translate(717 133.6) scale(0.26)"><g class="hs-hare-sit hs-hare"><use href="#hs-hare-sit"/></g></g>
        <!-- V34: the near ground is level from 392 to 622, where the wolf stands and the pool lies -->
        <path class="hs-near" d="M0 150 V134 L160 128 L320 136 L392 128.5 L622 128.5 L680 133 L800 128 L960 138 L1120 130 L1200 134 V150Z"/>
        <!-- V34 (Jeremy: "walk up on some water and drink a little bit then howl, like an oasis in the desert"): the pool, its reeds, and the rings the wolf makes -->
        <g class="hs-oasis">
          <ellipse cx="536" cy="134.9" rx="79" ry="6.2" class="hs-wet"/>
          <ellipse cx="536" cy="134.4" rx="74" ry="4.9" class="hs-water"/>
          <g clip-path="url(#hs-pool-clip)"><ellipse cx="554" cy="132.2" rx="46" ry="1.1" class="hs-shine"/><ellipse cx="522" cy="138.3" rx="58" ry="1.7" class="hs-deep"/>
            <ellipse cx="489" cy="133" rx="11" ry="2" class="hs-rip hs-rip-1"/><ellipse cx="489" cy="133" rx="11" ry="2" class="hs-rip hs-rip-2"/></g>
          <path class="hs-palm-trunk" d="M627.6 130 Q628.6 118 632.4 106 L634.6 106.6 Q631.4 118.4 630.8 130 Z"/>
          <path class="hs-palm" d="M633.6 106.4 Q643 97.5 654 103.4 Q643.5 101.6 633.6 106.4 Z M633.6 106.4 Q645 104 650.5 113.6 Q643 107.4 633.6 106.4 Z M633.6 106.4 Q637 95 647.4 93 Q639.6 98.4 633.6 106.4 Z M633.6 106.4 Q624.4 97.5 613.4 103.4 Q623.8 101.6 633.6 106.4 Z M633.6 106.4 Q622.4 104 616.8 113.6 Q624.4 107.4 633.6 106.4 Z M633.6 106.4 Q630.4 95 620 93 Q627.8 98.4 633.6 106.4 Z"/>
          <path class="hs-reed" d="M603.5 134.4 q-0.6 -7 -2.6 -12 M605.6 134.6 q0.2 -9 1 -15.5 M608 134.6 q1.2 -6 3.8 -10 M610.4 134.8 q2 -4 5.6 -6.4 M601.4 134.4 q-2.4 -4 -5.2 -6 M546 130.4 q-0.4 -3 -2 -5 M548 130.4 q0 -4 0.6 -6.4 M550 130.4 q1 -3 3 -4.6"/>
          <rect class="hs-cattail" x="605.7" y="115.6" width="1.7" height="4.6" rx="0.85"/><rect class="hs-cattail" x="600.1" y="119.2" width="1.6" height="4" rx="0.8" transform="rotate(-12 600.9 121.2)"/>
        </g>
        <!-- V36: the shrub the jackrabbit hides behind, the rabbit bolting, and the hawk's shadow -->
        <g class="hs-shrub"><path class="hs-shrub-twig" d="M708 132 l-3 -7 M711 132 l-1 -9 M716 132 l1.5 -10 M721 132 l3 -8 M725 132 l5 -5"/><path d="M701.5 133 C701 129.6 703 127.6 705.6 128 C705.8 125.2 708.6 123.6 711 124.8 C712.4 122.4 716 122 717.8 124.2 C720.2 122.8 723.6 123.8 724 126.6 C726.8 126.2 729.4 128 729 130.8 C730.8 131.2 731.4 132.4 731 133.4 Z"/><path class="hs-shrub-lit" d="M706 127.6 C707 125.6 709.4 125.2 711 126 C712.6 124 715.6 123.8 717.4 125.6 C719.6 124.4 722.2 125 723 127 C719 126 715 126.8 711.6 127.4 C709.6 127 707.6 127.2 706 127.6 Z"/></g>
        <g class="hs-hare-run hs-hare"><g transform="scale(0.26)"><g class="hs-hare-hop"><use class="hs-hare-a" href="#hs-hare-a"/><use class="hs-hare-b" href="#hs-hare-b"/></g></g></g>
        <g transform="translate(992 143.2) scale(1 0.13)" class="hs-hawk-shade"><g class="hs-hawk-orbit"><path transform="rotate(-90) scale(0.8)" d="M12.0 0.0 L11.2 1.2 L9.0 1.8 L6.0 2.4 L5.8 6.0 L5.2 10.0 L4.4 14.0 L3.6 16.5 L2.8 20.2 L1.6 17.6 L1.0 20.4 L0.0 17.6 L-0.9 20.0 L-1.6 17.2 L-2.8 19.2 L-3.2 16.4 L-4.4 17.6 L-5.0 15.0 L-6.4 11.0 L-7.0 7.0 L-6.6 4.0 L-6.2 2.4 L-7.6 2.6 L-12.5 5.2 L-14.2 3.6 L-14.8 0.0 L-14.2 -3.6 L-12.5 -5.2 L-7.6 -2.6 L-6.2 -2.4 L-6.6 -4.0 L-7.0 -7.0 L-6.4 -11.0 L-5.0 -15.0 L-4.4 -17.6 L-3.2 -16.4 L-2.8 -19.2 L-1.6 -17.2 L-0.9 -20.0 L0.0 -17.6 L1.0 -20.4 L1.6 -17.6 L2.8 -20.2 L3.6 -16.5 L4.4 -14.0 L5.2 -10.0 L5.8 -6.0 L6.0 -2.4 L9.0 -1.8 L11.2 -1.2 Z"/></g></g>
        <g transform="translate(440 132) scale(0.42)" class="hs-wolf">
          <g class="hs-stand"><use href="#wolf-far-hind" opacity=".85"/><use href="#wolf-far-front" opacity=".85"/><use class="hs-level" href="#wolf-level"/><use class="hs-d1" href="#hs-dip-1"/><use class="hs-d2" href="#hs-dip-2"/><use class="hs-d3" href="#hs-dip-3"/><use class="hs-howl" href="#wolf-howl"/></g>
          <g class="hs-run"><g class="run-body"><use href="#wolf-run"/><use class="gait-1" href="#wolf-legs-1"/><use class="gait-2" href="#wolf-legs-2"/><use class="gait-3" href="#wolf-legs-3"/><use class="gait-4" href="#wolf-legs-4"/></g></g>
        </g>
        <path d="M0 150 H1200" class="hs-line"/>
      </svg>
    </section>'''


# ---- How it works (V16, Nov 9 2026): three columns. The client's part, then Jeremy takes over, then one checkpoint.
# V29 (Nov 10 2026, Jeremy on how he really works): it starts with a conversation. From the client he needs the logo, as many photos
# as they can send and the few words that matter most (a main headline or slogan); he writes the rest. He helps find a domain
# name that is available, not just register it. Once he takes the job he sends a short list of what to send and how (PHASE_NOTE).
# V33 (Nov 10 2026, Jeremy: "the first step should only be about do they have a website? what's their situation and what are they
# wanting to do? what's the goal of this website?"): step one is only that conversation. The logo, photos and wording lines moved
# out of the You list into PHASE_NOTE ("this should go into the 'once i take the job' area").
PHASES = [
    ('First', 'You.', 'Tell me what you want.', [
        'Whether you have a website now',
        'Your situation, and what you want to do',
        'The goal of the website']),
    ('Then', 'Me.', 'I take over.', [
        'A price in writing, within five days',
        'Help finding a domain name that’s available',
        'The design and the build, start to finish',
        'Domain, hosting and email set up',
        'SEO for Google, Bing, DuckDuckGo and more']),
    ('Before launch', 'Us.', 'One checkpoint.', [
        'You see it before anyone else',
        'You say yes, or tell me what to change',
        'Then it goes live'])]
PHASE_NOTE = 'Once I take the job, I’ll send a short list of what I need and how to send it: your logo, as many photos as you can, and your main headline or slogan, key phrases, wording or other guidelines. I’ll write the rest.'


def phases():
    """V33: each step has a small animated scene above it (src/partials/how-scenes.html, generated) and a dot that runs along
    the trail when one step hands over to the next. The whole list is revealed as one block, so all three scenes share a clock."""
    scenes = [s.strip() for s in read('how-scenes.html').split('-->', 1)[1].split('<!-- next -->')]
    cols = []
    for i, (k, h, lead, items) in enumerate(PHASES):
        rows = ''.join(f'<li>{icon("check")}<span>{t}</span></li>' for t in items)
        cols.append(f'''
          <li class="phase phase-{i + 1}">
            <i class="phase-pulse" aria-hidden="true"></i>
            <div class="phase-scene" aria-hidden="true">{scenes[i]}</div>
            <p class="phase-k">{ARROW if i else ''}{k}</p>
            <h3 class="phase-h">{h}</h3>
            <p class="phase-lead">{lead}</p>
            <ul class="phase-list" role="list">{rows}</ul>
          </li>''')
    return f'''        <ol class="phases" role="list" data-reveal>{''.join(cols)}
        </ol>
        <p class="phases-note" data-reveal>{icon('list')}<span>{PHASE_NOTE}</span></p>'''


# ---- What I do: six services, one line each (V15: the tabs and the little scenes are gone; Jeremy wanted the site simpler.
#      V31: search engine setup added at Jeremy's request, "SEO optimization for bing/google/duckduckgo and more") ----
SERVICES = [('layout', 'Website design and build', 'Made for your business. No templates.'),
            ('wrench', 'Fixes and single pages', 'Something broken, or one new page. Days, not weeks.'),
            ('globe', 'Domain search and setup', 'I’ll help you find a name that’s available, then register it in your name.'),
            ('server', 'Hosting and small updates', 'No monthly fee. Changes quoted per job.'),
            ('mail', 'Business email setup', 'you@yourbusiness.com, set up and handed over.'),
            ('search', 'Search engine setup', 'Built so Google, Bing, DuckDuckGo and the rest can find and read it.')]


def services():
    """Six plates, each with a big line icon (the sprite), a name and one line."""
    rows = ''.join(f'''
          <li class="svc" data-reveal><span class="plate-ic" aria-hidden="true">{icon(ic)}</span><h3>{h}</h3><p>{t}</p></li>''' for ic, h, t in SERVICES)
    return f'''        <ul class="svc-list" role="list">{rows}
        </ul>'''


# ---- Who you'll work with: the brand story beside the promises in numbers ------------------------
STORY = 'A stray wolf doesn’t run with the pack. Neither should your website. I build sites that are bold, different and made around your business.'


# ---- The work: one clean picture of each site, in a browser frame -------------------------
def srcset(img):
    return f'images/work/{img}-desktop-480.webp 480w, images/work/{img}-desktop-640.webp 640w, images/work/{img}-desktop-960.webp 960w, images/work/{img}-desktop-1440.webp 1440w'


def host(link):
    return re.sub(r'^https?://', '', link).rstrip('/')


def phone_of(img):
    """The phone picture of a site, when there is one (docs/images/work/<image>-phone-300.webp)."""
    if (DOCS / 'images' / 'work' / f'{img}-phone-300.webp').exists():
        return f'<div class="mount-phone" aria-hidden="true"><img src="images/work/{img}-phone-300.webp" srcset="images/work/{img}-phone-300.webp 300w, images/work/{img}-phone-600.webp 600w" sizes="10rem" width="300" height="650" loading="lazy" decoding="async" alt=""></div>'
    return ''


def logo_of(s):
    """The business's own logo above its name, when sites.py names one (docs/images/work/<file>)."""
    logo = s.get('logo')
    if not logo or not (DOCS / 'images' / 'work' / logo[0]).exists():
        return ''
    return f'<img class="site-logo" src="images/work/{logo[0]}" width="{logo[1]}" height="{logo[2]}" alt="" loading="lazy" decoding="async">'


def mount(s, sizes, phone=True):
    """A site's homepage on a stone mount (and its phone view, when there is one). The picture links to the live site."""
    name, img, link = esc(s['name']), s['image'], esc(s['link'])
    pic = f'<img src="images/work/{img}-desktop-960.webp" srcset="{srcset(img)}" sizes="{sizes}" width="1440" height="900" loading="lazy" decoding="async" alt="">'
    return f'''<div class="mount"><a class="mount-pic" href="{link}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">{pic}</a>{phone_of(img) if phone else ''}</div>'''


def visit(s, cls='button button-quiet'):
    name, link = esc(s['name']), esc(s['link'])
    return f'<a class="{cls}" href="{link}" target="_blank" rel="noopener">Visit the site{icon("arrow-out")}<span class="visually-hidden">: {name} (opens in a new tab)</span></a>'


def carousel(sites):
    """The homepage work: one site at a time on its mount, moving on by itself every few seconds, with a pause button.
    It stops once someone uses the arrows, the bars or swipes, and never moves for reduced motion."""
    slides = []
    for s in sites:
        tag = f'<span class="tag">{esc(s["tag"])}</span>' if s.get('tag') else ''
        slides.append(f'''          <li class="slide">
            {mount(s, '(min-width: 64rem) 60vw, 100vw')}
            <div class="slide-text">
              {logo_of(s)}
              <h3 class="slide-name">{esc(s['name'])}</h3>
              <p class="slide-about">{esc(s['about'])}</p>
              {tag}
              {visit(s, 'button button-quiet slide-link')}
            </div>
          </li>''')
    dots = ''.join(f'<button type="button" class="car-dot" data-dot="{i}" aria-label="Show site {i + 1}: {esc(s["name"])}"><i></i></button>' for i, s in enumerate(sites))
    return f'''      <div class="wrap carousel" data-carousel data-autoplay="6000">
        <header class="sec-head">
          <h2 id="work-h" class="h2" data-reveal>Sites I’ve built.</h2>
          <p class="lead" data-reveal>Each one made for one business, from a blank page.</p>
        </header>
        <ul class="track" role="list" data-track aria-label="Websites" tabindex="0">
{chr(10).join(slides)}
        </ul>
        <div class="car-foot">
          <div class="car-dots" role="group" aria-label="Choose a site">{dots}</div>
          <div class="car-nav">
            <button class="car-btn car-play" type="button" data-play aria-label="Pause the slideshow"><svg class="i-pause" aria-hidden="true"><use href="#i-pause"/></svg><svg class="i-play" aria-hidden="true"><use href="#i-play"/></svg></button>
            <button class="car-btn" type="button" data-prev aria-label="Previous site">{icon('arrow-left')}</button>
            <button class="car-btn" type="button" data-next aria-label="Next site">{icon('arrow')}</button>
          </div>
          <a class="link-arrow car-all" href="work.html"><span>See all the work</span>{ARROW}</a>
        </div>
      </div>'''


def work_list(sites):
    """The Work page (Jeremy, Nov 9: "no need to give a deep analysis on their site"): each site big on its mount,
    and beside it only the logo, the name, one line and the link."""
    rows = []
    for i, s in enumerate(sites):
        name = esc(s['name'])
        tag = f'<span class="tag">{esc(s["tag"])}</span>' if s.get('tag') else ''
        rows.append(f'''          <li class="show{' show-flip' if i % 2 else ''}">
            <div class="show-art" data-reveal>{mount(s, '(min-width: 64rem) 62vw, 100vw')}</div>
            <div class="show-side" data-reveal>
              <div class="show-text">
                {logo_of(s)}
                <h2 class="show-name">{name}</h2>
                <p>{esc(s['about'])}</p>
                {tag}
                {visit(s)}
              </div>
            </div>
          </li>''')
    return '        <ol class="shows" role="list">\n' + '\n'.join(rows) + '\n        </ol>'


# ---- Questions people ask -------------------------------------------------------------------
FAQS = [('How much does a website cost?', f'Starter sites from ${STARTER_FROM}, larger ones from ${LARGER_FROM}. Details on the <a class="link" href="pricing.html">Pricing</a> page. Want to see something first? A mockup is ${MOCKUP_FROM} to ${MOCKUP_TO}, and if you go ahead, every dollar of it comes off your final price. One price in writing, before anything starts.'),
        ('Do you take every job?', 'No. I take the jobs I know I can do well, a few at a time. If yours isn’t a fit, I’ll say so up front and point you somewhere better.'),
        ('How long does it take?', 'About 30 days from yes. If you have a date that matters, put it in the form.'),
        ('Do I own the website?', 'Yes. Your domain, your content and your site are yours to keep.'),
        ('Will my site show up on Google?', 'It’s built to. Every site gets the SEO basics: clear titles and descriptions, your business details in the format search engines read, a sitemap and fast pages. Then I submit it to Google and Bing. DuckDuckGo and Yahoo draw on Bing, so that covers them too. Nobody can honestly promise a ranking, so I don’t.'),
        ('What do you need from me?', 'To start, just a conversation. Once I take the job, I’ll need your logo, as many photos as you can, and the words that matter most: your main headline or slogan, key phrases, wording or other guidelines. I’ll write the rest. I’ll send a short list of how to send it all. The 30 days starts when I have it.'),
]


def faq_section():
    items = ''.join(f'''
            <details class="faq" data-reveal>
              <summary><span>{q}</span><span class="faq-ic" aria-hidden="true">{icon('plus')}</span></summary>
              <div class="faq-a"><p>{a}</p></div>
            </details>''' for q, a in FAQS)
    return f'''    <section class="section faq-section tex" aria-labelledby="faq-h">
      <div class="wrap faq-grid">
        <header class="faq-head">
          <h2 id="faq-h" class="h2" data-reveal>Good to know before we start.</h2>
        </header>
        <div class="faqs">{items}
        </div>
      </div>
    </section>'''


# ---- The close: stone, one big line, and the first question right here -----------------------
def close_section(hid='close-h', line='Let’s talk about yours.'):
    return f'''    <section class="close-wrap has-facets facets-left" aria-labelledby="{hid}">
      <div class="wrap close">
        <h2 id="{hid}" data-reveal>{line}</h2>
        <div class="close-side" data-reveal>
          <p>Six quick questions. A reply within five days, with a price in writing.</p>
          <div class="button-row"><a class="button button-lg" href="start.html">Start a project{ARROW}</a></div>
        </div>
      </div>
    </section>'''


sprite = read('sprite.html')
form = read('intake-form.html').replace('{{WEB3FORMS_KEY}}', esc(WEB3FORMS_KEY)).replace('{{FALLBACK_EMAIL}}', esc(FALLBACK_EMAIL)).replace('{{DOMAIN}}', DOMAIN)
layout = (SRC / 'layout.html').read_text(encoding='utf-8')
# Content Security Policy as a meta tag (GitHub Pages can't send headers): only this site's own files run or load.
# The one inline script in the layout is allowed by its hash, worked out here so editing it can't break the page.
# form-action is left out on purpose so the Web3Forms post and its redirect are never blocked.
import hashlib, base64
_hashes = ' '.join("'sha256-" + base64.b64encode(hashlib.sha256(m.encode('utf-8')).digest()).decode() + "'"
                   for m in re.findall(r'<script>(.*?)</script>', layout, re.S))
# With GA4_ID set, Google's own list of what GA4 needs is added (googletagmanager.com for the script, google-analytics.com to send).
_ga_script = ' https://*.googletagmanager.com' if GA4_ID else ''
# (*.g.doubleclick.net and *.google.com are only used if Google signals is turned on in GA4; listed so it can't throw console errors)
_ga_send = ' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://*.g.doubleclick.net https://*.google.com' if GA4_ID else ''
_ga_img = ' https://*.google-analytics.com https://*.googletagmanager.com https://*.g.doubleclick.net https://*.google.com' if GA4_ID else ''
CSP = ("default-src 'self'; script-src 'self' " + _hashes + _ga_script + "; style-src 'self' 'unsafe-inline'; img-src 'self' data:" + _ga_img + "; "
       "font-src 'self'; connect-src 'self'" + _ga_send + "; object-src 'none'; base-uri 'self'; upgrade-insecure-requests")
layout = (layout.replace('{{CSP}}', f'  <meta http-equiv="Content-Security-Policy" content="{CSP}">\n')
          .replace('{{ANALYTICS}}', f'  <script src="js/analytics.js?v={{{{V}}}}" data-ga="{esc(GA4_ID)}" async></script>\n' if GA4_ID else ''))
LOGO_W, LOGO_H = viewbox((DOCS / 'images' / 'brand' / 'stray-wolf-logo-color.svg').read_text(encoding='utf-8'))


def load(name):
    spec = importlib.util.spec_from_file_location(name, SRC / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    return spec, mod

spec, sites_mod = load('sites')
spec.loader.exec_module(sites_mod)
SITES = sites_mod.SITES


def finish(file, html):
    """Applies the launch settings to a finished page."""
    if LAUNCHED and file not in HIDDEN:
        html = html.replace(ROBOTS_META, '')
    if LAUNCHED:
        html = html.replace(BANNER, '')
    if re.search(r'\[(PLACEHOLDER|CONFIRM)', html):
        sys.exit(f'{file}: a [PLACEHOLDER] or [CONFIRM] tag would be shown to visitors. Fix it in src/ first.')
    return html


def ld_json(file, title, desc):
    """Structured data for search engines: the business, the site, this page and where it sits, plus prices and FAQs where they're shown."""
    import json
    base = f'https://{DOMAIN}/'
    url = base + ('' if file == 'index.html' else file)
    business = {
        '@type': 'ProfessionalService', '@id': base + '#business',   # a kind of LocalBusiness (and of Organization), matching the Business Profile
        'name': 'Stray Wolf Technology', 'alternateName': 'Stray Wolf',
        'description': TAGLINE, 'url': base,
        'logo': {'@type': 'ImageObject', 'url': base + 'images/stray-wolf-logo-512.png', 'width': 512, 'height': 512},
        'image': base + 'images/og-card.jpg',
        'founder': {'@type': 'Person', 'name': 'Jeremy'},
        'address': {'@type': 'PostalAddress', 'addressRegion': 'TX', 'addressCountry': 'US'},   # "based in Texas" (privacy page); no street address on purpose
        'areaServed': [{'@type': 'City', 'name': f'{c}, {st}'} for c, st in SERVICE_AREAS],   # matches the Business Profile's service areas
        'knowsAbout': ['Website design', 'Web development', 'Domain registration', 'Website hosting', 'Business email setup'],
    }
    if EMAIL:
        business['email'] = EMAIL
        business['contactPoint'] = {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'url': base + 'start.html', 'availableLanguage': 'English'}
    if PHONE:
        business['telephone'] = tel
        business['contactPoint']['telephone'] = tel
    same_as = SAME_AS + ([GOOGLE_PROFILE_URL] if GOOGLE_PROFILE_URL and GOOGLE_PROFILE_URL not in SAME_AS else [])
    if same_as:
        business['sameAs'] = same_as
    graph = [
        {'@type': 'WebSite', '@id': base + '#website', 'name': 'Stray Wolf Technology',
         'alternateName': ['Stray Wolf', DOMAIN], 'url': base, 'inLanguage': 'en-US', 'publisher': {'@id': base + '#business'}},
        business,
    ]
    name = title.split(' | ')[0]
    webpage = {'@type': 'AboutPage' if file == 'about.html' else 'ContactPage' if file == 'start.html' else 'WebPage',
               '@id': url + '#webpage', 'url': url, 'name': name, 'description': desc, 'inLanguage': 'en-US',
               'isPartOf': {'@id': base + '#website'}, 'about': {'@id': base + '#business'},
               'primaryImageOfPage': {'@type': 'ImageObject', 'url': base + 'images/og-card.jpg'}}
    if file != 'index.html':
        webpage['breadcrumb'] = {'@id': url + '#breadcrumb'}
        graph.append({'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': base},
            {'@type': 'ListItem', 'position': 2, 'name': name.split(':')[0]}]})
    graph.insert(2, webpage)
    plain = lambda h: re.sub(r'\s+', ' ', htmlesc.unescape(re.sub(r'<[^>]+>', '', h))).strip()
    if file == 'index.html':
        graph.append({'@type': 'FAQPage', '@id': url + '#faq', 'isPartOf': {'@id': url + '#webpage'}, 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQS]})
    if file == 'pricing.html':
        def offer(n, low, text):
            return {'@type': 'Offer', 'name': n, 'description': text, 'url': url,
                    'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': int(low.replace(',', '')), 'priceCurrency': 'USD'},
                    'itemOffered': {'@type': 'Service', 'name': n, 'provider': {'@id': base + '#business'}}}
        graph.append({'@type': 'Service', '@id': url + '#service', 'name': 'Website design and build', 'serviceType': 'Website design',
                      'provider': {'@id': base + '#business'}, 'areaServed': business['areaServed'], 'url': url,
                      'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Website projects', 'itemListElement': [
                          offer('Starter website', STARTER_FROM, 'Up to five pages, written with you and built around your business. Domain and email set up.'),
                          offer('Larger website', LARGER_FROM, 'More pages, or a site that does more: booking, a price list you change yourself, a small shop.'),
                          offer('Homepage mockup', MOCKUP_FROM, f'Your homepage designed first. ${MOCKUP_FROM} to ${MOCKUP_TO}, credited in full if the site goes ahead.'),
                          offer('Fix to an existing website', FIX_FROM, 'A fix to a website you already have.'),
                          offer('New page on an existing website', PAGE_FROM, 'One new page on a website you already have.'),
                          offer('Website refresh', REFRESH_FROM, 'New words and photos across the pages you have.')]}})
    body = json.dumps({'@context': 'https://schema.org', '@graph': graph}, indent=2, ensure_ascii=False).replace('</', '<\\/')
    return '  <script type="application/ld+json">\n' + body + '\n  </script>\n'


CHANGED = set()   # pages whose content changed in this build, for the sitemap's <lastmod> dates


def page(file, title, desc, main, current=None, body_class='inner', banner=True, ld=False):
    url = f'https://{DOMAIN}/{"" if file == "index.html" else file}'
    html = (layout.replace('{{TITLE}}', esc(title)).replace('{{DESC}}', esc(desc))
            .replace('{{ROBOTS}}', ROBOTS_META)
            .replace('{{VERIFY}}', (f'  <meta name="google-site-verification" content="{esc(SEARCH_CONSOLE)}">\n' if SEARCH_CONSOLE else '')
                                   + (f'  <meta name="msvalidate.01" content="{esc(BING_VERIFY)}">\n' if BING_VERIFY else ''))
            .replace('{{CANONICAL}}', '' if file in HIDDEN else f'  <link rel="canonical" href="{url}">\n')
            .replace('{{OG_URL}}', '' if file in HIDDEN else f'  <meta property="og:url" content="{url}">\n')
            .replace('{{YEAR}}', YEAR)
            .replace('{{DOMAIN}}', DOMAIN).replace('{{V}}', VERSION).replace('{{LD}}', '' if file in HIDDEN else ld_json(file, title, desc))
            .replace('{{BODY_CLASS}}', body_class)
            .replace('{{SPRITE}}', sprite).replace('{{BANNER}}', BANNER if banner else '')
            .replace('{{LOGO_W}}', LOGO_W).replace('{{LOGO_H}}', LOGO_H)
            .replace('{{MAIN}}', main).replace('{{REACH}}', reach_block()))
    for key, f in (('{{CUR_HOME}}', 'index.html'), ('{{CUR_WORK}}', 'work.html'), ('{{CUR_PRICING}}', 'pricing.html'),
                   ('{{CUR_REVIEWS}}', 'reviews.html'), ('{{CUR_ABOUT}}', 'about.html'), ('{{CUR_START}}', 'start.html')):
        html = html.replace(key, ' aria-current="page"' if current == f else '')
    html = finish(file, html)
    out = DOCS / file
    same = lambda t: re.sub(r'\?v=\d+', '', t)    # a version bump alone isn't a content change
    if not out.exists() or same(out.read_text(encoding='utf-8')) != same(html):
        CHANGED.add(file)
    out.write_text(html, encoding='utf-8')
    print('built', file)


# 1) Homepage
home = (SRC / 'home.html').read_text(encoding='utf-8')
home = (home.replace('{{HERO}}', hero()).replace('{{SERVICES}}', services()).replace('{{CAROUSEL}}', carousel(SITES))
        .replace('{{TIMELINE}}', phases()).replace('{{FAQ}}', faq_section())
        .replace('{{CLOSE}}', close_section()))
page('index.html', 'Stray Wolf Technology | Bespoke websites for owner-run businesses', HOME_DESC, home, current='index.html', body_class='home', ld=True)

# 2) Inner pages (content in src/pages.py)
spec, mod = load('pages')
mod.page = page
mod.form = form
mod.SITES = SITES
mod.work_list = work_list
mod.services = services
mod.close_section = close_section
for _n in ('icon', 'ARROW', 'faq_section', 'phases', 'mount', 'visit', 'host', 'esc', 'STORY', 'PROMISES', 'HEADSHOT', 'photo_or_mark',
           'STARTER_FROM', 'LARGER_FROM', 'FIX_FROM', 'PAGE_FROM', 'REFRESH_FROM', 'MOCKUP_FROM', 'MOCKUP_TO', 'REVIEWS',
           'google_profile_link', 'google_review_badge', 'GOOGLE_PROFILE_URL', 'GOOGLE_REVIEW_URL'):
    setattr(mod, _n, globals()[_n])
mod.read = read
mod.WAYS = WAYS
mod.CONTACT = {'email': EMAIL_LINK, 'phone': PHONE_LINK, 'booking': BOOKING_LINK}
spec.loader.exec_module(mod)

# 3) 404 must work at any address, so its links start from the site's root folder ("/" on the domain).
SITE_ROOT = '/'
p404 = DOCS / '404.html'
s = p404.read_text(encoding='utf-8')
s = re.sub(r'(href|src)="(?!https?:|#|mailto:|tel:|/)([^"]+)"', lambda m: f'{m.group(1)}="{SITE_ROOT}{m.group(2)}"', s)
p404.write_text(s, encoding='utf-8')
print('404.html made root-relative')

# 4) Old addresses: send them on (contact and brand from the Firemark site; care.html from the dropped care plan)
for old, new in (('contact.html', 'start.html'), ('brand.html', 'index.html'), ('care.html', 'pricing.html')):
    clean = '' if new == 'index.html' else new
    (DOCS / old).write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Moved | Stray Wolf Technology</title><meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="https://{DOMAIN}/{clean}"></head>
<body><p>This page has moved to <a href="{new}">{new}</a>.</p></body></html>
''', encoding='utf-8')
    print('redirect', old, '->', new)

# 4b) The short review link, straywolftech.com/review/: Google's review form once GOOGLE_REVIEW_URL is set, the Reviews page until then
(DOCS / 'review').mkdir(exist_ok=True)
_rv = GOOGLE_REVIEW_URL or f'https://{DOMAIN}/reviews.html'
(DOCS / 'review' / 'index.html').write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Review Stray Wolf Technology</title><meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url={esc(_rv)}"></head>
<body><p>Taking you to <a href="{esc(_rv)}">{'the review form on Google' if GOOGLE_REVIEW_URL else 'the Reviews page'}</a>.</p></body></html>
''', encoding='utf-8')
print('redirect review/ ->', _rv)

# 5) Sitemap, robots.txt and the web manifest, so the domain setting flows through
_sm = DOCS / 'sitemap.xml'
_prev = dict(re.findall(r'<loc>https://[^/]+/([^<]*)</loc><lastmod>([^<]+)</lastmod>', _sm.read_text(encoding='utf-8'))) if _sm.exists() else {}
_today = datetime.date.today().isoformat()
def _lastmod(p):
    loc = '' if p == 'index.html' else p
    return _today if p in CHANGED or loc not in _prev else _prev[loc]
_sm.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'  <url><loc>https://{DOMAIN}/{"" if p == "index.html" else p}</loc><lastmod>{_lastmod(p)}</lastmod></url>\n' for p in PUBLIC) + '</urlset>\n', encoding='utf-8')
(DOCS / 'robots.txt').write_text(
    ('# Draft: every page also carries a noindex tag until launch (LAUNCHED in tools/build.py).\n' if not LAUNCHED else '') +
    f'User-agent: *\nAllow: /\n\nSitemap: https://{DOMAIN}/sitemap.xml\n', encoding='utf-8')
(DOCS / 'site.webmanifest').write_text(f'''{{
  "name": "Stray Wolf Technology",
  "short_name": "Stray Wolf",
  "description": "{TAGLINE}",
  "id": "/",
  "start_url": "/",
  "lang": "en-US",
  "icons": [
    {{ "src": "images/favicon-192.png", "sizes": "192x192", "type": "image/png" }},
    {{ "src": "images/favicon-512.png", "sizes": "512x512", "type": "image/png" }},
    {{ "src": "images/favicon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }}
  ],
  "theme_color": "#24221F",
  "background_color": "#F7F5F1",
  "display": "browser"
}}
''', encoding='utf-8')
print('built sitemap.xml, robots.txt and site.webmanifest for', DOMAIN, '(launched)' if LAUNCHED else '(draft)')

# 6) Typographer's quotes on every page
subprocess.run([sys.executable, str(ROOT / 'tools' / 'typeset.py')], check=True)
