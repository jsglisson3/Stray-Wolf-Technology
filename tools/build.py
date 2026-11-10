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
VERSION = '31'                 # bump when docs/css/site.css or docs/js/site.js change, so visitors get the new files

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
    # 'https://g.page/r/...',
]

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
        return '<ul class="reach" role="list">' + ''.join(f'<li>{x}</li>' for x in WAYS) + '</ul>'
    return '<p class="muted">The quickest way is the <a href="start.html">Start a project</a> page. You\'ll hear back within five days.</p>'


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
    """The words. V24 (Nov 10 2026): the wolf on the ridge lifts its head and howls every 16 seconds, in step with the moon
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
      <svg class="hero-scene" viewBox="0 0 1200 150" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
        <defs><radialGradient id="hs-glow"><stop offset=".4" stop-color="#E0763A" stop-opacity=".22"/><stop offset=".6" stop-color="#E0763A" stop-opacity=".08"/><stop offset="1" stop-color="#E0763A" stop-opacity="0"/></radialGradient></defs>
        <circle cx="980" cy="70" r="66" fill="url(#hs-glow)"/>
        <circle cx="980" cy="70" r="28" class="hs-sun"/>
        <path class="hs-far" d="M0 150 V92 L90 84 L180 90 L260 76 L330 80 L420 70 L520 84 L600 72 L700 80 L800 66 L900 78 L1000 70 L1100 82 L1200 74 V150Z"/>
        <g transform="translate(250 112) scale(0.2)" class="hs-cactus-far"><use href="#cactus"/></g>
        <path class="hs-mid" d="M0 150 V116 L120 106 L240 118 L380 102 L500 114 L620 104 L760 118 L880 108 L1020 120 L1200 110 V150Z"/>
        <g transform="translate(760 130) scale(0.3)" class="hs-cactus"><use href="#cactus"/></g>
        <g transform="translate(900 128) scale(0.42)" class="hs-cactus"><use href="#cactus"/></g>
        <g transform="translate(1110 132) scale(0.26)" class="hs-cactus"><use href="#cactus"/></g>
        <path class="hs-near" d="M0 150 V134 L160 128 L320 136 L480 126 L640 134 L800 128 L960 138 L1120 130 L1200 134 V150Z"/>
        <g transform="translate(440 130) scale(0.42)" class="hs-wolf">
          <g class="hs-stand"><use href="#wolf-far-hind" opacity=".85"/><use href="#wolf-far-front" opacity=".85"/><use class="hs-level" href="#wolf-level"/><use class="hs-howl" href="#wolf-howl"/></g>
          <g class="hs-run"><g class="run-body"><use href="#wolf-run"/><use class="gait-1" href="#wolf-legs-1"/><use class="gait-2" href="#wolf-legs-2"/><use class="gait-3" href="#wolf-legs-3"/><use class="gait-4" href="#wolf-legs-4"/></g></g>
        </g>
        <path d="M0 150 H1200" class="hs-line"/>
      </svg>
    </section>'''


# ---- How it works (V16, Nov 9 2026): three columns. The client's part, then Jeremy takes over, then one checkpoint.
# V29 (Nov 10 2026, Jeremy on how he really works): it starts with a conversation. From the client he needs the logo, as many photos
# as they can send and the few words that matter most (a main headline or slogan); he writes the rest. He helps find a domain
# name that is available, not just register it. Once he takes the job he sends a short list of what to send and how (PHASE_NOTE).
PHASES = [
    ('First', 'You.', 'Tell me what you want.', [
        'A conversation about your business and your goals',
        'Your logo, and as many photos as you can',
        'Your main headline or slogan, key phrases, wording or other guidelines. I’ll write the rest.']),
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
PHASE_NOTE = 'Once I take the job, I’ll send a short list of what I need and how to send it: your photos, your logo, the key words, and your current site if you have one.'


def phases():
    cols = []
    for i, (k, h, lead, items) in enumerate(PHASES):
        rows = ''.join(f'<li>{icon("check")}<span>{t}</span></li>' for t in items)
        cols.append(f'''
          <li class="phase phase-{i + 1}" data-reveal>
            <p class="phase-k">{ARROW if i else ''}{k}</p>
            <h3 class="phase-h">{h}</h3>
            <p class="phase-lead">{lead}</p>
            <ul class="phase-list" role="list">{rows}</ul>
          </li>''')
    return f'''        <ol class="phases" role="list">{''.join(cols)}
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
        ('What do you need from me?', 'Your logo, as many photos as you can, and the words that matter most: your main headline or slogan, key phrases, wording or other guidelines. I’ll write the rest. Once I take the job, I’ll send a short list of how to send it all. The 30 days starts when I have it.'),
]


def faq_section():
    items = ''.join(f'''
            <details class="faq" data-reveal>
              <summary><span>{q}</span><span class="faq-ic" aria-hidden="true">{icon('plus')}</span></summary>
              <div class="faq-a"><p>{a}</p></div>
            </details>''' for q, a in FAQS)
    return f'''    <section class="section faq-section" aria-labelledby="faq-h">
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
        '@type': 'Organization', '@id': base + '#business',
        'name': 'Stray Wolf Technology', 'alternateName': 'Stray Wolf',
        'description': TAGLINE, 'url': base,
        'logo': {'@type': 'ImageObject', 'url': base + 'images/stray-wolf-logo-512.png', 'width': 512, 'height': 512},
        'image': base + 'images/og-card.jpg',
        'founder': {'@type': 'Person', 'name': 'Jeremy'},
        'address': {'@type': 'PostalAddress', 'addressRegion': 'TX', 'addressCountry': 'US'},   # "based in Texas" (privacy page); no street address on purpose
        'areaServed': {'@type': 'Country', 'name': 'United States'},
        'knowsAbout': ['Website design', 'Web development', 'Domain registration', 'Website hosting', 'Business email setup'],
    }
    if EMAIL:
        business['email'] = EMAIL
        business['contactPoint'] = {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'url': base + 'start.html', 'availableLanguage': 'English'}
    if PHONE:
        business['telephone'] = tel
        business['contactPoint']['telephone'] = tel
    if SAME_AS:
        business['sameAs'] = SAME_AS
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
           'STARTER_FROM', 'LARGER_FROM', 'FIX_FROM', 'PAGE_FROM', 'REFRESH_FROM', 'MOCKUP_FROM', 'MOCKUP_TO', 'REVIEWS'):
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
