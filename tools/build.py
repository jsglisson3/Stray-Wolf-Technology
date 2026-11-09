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
LAUNCHED = False              # True on launch day: removes the draft banner and the noindex tag from public pages
HIDDEN = {'404.html', 'thanks.html', 'contact.html', 'brand.html'}   # never listed for search engines
PUBLIC = ['index.html', 'work.html', 'pricing.html', 'reviews.html', 'about.html', 'start.html', 'privacy.html']   # listed in sitemap.xml
VERSION = '15'                 # bump when docs/css/site.css or docs/js/site.js change, so visitors get the new files

# ---- Contact details: fill these in when they exist, then rebuild ------------------
# Anything left empty is simply left off the site (no placeholder text is ever shown).
EMAIL = 'info@straywolftech.com'                    # e.g. 'jeremy@straywolftech.com'  (shows in the footer and on the Start page)
PHONE = ''                    # e.g. '(469) 555-0123'            (same places; tap to call on phones)
BOOKING_URL = ''              # e.g. a Cal.com or Calendly link for "Book a 15-minute call"
HEADSHOT = False              # True once docs/images/jeremy.webp is a real photo (4:3 or square, 1200px wide or more); used on the About page
WEB3FORMS_KEY = '0cf93fa5-b765-42a7-9364-2d5a1517d084'            # the access key from web3forms.com; until then the form opens a pre-filled email
FALLBACK_EMAIL = 'info@straywolftech.com'   # where the pre-filled email goes if the form service is ever unreachable

# ---- Prices (FIRST DRAFT, Nov 9 2026: Jeremy's call; change the numbers here and rebuild) ----------
STARTER_FROM = '1,800'        # a starter site, up to five pages ("from $...")
LARGER_FROM = '3,500'         # a larger site: more pages, booking, a menu, a gallery, a small shop
FIX_FROM = '150'              # smaller jobs on a site that already exists: a fix ...
PAGE_FROM = '400'             # ... one new page ...
REFRESH_FROM = '900'          # ... new photos and words across the pages you have
# No monthly fees, ever (Jeremy, Nov 9 2026): the care plan is gone; care.html now sends people to pricing.html.
# -----------------------------------------------------------------------------------

# ---- Reviews: real words only, with the client's OK to quote them by name. Empty = the page says "coming soon". ----
REVIEWS = [
    # ('The words the client wrote, as written.', 'First Last', 'Business name', 'https://their-site.com'),   # url can be ''
]

# ---- Google Search Console: paste the content value from the "HTML tag" method here, then rebuild ----
SEARCH_CONSOLE = ''           # e.g. 'AbCdEf123...' from <meta name="google-site-verification" content="...">

TAGLINE = 'Bespoke, hand-built websites. One designer, working by referral, for owner-run businesses.'
HOME_DESC = 'Bespoke, hand-built websites for owner-run businesses. One designer, by referral, with a price in writing before anything starts.'   # the homepage's line in search results
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


# ---- Hero: paper on the left, a charcoal panel on the right ------------------------------
# The panel shows a small example website going from sketch to finished: "built around your needs".
# It's made of plain HTML boxes (no client's site, no stock photo). Visitors can flip between the sketch
# and the finished page, and between three kinds of business, each with its own colours, layout and button.
H1_A = 'A website built around'
H1_B = 'your needs.'
H1 = f'{H1_A} {H1_B}'
LEAD = 'Hand-built websites, designed around your business. I work on my own, so you deal with one person from the first call to launch day.'
PROMISES = [('craft', 'Hand-built', 'No templates or page builders'),
            ('key', 'Yours to keep', 'Your domain, your site'),
            ('calendar', 'About 30 days', 'From answers to launch')]


def hero():
    """The words. The headline on the left; the lead, the buttons and one small picture of a recent site on the right.
    The picture changes by itself every few seconds (site.js, "The hero"); the full showcase is on the Work page."""
    imgs = []
    for i, s in enumerate(SITES):
        im = s['image']
        imgs.append(f'<img src="images/work/{im}-desktop-480.webp" srcset="images/work/{im}-desktop-480.webp 480w, images/work/{im}-desktop-640.webp 640w" sizes="88px" width="480" height="300" alt="{esc(s["name"])}: the homepage" class="{"is-on" if i == 0 else ""}" data-site-img data-name="{esc(s["name"])}" data-link="{esc(s["link"])}" data-domain="{esc(host(s["link"]))}"{"" if i == 0 else " loading=\"lazy\""} decoding="async">')
    first = SITES[0]
    return f'''    <section class="hero" aria-labelledby="hero-h">
      <div class="wrap hero-grid">
        <h1 id="hero-h" class="hero-h1">{H1_A} <em>{H1_B}</em></h1>
        <div class="hero-text">
          <p class="hero-lead">{LEAD}</p>
          <div class="button-row">
            <a class="button button-lg" href="start.html">Start a project{ARROW}</a>
            <a class="button button-quiet button-lg" href="#how">How it works</a>
          </div>
          <a class="hero-recent" href="work.html" data-sites data-every="3200">
            <span class="hero-recent-frame" aria-hidden="true">{''.join(imgs)}</span>
            <span class="hero-recent-text"><span class="hero-recent-k">Recently built</span><span class="hero-recent-name" data-site-name>{esc(first['name'])}</span></span>
            <span class="hero-recent-go">See the work{ARROW}</span>
          </a>
        </div>
      </div>
    </section>'''


# ---- How it works: a 30-day ruler with the four steps under it ---------------------------------
# Each step lights up when the orange line along the ruler reaches its day (DAY is where that is, out of 30).
STEPS = [(1, 'Day 1', 'You answer six questions', 'About two minutes on the Start a project page.'),
         (5, 'Within 5 days', 'We talk', 'I learn exactly what you want from your website, then send a price in writing.'),
         (8, 'Your 10%', 'You send the words, photos and logo', 'Be clear about what you want, and send the text, images and logo you have. The 30 days starts when they arrive.'),
         (19, 'The build', 'I design and build it by hand', 'You see it before anyone else and we shape it together.'),
         (30, 'About day 30', 'You say yes. It goes live.', 'Nothing launches until you’ve seen it and approved it.')]


def timeline():
    ticks = ''.join(
        f'<i class="{"is-5" if d in (1, 5, 10, 15, 20, 25, 30) else ""}{" is-10" if d in (10, 20) else ""}">{f"<b>{d}</b>" if d in (1, 5, 10, 15, 20, 25) else ("<b>30 <small>days</small></b>" if d == 30 else "")}</i>'
        for d in range(1, 31))
    items = ''.join(f'''
          <li class="rs-step" data-day="{day}" data-reveal>
            <p class="rs-when">{when}</p>
            <h3>{h}</h3>
            <p>{t}</p>
          </li>''' for day, when, h, t in STEPS)
    return f'''        <div class="ruler" data-timeline>
          <div class="ruler-scale" aria-hidden="true"><div class="ruler-ticks">{ticks}</div><span class="ruler-fill"></span></div>
          <ol class="ruler-steps" role="list">{items}
          </ol>
        </div>'''


# ---- What I do: five services, one line each (V15: the tabs and the little scenes are gone; Jeremy wanted the site simpler) ----
SERVICES = [('Website design and build', 'By hand, for your business. No templates, no page builders.'),
            ('Fixes and single pages', 'Something broken on the site you have, or one new page added to it. Days, not weeks, with a price in writing first.'),
            ('Domain registration and setup', 'I register it in your name and point it at your site.'),
            ('Hosting and small updates', 'After launch the site stays up with no monthly fee. Small changes are quoted per job and done within days.'),
            ('Business email setup', 'A professional address like you@yourbusiness.com instead of a Gmail, set up and handed over to you.')]


def services():
    rows = ''.join(f'''
          <li data-reveal><h3>{h}</h3><p>{t}</p></li>''' for h, t in SERVICES)
    return f'''        <ul class="svc-list" role="list">{rows}
        </ul>'''


# ---- Who you'll work with: the brand story beside the promises in numbers ------------------------
STORY = 'A stray wolf doesn’t run with a pack, and neither do I. I build websites on my own, for businesses that want to stand out.'
NUMBERS = [('1', 'person, from the first call to launch day'),
           ('14', 'questions to get started'),
           ('5', 'days, at most, to hear back'),
           ('~30', 'days from yes to launch')]


def numbers_html():
    return '<dl class="numbers">' + ''.join(f'<div data-reveal><dt>{n}</dt><dd>{t}</dd></div>' for n, t in NUMBERS) + '</dl>'


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
              <h3 class="slide-name">{esc(s['name'])}</h3>
              <p class="slide-about">{esc(s['about'])}</p>
              {tag}
              <p class="slide-host">{esc(host(s['link']))}</p>
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
    """The Work page: each site big on its mount, with a second page of it beside when there is one, and the words under a rule."""
    rows = []
    for i, s in enumerate(sites):
        name, img = esc(s['name']), s['image']
        tag = f'<span class="tag">{esc(s["tag"])}</span>' if s.get('tag') else ''
        extra = s.get('extra')
        side = ''
        if extra and (DOCS / 'images' / 'work' / f'{extra[0]}-800.webp').exists():
            side = f'''<figure class="show-extra"><div class="mount-pic"><img src="images/work/{extra[0]}-800.webp" srcset="images/work/{extra[0]}-800.webp 800w, images/work/{extra[0]}-1200.webp 1200w" sizes="(min-width: 64rem) 30vw, 92vw" width="800" height="{extra[2]}" loading="lazy" decoding="async" alt="{esc(name)}: {esc(extra[1].lower())}."></div><figcaption>{esc(extra[1])}</figcaption></figure>'''
        rows.append(f'''          <li class="show{' show-flip' if i % 2 else ''}">
            <div class="show-art" data-reveal>{mount(s, '(min-width: 64rem) 62vw, 100vw')}</div>
            <div class="show-side" data-reveal>
              {side}
              <div class="show-text">
                <h2 class="show-name">{name}</h2>
                <p>{esc(s['about'])}</p>
                {tag}
                <p class="show-host">{esc(host(s['link']))}</p>
                {visit(s)}
              </div>
            </div>
          </li>''')
    return '        <ol class="shows" role="list">\n' + '\n'.join(rows) + '\n        </ol>'


# ---- Questions people ask -------------------------------------------------------------------
FAQS = [('How much does a website cost?', f'Starter sites begin at ${STARTER_FROM} and larger ones at ${LARGER_FROM}; the <a class="link" href="pricing.html">Pricing</a> page has the details. After we talk you get one price in writing, before anything starts. No tiers, no surprise add-ons.'),
        ('Do you take every job?', 'No. I’m not trying to take on as much work as I can, or make as much money as I can. I take the jobs I know I can do well, a few at a time, and I turn down the ones I don’t think I can do right. If yours isn’t a fit, I’ll say so up front and point you somewhere better.'),
        ('How long does it take?', 'About 30 days from the time we agree to start. If you have a date that matters, put it in the form and I’ll tell you up front whether it works.'),
        ('Do I own the website?', 'Yes. Your domain, your content and your site are yours to keep.'),
        ('What do you need from me?', 'Three things, and they’re your 10%: a clear idea of what you want, the words for each page, and your photos and logo. The other 90% is mine. The 30 days starts when I have them. No logo or photos yet? Say so and we’ll work it out.'),
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
          <p data-reveal>Something else on your mind? The last box on the <a class="link" href="start.html">Start a project</a> page is for exactly that.</p>
        </header>
        <div class="faqs">{items}
        </div>
      </div>
    </section>'''


# ---- The close: stone, one big line, and the first question right here -----------------------
def close_section(hid='close-h', line='Let’s talk about yours.'):
    return f'''    <section class="close-wrap" aria-labelledby="{hid}">
      <div class="wrap close">
        <h2 id="{hid}" data-reveal>{line}</h2>
        <div class="close-side" data-reveal>
          <p>Six quick questions, about two minutes. You’ll hear from me within five days, with a price in writing before anything starts.</p>
          <div class="button-row"><a class="button button-lg" href="start.html">Start a project{ARROW}</a></div>
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
    """Tells search engines the business's name, logo and what the site is called (the name shown above results)."""
    extra = ''
    if EMAIL:
        extra += f',\n        "email": "{EMAIL}"'
    if PHONE:
        extra += f',\n        "telephone": "{tel}"'
    return f'''  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebSite",
        "@id": "https://{DOMAIN}/#website",
        "name": "Stray Wolf Technology",
        "alternateName": ["Stray Wolf", "{DOMAIN}"],
        "url": "https://{DOMAIN}/",
        "inLanguage": "en-US",
        "publisher": {{"@id": "https://{DOMAIN}/#business"}}
      }},
      {{
        "@type": "Organization",
        "@id": "https://{DOMAIN}/#business",
        "name": "Stray Wolf Technology",
        "alternateName": "Stray Wolf",
        "description": "{TAGLINE}",
        "url": "https://{DOMAIN}/",
        "logo": {{"@type": "ImageObject", "url": "https://{DOMAIN}/images/stray-wolf-logo-512.png", "width": 512, "height": 512}},
        "image": "https://{DOMAIN}/images/og-card.jpg",
        "founder": {{"@type": "Person", "name": "Jeremy"}},
        "areaServed": {{"@type": "Country", "name": "United States"}},
        "knowsAbout": ["Website design", "Web development", "Domain registration", "Website hosting", "Business email setup"]{extra}
      }}
    ]
  }}
  </script>
'''


def page(file, title, desc, main, current=None, body_class='inner', banner=True, ld=False):
    url = f'https://{DOMAIN}/{"" if file == "index.html" else file}'
    html = (layout.replace('{{TITLE}}', esc(title)).replace('{{DESC}}', esc(desc))
            .replace('{{ROBOTS}}', ROBOTS_META)
            .replace('{{VERIFY}}', f'  <meta name="google-site-verification" content="{esc(SEARCH_CONSOLE)}">\n' if SEARCH_CONSOLE else '')
            .replace('{{CANONICAL}}', '' if file == '404.html' else f'  <link rel="canonical" href="{url}">\n')
            .replace('{{OG_URL}}', '' if file == '404.html' else f'  <meta property="og:url" content="{url}">\n')
            .replace('{{YEAR}}', YEAR)
            .replace('{{DOMAIN}}', DOMAIN).replace('{{V}}', VERSION).replace('{{LD}}', ld_json() if ld else '')
            .replace('{{BODY_CLASS}}', body_class)
            .replace('{{SPRITE}}', sprite).replace('{{BANNER}}', BANNER if banner else '')
            .replace('{{LOGO_W}}', LOGO_W).replace('{{LOGO_H}}', LOGO_H)
            .replace('{{MAIN}}', main).replace('{{REACH}}', reach_block()))
    for key, f in (('{{CUR_HOME}}', 'index.html'), ('{{CUR_WORK}}', 'work.html'), ('{{CUR_PRICING}}', 'pricing.html'),
                   ('{{CUR_REVIEWS}}', 'reviews.html'), ('{{CUR_ABOUT}}', 'about.html'), ('{{CUR_START}}', 'start.html')):
        html = html.replace(key, ' aria-current="page"' if current == f else '')
    (DOCS / file).write_text(finish(file, html), encoding='utf-8')
    print('built', file)


# 1) Homepage
home = (SRC / 'home.html').read_text(encoding='utf-8')
home = (home.replace('{{HERO}}', hero()).replace('{{SERVICES}}', services()).replace('{{CAROUSEL}}', carousel(SITES))
        .replace('{{TIMELINE}}', timeline()).replace('{{FAQ}}', faq_section())
        .replace('{{CLOSE}}', close_section()))
page('index.html', 'Stray Wolf Technology | Bespoke, hand-built websites', HOME_DESC, home, current='index.html', body_class='home', ld=True)

# 2) Inner pages (content in src/pages.py)
spec, mod = load('pages')
mod.page = page
mod.form = form
mod.SITES = SITES
mod.work_list = work_list
mod.services = services
mod.close_section = close_section
for _n in ('icon', 'ARROW', 'faq_section', 'numbers_html', 'timeline', 'mount', 'visit', 'host', 'esc', 'STORY', 'PROMISES', 'HEADSHOT', 'photo_or_mark',
           'STARTER_FROM', 'LARGER_FROM', 'FIX_FROM', 'PAGE_FROM', 'REFRESH_FROM', 'REVIEWS'):
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
  "id": "/",
  "start_url": "/",
  "lang": "en-US",
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
