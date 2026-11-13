"""Content for the inner pages. tools/build.py runs this file and provides:
   page(file, title, desc, main, current=None, body_class='inner', banner=True)   writes docs/<file>
   form                      the intake questions (src/partials/intake-form.html, with the settings filled in)
   SITES, work_list(sites)   the Work showcase (src/sites.py)
   services()                the "What I do" tiles
   close_section(hid, line)  the closing band with one big line and the Start a project button
   icon(name), ARROW         an icon from src/partials/sprite.html
   photo_or_mark(dark), HEADSHOT, STORY
   read(name)                a partial from src/partials
   CONTACT, WAYS             the email, phone and booking links, or '' while not set
Voice: first person, plain and short. Jeremy by first name only. Nothing unconfirmed goes on a page."""


def page_head(h1, lead, notes=None, cls=''):
    """The top of an inner page: a big title, one line beside it, and a few plain notes under a rule."""
    side = f'<p class="lead">{lead}</p>' + (notes_list(notes) if notes else '')
    return f'''    <section class="page-head has-facets{cls}">
      <div class="wrap page-head-grid">
        <h1 class="h1">{h1}</h1>
        <div class="page-head-side">{side}</div>
      </div>
    </section>'''


def notes_list(items):
    return '<ul class="page-notes" role="list">' + ''.join(f'<li>{t}</li>' for t in items) + '</ul>'


# ---------------------------------------------------------------- Work

work_main = page_head('Sites I’ve designed <em>and built.</em>', 'Each one made for one business. Tap any of them to see it live.',
                      [f'{len(SITES)} sites so far', 'No templates, no page builders', 'Looks right on every screen']) + f'''
    <section class="section work-section" aria-label="Websites">
      <div class="wrap">
{work_list(SITES)}
      </div>
    </section>
{close_section('work-close-h', 'Want yours on this list?')}'''

page('work.html', 'Work: custom websites, one at a time | Stray Wolf Technology',
     'Custom websites Stray Wolf Technology has designed and built for owner-run businesses. Tap any one to see it live.',
     work_main, current='work.html')


# ---------------------------------------------------------------- About
# A profile card, six pledges, and the story behind the name. No case studies, no personal background, nothing about working alone (Jeremy may hire).


PLEDGES = [('craft', 'Made for you', 'One site for one business. No templates, no page builders.'),
           ('chat', 'You first, then the design', 'I learn what you want before I design anything.'),
           ('doc', 'A price in writing', 'Before anything starts. No tiers, no add-ons.'),
           ('eye', 'Nothing goes live without you', 'You see it first. It launches when you say yes.'),
           ('key', 'Yours to keep', 'Your domain, your content and your site.'),
           ('person', 'Straight to me', 'Before and after launch. No account manager in between.')]


def pledge_list(items):
    """Plates with a big line icon, a name and one line (About and Pricing)."""
    return '<ul class="pledges" role="list">' + ''.join(f'''
          <li class="pledge" data-reveal><span class="plate-ic" aria-hidden="true">{icon(ic)}</span><h3>{h}</h3><p>{t}</p></li>''' for ic, h, t in items) + '\n        </ul>'

profile_card = f'''<figure class="profile{' has-photo' if HEADSHOT else ''}" data-reveal>
          <div class="profile-pic">{photo_or_mark(dark=False)}</div>
          <figcaption class="profile-body">
            <p class="profile-name">Jeremy<span>Designer and developer</span></p>
            <p class="profile-status"><span class="dot" aria-hidden="true"></span>Taking a few projects at a time</p>
          </figcaption>
        </figure>'''

about_main = f'''    <section class="about-hero tex" aria-labelledby="about-h">
      <div class="wrap about-hero-grid">
        <div class="about-text">
          <h1 id="about-h" class="h1">Different, <em>on purpose.</em></h1>
          <p class="lead about-lead">Hi, I’m Jeremy. I design and build websites made around one business: yours. No templates, no page builders, and nothing you’ve seen a hundred times before.</p>
          <p class="about-more" data-reveal>I’m not trying to make as much money as I can. I want to do quality work. So I take a few clients at a time, only the jobs I know I can do well, and I’ll turn down one I don’t think I can do right.</p>
          <div class="button-row"><a class="button button-lg" href="start.html">Start a project{ARROW}</a><a class="button button-quiet button-lg" href="work.html">See the work</a></div>
        </div>
        {profile_card}
      </div>
    </section>

    <section class="section tex tex-left tex-b" aria-labelledby="how-h">
      <div class="wrap">
        <header class="sec-head">
          <h2 id="how-h" class="h2" data-reveal>Six things you can count on.</h2>
          <div class="sec-aside" data-reveal>
            <p class="lead">The same promises on every project, written down so you can hold me to them.</p>
          </div>
        </header>
        {pledge_list(PLEDGES)}
      </div>
    </section>

    <section class="section story tex" aria-labelledby="story-h">
      <div class="wrap story-grid">
        <div class="story-art" aria-hidden="true">
          <img src="images/brand/stray-wolf-facets.svg" width="200" height="200" alt="" loading="lazy" decoding="async">
        </div>
        <div class="story-text">
          <h2 id="story-h" class="h2" data-reveal>Stray from <em>the pack.</em></h2>
          <p class="lead" data-reveal>A stray wolf doesn’t run with the pack. That’s the idea behind the name. Your website shouldn’t look like everyone else’s either: it should be bold, different and built around what your business needs.</p>
        </div>
      </div>
    </section>

{close_section('about-close-h')}'''

page('about.html', 'About: bold, custom websites | Stray Wolf Technology',
     'About Stray Wolf Technology and Jeremy: bold, custom websites made around your business, not a template.',
     about_main, current='about.html')


# ---------------------------------------------------------------- Start a project (the intake)

if WAYS:
    talk = '<div class="aside-block"><h2 class="aside-h">Rather talk first?</h2>\n            <ul class="reach-list" role="list">' + ''.join(f'<li>{x}</li>' for x in WAYS) + '</ul></div>'
else:
    talk = '<div class="aside-block aside-tip"><p><strong>Just have a question?</strong> Put it in the last box. You don’t need every answer to send the form.</p></div>'

start_main = page_head('Tell me about <em>your business.</em>', 'Six quick questions, about two minutes. I read every answer, and you’ll hear from me within five days. The rest we work out on a call.',
                       ['About 2 minutes', 'Most answers are optional', 'A reply within 5 days'], cls=' page-head-start') + f'''
    <section class="section section-tight start-section tex tex-left tex-b" aria-label="The questions">
      <div class="wrap start-grid">
        <h2 id="start-h" class="visually-hidden">The questions</h2>
        {form}
        <div class="start-aside">
          <div class="aside-block">
            <h2 class="aside-h">What happens next</h2>
            <ol class="next-steps" role="list">
              <li><strong>Within 5 days</strong>I read your answers and reply. If it’s not something I can do well, I’ll say so.</li>
              <li><strong>Before anything starts</strong>You get a price in writing.</li>
              <li><strong>Your part</strong>You send your logo, photos and key words.</li>
              <li><strong>About 30 days</strong>Your site goes live.</li>
            </ol>
          </div>
          <div class="aside-block aside-safe">
            <h2 class="aside-h">{icon('lock')}Private and secure</h2>
            <ul class="safe-list" role="list">
              <li>Your answers go to me and no one else. Never sold, never shared for marketing.</li>
              <li>Sent over a secure connection. Never added to a mailing list.</li>
              <li>Deleted when you ask. <a href="privacy.html">Privacy</a> and <a href="terms.html">terms</a>, in plain English.</li>
            </ul>
          </div>
          {talk}
        </div>
      </div>
    </section>'''

page('start.html', 'Start a website project | Stray Wolf Technology',
     'Six quick questions about your business and your website, about two minutes. Answer them and Jeremy replies within five days.',
     start_main, current='start.html', body_class='inner page-start')


# ---------------------------------------------------------------- Thanks and 404

def go_cards(links, label):
    return f'''          <nav aria-label="{label}"><ul class="go-cards" role="list">''' + ''.join(
        f'<li><a href="{href}"><span class="go-t"><strong>{text}</strong><small>{sub}</small></span>{ARROW}</a></li>' for href, ic, text, sub in links) + '</ul></nav>'


def end_page(h1, lead, inner, badge, side):
    return f'''    <section class="end-page tex tex-left" aria-labelledby="end-h">
      <div class="wrap end-grid">
        <div class="end-text">{badge}
          <h1 id="end-h" class="h1">{h1}</h1>
          <p class="lead">{lead}</p>
{inner}
        </div>
        <div class="end-side" aria-hidden="true">
          {side}
        </div>
      </div>
    </section>'''


WOLF = '<img src="images/brand/stray-wolf-symbol-color.svg" width="200" height="200" alt="">'

thanks_main = end_page('Got it. Thanks.', 'Your answers are in. Here’s what happens next.', f'''          <ol class="thanks-steps" role="list">
            <li class="is-done"><span class="ts-n">{icon('check')}</span><span><strong>Your answers are in</strong>Nothing else to do right now.</span></li>
            <li><span class="ts-n">2</span><span><strong>I reply within five days</strong>With questions, a time to talk, or an honest no if it’s not something I can do well.</span></li>
            <li><span class="ts-n">3</span><span><strong>A price in writing</strong>Before anything starts.</span></li>
            <li><span class="ts-n">4</span><span><strong>Your part</strong>You send your logo, photos and key words.</span></li>
            <li><span class="ts-n">5</span><span><strong>Live in about 30 days</strong>Only once you’ve seen it and said yes.</span></li>
          </ol>
''' + go_cards([('index.html', 'arrow-left', 'Back to the homepage', 'Where you started'), ('work.html', 'layout', 'See the work', 'Sites I’ve built')]
               + ([(esc(GOOGLE_PROFILE_URL), 'star', 'See us on Google', 'Our Business Profile')] if GOOGLE_PROFILE_URL else []), 'Where to next'),
    '', WOLF)

page('thanks.html', 'Thanks | Stray Wolf Technology', 'Your answers are in.', thanks_main)


lost_main = end_page('That page isn’t here.', 'The link may be old, or the address may have a typo. One of these should get you where you were going.',
                     go_cards([('index.html', 'compass', 'Home', 'Start from the top'), ('work.html', 'layout', 'Work', 'Sites I’ve built'),
                               ('about.html', 'person', 'About', 'Different, on purpose'), ('start.html', 'send', 'Start a project', 'About two minutes')], 'Pages on this site'),
                     '', '<p class="end-404">404</p><img src="images/brand/stray-wolf-facets.svg" width="200" height="200" alt="">')

page('404.html', 'Page not found | Stray Wolf Technology', 'That page could not be found.', lost_main, body_class='inner lost')


# ---------------------------------------------------------------- Pricing
# Nov 13 2026 (Jeremy): no numbers on the site, pricing is "Let's talk". Each row says what the job is; the price
# column gives its size or promise instead of a dollar figure, and the "Don't see your job here?" row ends with Let's talk.

RATES = [
    ('A starter site', ('Pages', 'Up to 5'), 'Up to five pages, written with you and built around your business. Domain and email set up.', 'What most owner-run businesses need.'),
    ('A larger site', ('Pages', '6 or more'), 'More pages, or a site that does more: booking, a price list you change yourself, a small shop.', 'More to show, or more to sell.'),
    ('A mockup first', ('Credited', 'In full'), 'Your homepage, designed first so you can see it.', '<strong>Credited in full.</strong> Go ahead with the site and every dollar of the mockup comes off your final price.'),
    ('A fix, a page or a refresh', ('Turnaround', 'Days'), 'A fix, a new page, or new words and photos across the pages you have. Days, not weeks.', 'For a website you already have.'),
]
INCLUDED = [
    ('words', 'Help with the words', 'Clear pages people actually read.'),
    ('phone', 'Made for phones', 'Built for small screens first.'),
    ('globe', 'Domain and email set up', 'In your name. The registrar’s yearly fee is about $15.'),
    ('search', 'Set up for search engines', 'Google, Bing, DuckDuckGo and more. No ranking promises.'),
    ('key', 'Yours to keep', 'Domain, content and site, once it’s paid for.'),
    ('calendar', 'Thirty days of fixes', 'Anything not right in the first month, fixed free.'),
]
EXTRA = [
    ('Photography', 'Shoot it on your phone with my notes, or I’ll point you to a photographer.'),
    ('A shop or online payments', 'Stripe, Square or similar, quoted once I know what you sell.'),
    ('Writing everything from scratch', 'Rather not write a word? I’ll quote for all of it.'),
    ('A rush', 'Live in under 30 days? Ask. Sometimes the answer is yes.'),
]

def ruled(items, tag='ul'):
    return f'<{tag} class="ruled" role="list">' + ''.join(f'<li data-reveal><h3>{h}</h3><p>{t}</p></li>' for h, t in items) + f'</{tag}>'


def two_col(hid, h2, lead, body, cls=''):
    return f'''    <section class="section{cls}" aria-labelledby="{hid}">
      <div class="wrap two-col">
        <div class="two-col-side"><h2 id="{hid}" class="h2" data-reveal>{h2}</h2>{f'<p class="lead" data-reveal>{lead}</p>' if lead else ''}</div>
        {body}
      </div>
    </section>'''


rates_html = ''.join(f'''
          <li class="rate" data-reveal>
            <h3 class="rate-name">{n}</h3>
            <p class="rate-price"><small>{label}</small>{size}</p>
            <div class="rate-text"><p>{t}</p><p class="rate-who">{who}</p></div>
          </li>''' for n, (label, size), t, who in RATES)

pricing_main = page_head('What a website <em>costs.</em>', 'One price for the whole site, in writing, before any work starts. Every job is priced on its own, so let’s talk.',
                         ['A price in writing first', 'A mockup first, credited in full', 'No monthly fees, ever']) + f'''
    <section class="section tex tex-left" aria-labelledby="rates-h">
      <div class="wrap">
        <header class="sec-head">
          <h2 id="rates-h" class="h2" data-reveal>The jobs I take on.</h2>
          <p class="lead" data-reveal>Every site is priced on its own. Tell me what you need and you’ll have a price in writing within five days.</p>
        </header>
        <ul class="rates" role="list">{rates_html}
          <li class="rate rate-fit" data-reveal>
            <h3 class="rate-name">Don’t see your job here?</h3>
            <p class="rate-price"><small>Any size</small>Let’s talk</p>
            <div class="rate-text"><p>Most projects don’t fit in a box. Tell me what you need, big or small, and I’ll work out a version that fits you and your budget.</p><p><a class="link-arrow" href="start.html"><span>Talk it through with me</span>{ARROW}</a></p></div>
          </li>
          <li class="rate rate-after" data-reveal>
            <h3 class="rate-name">After launch</h3>
            <p class="rate-price"><small>Monthly</small>$0</p>
            <div class="rate-text"><p>No monthly fee, no contract. The hosting I set up costs nothing a month.</p><p><strong>Thirty days to make it right.</strong> Anything that isn’t right in the first 30 days, I fix at no charge. After that, changes are quoted per job.</p></div>
          </li>
        </ul>
      </div>
    </section>
    <section class="section on-stone tex tex-b" aria-labelledby="incl-h">
      <div class="wrap">
        <header class="sec-head">
          <h2 id="incl-h" class="h2" data-reveal>In every price.</h2>
          <p class="lead" data-reveal>Whatever the size of the site, these come with it.</p>
        </header>
        {pledge_list(INCLUDED)}
      </div>
    </section>
''' + two_col('extra-h', 'What costs extra.', 'Quoted on their own, and always before, never after.', ruled(EXTRA), ' tex tex-left') + '\n' \
  + f'''
{close_section('pricing-close-h', 'Want a number for yours?')}'''

page('pricing.html', 'Pricing: what a website costs | Stray Wolf Technology',
     'What a custom website costs: every site priced on its own, one price in writing before anything starts, no monthly fees.',
     pricing_main, current='pricing.html')


# ---------------------------------------------------------------- Reviews (real quotes from REVIEWS in tools/build.py; "coming soon" while it is empty)

sites_rows = ''.join(f'''<li data-reveal><h3>{s["name"]}</h3><p>{s["about"]}</p>{visit(s, 'link-arrow ruled-go').replace('Visit the site', '<span>Visit the site</span>')}</li>''' for s in SITES)

# The Google band: the "Review us on Google" button for past clients, and the profile link. Shows only once the
# GOOGLE_REVIEW_URL / GOOGLE_PROFILE_URL settings in tools/build.py are filled in (after the profile is verified).
google_band = ''
if GOOGLE_REVIEW_URL or GOOGLE_PROFILE_URL:
    google_band = f'''
    <section class="section g-band" aria-labelledby="g-band-h">
      <div class="wrap g-band-grid">
        <div class="g-band-text" data-reveal>
          <h2 id="g-band-h" class="h3">Worked with Stray Wolf?</h2>
          <p>A few honest words on Google help the next owner decide. It takes about a minute, and every review is read.</p>
        </div>
        <div class="g-band-act" data-reveal>{google_review_badge('About a minute')}{google_profile_link()}</div>
      </div>
    </section>'''

if REVIEWS:
    quotes = ''.join(f'''
          <li class="quote" data-reveal>
            <blockquote class="quote-text"><p>{esc(q)}</p></blockquote>
            <p class="quote-by"><strong>{esc(who)}</strong><span>{esc(biz)}</span>{f'<a class="link" href="{url}" rel="noopener">Visit the site</a>' if url else ''}</p>
          </li>''' for q, who, biz, url in REVIEWS)
    reviews_main = page_head('What clients <em>say.</em>', 'In their own words, with their OK to quote them by name.') + f'''
    <section class="section" aria-labelledby="quotes-h">
      <div class="wrap">
        <h2 id="quotes-h" class="visually-hidden">Reviews</h2>
        <ul class="quotes" role="list">{quotes}
        </ul>
      </div>
    </section>{google_band}
{close_section('reviews-close-h', 'Ready to start yours?')}'''
    reviews_desc = 'What clients say about working with Stray Wolf Technology, in their own words.'
else:
    reviews_main = page_head('What clients <em>say.</em>', 'This page is waiting on real words. The first sites launched recently, and I’d rather show what people actually said than fill the space.') + \
      two_col('soon-h', 'Coming soon.', 'Real words from real clients, as they come in. Until then, the work speaks for itself.',
              f'<ul class="ruled ruled-sites" role="list">{sites_rows}</ul>', ' tex tex-left') + google_band + f'''
{close_section('reviews-close-h', 'Ready to start yours?')}'''
    reviews_desc = 'What clients say about working with Stray Wolf Technology. Coming soon, as the first sites settle in.'

page('reviews.html', 'Client reviews | Stray Wolf Technology', reviews_desc, reviews_main, current='reviews.html')


# ---------------------------------------------------------------- Privacy and Terms (legal pass, Nov 9 2026)
# Conservative on purpose: plain first-person copy, but every protective point a Texas web business should cover.
# A template, not legal advice. Update LEGAL_UPDATED whenever either page changes in substance.

LEGAL_UPDATED = 'November 10, 2026'
mail_me = (f'email {CONTACT["email"]}' if CONTACT['email'] else 'reply to any email from me')
Mail_me = mail_me[0].upper() + mail_me[1:]


def legal_page(sections, summary, label):
    """Summary cards, a sticky contents list and the full text: the layout Privacy and Terms share."""
    return f'''
    <section class="section section-tight" aria-label="{label}">
      <div class="wrap">
        <ul class="pv-cards" role="list">{''.join(f'<li data-reveal><span class="plate-ic" aria-hidden="true">{icon(ic)}</span><h2 class="pv-h">{h}</h2><p>{t}</p></li>' for ic, h, t in summary)}</ul>
        <div class="pv-grid">
          <nav class="toc" aria-label="On this page">
            <p class="toc-h">On this page</p>
            <ol role="list">{''.join(f'<li><a href="#{sid}">{h}</a></li>' for sid, h, _ in sections)}</ol>
          </nav>
          <div class="prose">
''' + '\n'.join(f'            <section id="{sid}"><h2>{h}</h2>{t}</section>' for sid, h, t in sections) + '''
          </div>
        </div>
      </div>
    </section>'''


# ---- Privacy

PRIVACY = [
    ('who', 'Who I am', f'<p>This site belongs to Stray Wolf Technology, a web design business based in Texas. On this page, “I” and “me” mean Stray Wolf Technology. Questions about your privacy? {Mail_me}.</p>'),
    ('collects', 'What this site collects', '<p>First, what you choose to send. On the Start a project page, that’s your name, business name and email, plus anything else you add, like a phone number, a link or a note. If you email me, I get what’s in your email.</p><p>This site uses Google Analytics to count visits and see which pages people find useful. It sets a few cookies (their names start with _ga) and records things like the pages you view, the links you click, roughly where you are (city or region), your device and browser, and how you found the site. It never sees what you type into the form. I use it only to improve this site, never for ads.</p><p>Don’t want to be counted? Block cookies for this site in your browser, use a content blocker, or install Google’s <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">opt-out add-on<span class="visually-hidden"> (opens in a new tab)</span></a>. The site works the same either way.</p>'),
    ('used', 'How I use it', '<p>To reply to you, understand your project and send you a price. If you become a client, also to run the project, send invoices and keep the records the law asks a business to keep.</p><p>I don’t sell your details. I don’t share them for anyone’s marketing, and I won’t add you to a mailing list.</p>'),
    ('shared', 'Who else handles it', '<p>A few services keep this site and my email running. Each one only gets what it needs to do its job:</p><ul><li><strong>Web3Forms</strong> delivers the form to my inbox.</li><li><strong>Cloudflare</strong> runs the domain.</li><li><strong>Google Workspace</strong> handles my email.</li><li><strong>Google Analytics</strong> counts visits to this site, as described above.</li><li><strong>GitHub</strong> hosts the site. Like most hosts, it keeps short technical logs, such as IP addresses, to keep the service secure.</li></ul><p>Each of these companies has its own privacy policy. If a team member or contractor helps on your project, they see only what the project needs and must keep it private. I’ll also share information if the law requires it, or to protect my rights or someone’s safety.</p>'),
    ('kept', 'How long I keep it', '<p>If your project doesn’t go ahead, I delete your form answers within 12 months. If you become a client, I keep project emails and invoices as long as tax and business records require, usually up to seven years. Anything I don’t need to keep, I’ll delete when you ask.</p>'),
    ('safe', 'Keeping it safe', '<p>My accounts use strong passwords and two-step login, and this whole site runs over a secure connection (HTTPS). Even so, no website, form or email is ever completely secure, and I can’t promise it will be.</p><p class="pv-warn"><strong>Please don’t send passwords, card or bank numbers, Social Security numbers or health information through the form or by email.</strong> If your project needs a login, I’ll set up a safer way to share it.</p>'),
    ('choices', 'Your choices', f'<p>You can ask to see what I have about you, correct it or delete it. {Mail_me}. I’ll answer within 30 days, and asking won’t change how I treat you.</p>'),
    ('kids', 'Children', '<p>This site is for business owners. It isn’t meant for anyone under 18, and I don’t knowingly collect anything from children under 13. If you think a child has sent me something, tell me and I’ll delete it.</p>'),
    ('links', 'Other websites', '<p>The Work page links to sites I’ve built for clients, and some pages link to other services. Those sites belong to someone else and have their own privacy policies. This page covers straywolftech.com only. It doesn’t cover the sites I build for clients; each client is responsible for their own site’s privacy policy.</p>'),
    ('changes', 'Changes', f'<p>If this page changes, the date below changes too. Last updated {LEGAL_UPDATED}.</p>'),
]
PRIVACY_SUMMARY = [('cookie', 'No ads, nothing sold', 'Google Analytics counts visits. That’s all it’s used for.'),
                   ('lock', 'Your answers stay private', 'Used to reply and plan your project. Never sold.'),
                   ('trash', 'Deleted when you ask', 'Ask once and anything I don’t have to keep is gone.')]

privacy_main = page_head('Privacy, in <em>plain English.</em>', 'The short version: this site counts visits with Google Analytics. Beyond that, it only collects what you send, and only uses it to reply to you and plan your project.', cls=' page-head-privacy') \
    + legal_page(PRIVACY, PRIVACY_SUMMARY, 'Privacy details')

page('privacy.html', 'Privacy policy | Stray Wolf Technology', 'What this website collects, who handles it, how long it’s kept and how to have it deleted. No ads, and nothing sold.', privacy_main)


# ---- Terms

TERMS = [
    ('using', 'Using this site', '<p>By using straywolftech.com, you agree to these terms and to the <a href="privacy.html">privacy policy</a>. If you don’t agree, please don’t use the site. On this page, “I” and “me” mean Stray Wolf Technology and anyone who works with it.</p>'),
    ('offer', 'Nothing here is a contract', '<p>Prices, timelines and descriptions on this site are general information and starting points. They aren’t an offer or a promise. Every project gets its own written price and project agreement before any work starts. If anything on this site differs from a signed agreement, the agreement wins.</p>'),
    ('payments', 'Payments and refunds', f'<p>Every project has its own signed agreement, and that agreement decides. This is how payments work:</p><ul><li><strong>Deposit.</strong> Half the price is due when you sign. It holds your spot and is not refundable once work has started. Cancel before any work starts and I refund it.</li><li><strong>The rest.</strong> The other half is due before the site goes live or is handed over. Smaller jobs may be paid in full up front.</li><li><strong>Mockups.</strong> A mockup is paid up front and isn’t refundable. If the full site goes ahead within 60 days, the whole mockup fee comes off the price.</li><li><strong>Invoices.</strong> Due within 14 days. If a payment is late, I may pause the work until it’s paid.</li><li><strong>Ending early.</strong> If a project stops part way, you pay for the work done up to that point. If I end it for my own reasons, I refund anything not yet earned.</li><li><strong>Ownership.</strong> The site becomes yours once it’s paid in full.</li><li><strong>After launch.</strong> Anything in my work that isn’t right in the first 30 days, I fix at no charge. There are no monthly fees. Later changes are priced before I start.</li><li><strong>Other companies.</strong> Your domain, hosting and email are paid to those companies directly and follow their own refund rules.</li></ul><p>Questions about an invoice? {Mail_me}.</p>'),
    ('send', 'What you send me', '<p>Sending the form or an email doesn’t make you a client or commit either of us to anything. I may say no to any project, for any reason.</p><p>Please only send information that’s accurate and that you have the right to share. Don’t send passwords, payment details or anything confidential. You keep owning anything you send. You let me use it to reply to you and price your project.</p>'),
    ('own', 'Who owns this site', '<p>The design, words, code, logo and wolf on this site belong to Stray Wolf Technology. You’re welcome to look around and share links. Please don’t copy the site, its words or its logo.</p><p>The client sites on the Work page belong to their owners and are shown with their permission. Their names and logos are theirs.</p>'),
    ('accuracy', 'Accuracy and changes', '<p>I work to keep this site accurate and running. I can’t promise it’s always complete, current, error-free or available. I may change or remove anything on it at any time.</p>'),
    ('links', 'Links to other sites', '<p>Links to client sites and other services are there for convenience. I don’t control those sites and I’m not responsible for their content, privacy or security.</p>'),
    ('warranty', 'No warranties', '<p><strong>THIS SITE IS PROVIDED “AS IS” AND “AS AVAILABLE,” WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, TO THE FULLEST EXTENT THE LAW ALLOWS.</strong></p>'),
    ('liability', 'Limits on liability', '<p><strong>TO THE FULLEST EXTENT THE LAW ALLOWS, STRAY WOLF TECHNOLOGY, ITS OWNER, TEAM MEMBERS AND CONTRACTORS ARE NOT LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL OR CONSEQUENTIAL DAMAGES, OR FOR ANY LOSS OF DATA, PROFITS OR BUSINESS, ARISING FROM YOUR USE OF THIS SITE OR ANY SITE IT LINKS TO.</strong></p><p>If you misuse this site or break these terms, you agree to cover any claim against me that results.</p>'),
    ('law', 'Texas law', '<p>These terms are governed by the laws of Texas. Any dispute about this site will be handled in the state courts of Texas. If a court finds part of these terms unenforceable, the rest still applies.</p>'),
    ('changes', 'Changes', f'<p>If these terms change, the date below changes too. Using the site after a change means you accept it. Last updated {LEGAL_UPDATED}.</p>'),
    ('questions', 'Questions', f'<p>{Mail_me}. I’m happy to explain anything on this page.</p>'),
]
TERMS_SUMMARY = [('doc', 'No deal until it’s signed', 'Prices here are starting points. Every project gets a written price and agreement first.'),
                 ('shield', 'Send only what’s yours', 'Accurate details you have the right to share. Never passwords or payment details.'),
                 ('layout', 'The work shown is theirs', 'Client sites belong to their owners and appear with their OK.')]

terms_main = page_head('Terms, in <em>plain English.</em>', 'The rules for using this site, and how payments and refunds work. Nothing on this site is a contract until you and I both sign one.', cls=' page-head-privacy') \
    + legal_page(TERMS, TERMS_SUMMARY, 'Terms of use')

page('terms.html', 'Terms of use | Stray Wolf Technology', 'The terms for using straywolftech.com and for paying for a project: deposits, refunds, ownership, and the limits on liability.', terms_main)
