"""Builds the Stray Wolf website into docs/.

Sources live in src/ (not published):
  src/layout.html                the shell every page shares: head, header, footer ({{...}} slots are filled below)
  src/home.html                  the homepage
  src/pages.py                   the inner pages (Work, About, Start a project, thanks, privacy, 404)
  src/sites.py                   the list of websites shown on the Work page and in the homepage carousel
  src/partials/intake-form.html  the fourteen questions (the Start a project page)
  src/partials/sprite.html       the icons

Run from the project folder:  python3 tools/build.py
"""
import pathlib, re, subprocess, sys, importlib.util, html as htmlesc

# ---- Launch settings ------------------------------------------------------------
DOMAIN = 'straywolftech.com'  # the site's address. docs/CNAME must say the same thing
LAUNCHED = False              # True on launch day: removes the draft banner and the noindex tag from public pages
HIDDEN = {'404.html', 'thanks.html', 'contact.html', 'brand.html'}   # never listed for search engines
PUBLIC = ['index.html', 'work.html', 'about.html', 'start.html', 'privacy.html']   # listed in sitemap.xml
VERSION = '3'                 # bump when docs/css/site.css or docs/js/site.js change, so visitors get the new files
HERO = 'B'                    # the homepage hero layout: 'A' (mark on a tile), 'B' (charcoal panel), 'C' (centred)

# ---- Contact details: fill these in when they exist, then rebuild ------------------
# Anything left empty is simply left off the site (no placeholder text is ever shown).
EMAIL = ''                    # e.g. 'jeremy@straywolftech.com'  (shows in the footer and on the Start page)
PHONE = ''                    # e.g. '(469) 555-0123'            (same places; tap to call on phones)
BOOKING_URL = ''              # e.g. a Cal.com or Calendly link for "Book a 15-minute call"
HEADSHOT = False              # True once docs/images/jeremy.webp is a real photo (4:3 or square, 1200px wide or more)
WEB3FORMS_KEY = ''            # the access key from web3forms.com; until then the form opens a pre-filled email
FALLBACK_EMAIL = 'jsglisson@gmail.com'   # where that pre-filled email goes. Swap for the straywolftech.com address once it exists.
# -----------------------------------------------------------------------------------

TAGLINE = 'Bespoke, hand-built websites. One designer, working by referral, for businesses anywhere in the US.'
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
    name = 'stray-wolf-logo-stacked-reverse.svg' if dark else 'stray-wolf-symbol-color.svg'
    return f'<img src="images/brand/{name}" width="200" height="190" loading="lazy" decoding="async" alt="">'


# ---- Hero: one of three layouts (HERO above) ------------------------------------------
H1 = 'A website built around your needs.'
LEAD = 'Bespoke, hand-built websites. I work on my own, by referral, so you deal with one person from the first call to launch day.'
FACTS = [('Hand-built', 'No templates, no page builders. Designed and written for your business.'),
         ('By referral', 'A few clients at a time, so each one gets my full attention.'),
         ('Live in about 45 days', 'A price in writing before anything starts. Nothing goes live until you say yes.')]


def facts_html(tag='h2'):
    return '<div class="facts">' + ''.join(f'<div data-reveal><{tag}>{h}</{tag}><p>{t}</p></div>' for h, t in FACTS) + '</div>'


def hero():
    buttons = '<div class="button-row"><a class="button" href="start.html">Start a project</a><a class="button button-ghost" href="#how">How it works</a></div>'
    if HERO == 'A':
        return f'''    <section class="hero hero-a" aria-labelledby="hero-h">
      <div class="wrap hero-grid">
        <div class="hero-text">
          <h1 id="hero-h" class="h1">{H1}</h1>
          <p class="lead">{LEAD}</p>
          {buttons}
        </div>
        <div class="hero-tile{' has-photo' if HEADSHOT else ''}">{photo_or_mark(dark=False)}</div>
      </div>
      <div class="wrap facts-row">{facts_html()}</div>
    </section>'''
    if HERO == 'C':
        return f'''    <section class="hero hero-c" aria-labelledby="hero-h">
      <div class="wrap hero-text">
        <p class="kicker">Bespoke websites by one designer</p>
        <h1 id="hero-h" class="h1">{H1}</h1>
        <p class="lead">{LEAD}</p>
        {buttons}
      </div>
      <div class="facts-band on-stone">
        <img class="watermark" src="images/brand/stray-wolf-symbol-mono-dark.svg" width="200" height="200" alt="" aria-hidden="true">
        <div class="wrap">{facts_html()}</div>
      </div>
    </section>'''
    return f'''    <section class="hero hero-b" aria-labelledby="hero-h">
      <div class="hero-grid">
        <div class="hero-text">
          <h1 id="hero-h" class="h1">{H1}</h1>
          <p class="lead">{LEAD}</p>
          <ul class="ticks" role="list">
            <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg><span>No templates, no page builders</span></li>
            <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg><span>A price in writing before anything starts</span></li>
            <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg><span>Live in about 45 days</span></li>
          </ul>
          {buttons}
        </div>
        <div class="hero-panel{' has-photo' if HEADSHOT else ''}">
          {photo_or_mark(dark=True)}
          {'' if HEADSHOT else '<p>Bespoke websites · Referral only · Anywhere in the US</p>'}
        </div>
      </div>
    </section>'''


# ---- What I do ----------------------------------------------------------------------
SERVICES = [('Website design and build', 'By hand, for your business. No templates, no page builders.'),
            ('Domain registration and setup', 'I register it in your name and point it at your site.'),
            ('Hosting and small updates', 'After launch I keep the site up and make the small changes as they come.'),
            ('Email at your own domain', 'An address like you@yourbusiness.com, set up and handed over to you.')]


def services():
    items = ''.join(f'<li class="service" data-reveal><h3>{h}</h3><p>{t}</p></li>' for h, t in SERVICES)
    return f'''        <ul class="services" role="list">{items}</ul>
        <p class="services-note" data-reveal>Google Business Profile and social media aren’t on the list. I stick to what I’m good at.</p>'''


# ---- The work: one clean picture of each site -------------------------------------------
def srcset(img):
    return f'images/work/{img}-desktop-480.webp 480w, images/work/{img}-desktop-640.webp 640w, images/work/{img}-desktop-960.webp 960w, images/work/{img}-desktop-1440.webp 1440w'


def site_card(s, cls, h='h3', sizes='(min-width: 64rem) 54rem, 86vw'):
    name, about, img, link = esc(s['name']), esc(s['about']), s['image'], esc(s['link'])
    tag = f' <span class="muted">{esc(s["tag"])}</span>' if s.get('tag') else ''
    return f'''          <li class="{cls}" data-reveal>
            <a class="slide-pic" href="{link}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true"><img src="images/work/{img}-desktop-960.webp" srcset="{srcset(img)}" sizes="{sizes}" width="1440" height="900" loading="lazy" decoding="async" alt="The {name} homepage."></a>
            <div class="slide-text">
              <div><{h} class="slide-name">{name}</{h}><p class="slide-about">{about}{tag}</p></div>
              <a class="link slide-link" href="{link}" target="_blank" rel="noopener">Visit the site<span class="visually-hidden">: {name} (opens in a new tab)</span></a>
            </div>
          </li>'''


def carousel(sites):
    slides = '\n'.join(site_card(s, 'slide') for s in sites)
    return f'''        <div class="carousel" data-carousel>
          <div class="car-head">
            <div class="sec-head" style="margin:0">
              <h2 id="work-h" class="h2" data-reveal>Recent work</h2>
              <p class="lead" data-reveal>One clean look at each site. Tap through to see it live.</p>
            </div>
            <div class="car-nav">
              <button class="car-btn" type="button" data-prev aria-label="Previous site"><svg aria-hidden="true"><use href="#i-arrow-left"/></svg></button>
              <button class="car-btn" type="button" data-next aria-label="Next site"><svg aria-hidden="true"><use href="#i-arrow"/></svg></button>
            </div>
          </div>
          <ul class="track" role="list" data-track aria-label="Websites">
{slides}
          </ul>
        </div>
        <p class="car-more" data-reveal><a class="link" href="work.html">See all the work</a></p>'''


def work_list(sites):
    return '        <ul class="work-grid" role="list">\n' + '\n'.join(site_card(s, 'work-item', h='h2', sizes='(min-width: 48rem) 46vw, 92vw') for s in sites) + '\n        </ul>'


def close_section(hid='close-h', line='Let’s talk about yours.'):
    return f'''    <section class="section close" aria-labelledby="{hid}">
      <div class="wrap close-grid">
        <h2 id="{hid}" data-reveal>{line}</h2>
        <div class="close-act" data-reveal>
          <p>Answer the questions and you'll hear from me within five days, with a price in writing before anything starts.</p>
          <a class="button" href="start.html">Start a project</a>
        </div>
      </div>
    </section>'''


sprite = read('sprite.html')
form = read('intake-form.html').replace('{{WEB3FORMS_KEY}}', esc(WEB3FORMS_KEY)).replace('{{FALLBACK_EMAIL}}', esc(FALLBACK_EMAIL)).replace('{{DOMAIN}}', DOMAIN)
layout = (SRC / 'layout.html').read_text(encoding='utf-8')
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


def ld_json():
    extra = ''
    if EMAIL:
        extra += f',\n    "email": "{EMAIL}"'
    if PHONE:
        extra += f',\n    "telephone": "{tel}"'
    return f'''  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Stray Wolf Technology",
    "description": "{TAGLINE}",
    "url": "https://{DOMAIN}/",
    "image": "https://{DOMAIN}/images/og-card.jpg",
    "founder": {{"@type": "Person", "name": "Jeremy"}},
    "areaServed": "US"{extra}
  }}
  </script>
'''


def page(file, title, desc, main, current=None, body_class='inner', banner=True, ld=False):
    html = (layout.replace('{{TITLE}}', esc(title)).replace('{{DESC}}', esc(desc))
            .replace('{{ROBOTS}}', ROBOTS_META)
            .replace('{{CANONICAL}}', '' if file == '404.html' else f'  <link rel="canonical" href="https://{DOMAIN}/{"" if file == "index.html" else file}">\n')
            .replace('{{DOMAIN}}', DOMAIN).replace('{{V}}', VERSION).replace('{{LD}}', ld_json() if ld else '')
            .replace('{{BODY_CLASS}}', body_class)
            .replace('{{SPRITE}}', sprite).replace('{{BANNER}}', BANNER if banner else '')
            .replace('{{LOGO_W}}', LOGO_W).replace('{{LOGO_H}}', LOGO_H)
            .replace('{{MAIN}}', main).replace('{{REACH}}', reach_block()))
    for key, f in (('{{CUR_WORK}}', 'work.html'), ('{{CUR_ABOUT}}', 'about.html'), ('{{CUR_START}}', 'start.html')):
        html = html.replace(key, ' aria-current="page"' if current == f else '')
    (DOCS / file).write_text(finish(file, html), encoding='utf-8')
    print('built', file)


# 1) Homepage
home = (SRC / 'home.html').read_text(encoding='utf-8')
home = (home.replace('{{HERO}}', hero()).replace('{{SERVICES}}', services()).replace('{{CAROUSEL}}', carousel(SITES))
        .replace('{{TILE_CLASS}}', ' has-photo' if HEADSHOT else '').replace('{{TILE}}', photo_or_mark(dark=False)))
page('index.html', 'Stray Wolf Technology | Bespoke, hand-built websites', TAGLINE, home, body_class='home', ld=True)

# 2) Inner pages (content in src/pages.py)
spec, mod = load('pages')
mod.page = page
mod.form = form
mod.SITES = SITES
mod.work_list = work_list
mod.services = services
mod.close_section = close_section
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

# 4) Old addresses from the Firemark site: send them on
for old, new in (('contact.html', 'start.html'), ('brand.html', 'index.html')):
    (DOCS / old).write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="https://{DOMAIN}/{new}"></head>
<body><p>This page has moved to <a href="{new}">{new}</a>.</p></body></html>
''', encoding='utf-8')
    print('redirect', old, '->', new)

# 5) Sitemap, robots.txt and the web manifest, so the domain setting flows through
(DOCS / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'  <url><loc>https://{DOMAIN}/{"" if p == "index.html" else p}</loc></url>\n' for p in PUBLIC) + '</urlset>\n', encoding='utf-8')
(DOCS / 'robots.txt').write_text(
    ('# Draft: every page also carries a noindex tag until launch (LAUNCHED in tools/build.py).\n' if not LAUNCHED else '') +
    f'User-agent: *\nAllow: /\n\nSitemap: https://{DOMAIN}/sitemap.xml\n', encoding='utf-8')
(DOCS / 'site.webmanifest').write_text(f'''{{
  "name": "Stray Wolf Technology",
  "short_name": "Stray Wolf",
  "description": "{TAGLINE}",
  "start_url": "/",
  "icons": [
    {{ "src": "images/favicon-192.png", "sizes": "192x192", "type": "image/png" }},
    {{ "src": "images/favicon-512.png", "sizes": "512x512", "type": "image/png" }},
    {{ "src": "images/favicon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }}
  ],
  "theme_color": "#F7F5F1",
  "background_color": "#F7F5F1",
  "display": "browser"
}}
''', encoding='utf-8')
print('built sitemap.xml, robots.txt and site.webmanifest for', DOMAIN, '(launched)' if LAUNCHED else '(draft)')

# 6) Typographer's quotes on every page
subprocess.run([sys.executable, str(ROOT / 'tools' / 'typeset.py')], check=True)
