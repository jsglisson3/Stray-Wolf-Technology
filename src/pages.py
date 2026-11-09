"""Content for the inner pages. tools/build.py runs this file and provides:
   page(file, title, desc, main, current=None, body_class='inner', banner=True)   writes docs/<file>
   form                      the intake questions (src/partials/intake-form.html, with the settings filled in)
   SITES, work_list(sites)   the Work showcase (src/sites.py)
   services()                the "What I do" tiles
   close_section(hid, line)  the closing card with the business-name box
   numbers_html()            the four numbers (1 person, 14 questions, 5 days, about 30 days)
   icon(name), ARROW         an icon from src/partials/sprite.html
   photo_or_mark(dark), HEADSHOT, STORY
   read(name)                a partial from src/partials
   CONTACT, WAYS             the email, phone and booking links, or '' while not set
Voice: first person, plain and short. Jeremy by first name only. Nothing unconfirmed goes on a page."""


def page_head(h1, lead, notes=None, cls=''):
    """The top of an inner page: a big title, one line beside it, and a few plain notes under a rule."""
    side = f'<p class="lead">{lead}</p>' + (notes_list(notes) if notes else '')
    return f'''    <section class="page-head{cls}">
      <div class="wrap page-head-grid">
        <h1 class="h1">{h1}</h1>
        <div class="page-head-side">{side}</div>
      </div>
    </section>'''


def notes_list(items):
    return '<ul class="page-notes" role="list">' + ''.join(f'<li>{t}</li>' for t in items) + '</ul>'


# ---------------------------------------------------------------- Work

work_main = page_head('Sites I’ve designed and built <em>by hand.</em>', 'Each one made for one business, from a blank page. Tap any of them to see it live.',
                      [f'{len(SITES)} sites so far', 'Built by hand, no templates', 'Made for phones too']) + f'''
    <section class="section work-section" aria-label="Websites">
      <div class="wrap">
{work_list(SITES)}
      </div>
    </section>
{close_section('work-close-h', 'Want yours on this list?')}'''

page('work.html', 'Work | Stray Wolf Technology',
     'Websites Stray Wolf Technology has designed and built by hand for owner-run businesses. Tap any one to see it live.',
     work_main, current='work.html')


# ---------------------------------------------------------------- About
# One person, start to finish: a profile card, six pledges, and the story behind the name. No case studies, no personal background.


PLEDGES = [('craft', 'Hand-built', 'Designed and written for your business. No templates, no page builders.'),
           ('chat', 'You first, then the design', 'I get to know you and what you want from a website before I design anything. Everything in plain English.'),
           ('doc', 'A price in writing', 'Before anything starts. No tiers and no surprise add-ons.'),
           ('eye', 'Nothing goes live without you', 'You see the site before anyone else, and it launches when you say yes.'),
           ('key', 'Yours to keep', 'Your domain, your content and your site belong to you.'),
           ('person', 'One person to call', 'Me, before and after launch. No account manager in between.')]

profile_card = f'''<figure class="profile{' has-photo' if HEADSHOT else ''}" data-reveal>
          <div class="profile-pic">{photo_or_mark(dark=False)}</div>
          <figcaption class="profile-body">
            <p class="profile-name">Jeremy<span>Designer and developer</span></p>
            <p class="profile-status"><span class="dot" aria-hidden="true"></span>Taking a few projects at a time</p>
          </figcaption>
        </figure>'''

about_main = f'''    <section class="about-hero" aria-labelledby="about-h">
      <div class="wrap about-hero-grid">
        <div class="about-text">
          <h1 id="about-h" class="h1">One person, <em>start to finish.</em></h1>
          <p class="lead about-lead">Hi, I’m Jeremy. I design and build websites on my own, for owner-run businesses. No account manager and no hand-offs: the person you talk to is the person doing the work.</p>
          <p class="about-more" data-reveal>I’m not trying to make as much money as I can. I want to do quality work. So I take a few clients at a time, only the jobs I know I can do well, and I’ll turn down one I don’t think I can do right.</p>
          <div class="button-row"><a class="button button-lg" href="start.html">Start a project{ARROW}</a><a class="button button-quiet button-lg" href="work.html">See the work</a></div>
        </div>
        {profile_card}
      </div>
    </section>

    <section class="section" aria-labelledby="how-h">
      <div class="wrap">
        <header class="sec-head">
          <h2 id="how-h" class="h2" data-reveal>Six things you can count on.</h2>
          <div class="sec-aside" data-reveal>
            <p class="lead">The same promises on every project, written down so you can hold me to them.</p>
          </div>
        </header>
        <ul class="pledges" role="list">{''.join(f"""
          <li class="pledge" data-reveal><h3>{h}</h3><p>{t}</p></li>""" for _, h, t in PLEDGES)}
        </ul>
      </div>
    </section>

    <section class="section story" aria-labelledby="story-h">
      <div class="wrap story-grid">
        <div class="story-art" aria-hidden="true">
          <img src="images/brand/stray-wolf-symbol-color.svg" width="200" height="200" alt="" loading="lazy" decoding="async">
        </div>
        <div class="story-text">
          <h2 id="story-h" class="h2" data-reveal>No pack. <em>One person.</em></h2>
          <p class="lead" data-reveal>A stray wolf doesn’t run with a pack. That’s how I work. I don’t start from a template, and I don’t farm the work out. Every site I put my name on, I designed and built myself.</p>
        </div>
      </div>
    </section>

{close_section('about-close-h')}'''

page('about.html', 'About | Stray Wolf Technology',
     'Stray Wolf Technology is Jeremy: one designer building hand-built websites for owner-run businesses, start to finish.',
     about_main, current='about.html')


# ---------------------------------------------------------------- Start a project (the intake)

if WAYS:
    talk = '<div class="aside-block"><h2 class="aside-h">Rather talk first?</h2>\n            <ul class="reach-list" role="list">' + ''.join(f'<li>{x}</li>' for x in WAYS) + '</ul></div>'
else:
    talk = '<div class="aside-block aside-tip"><p><strong>Just have a question?</strong> Put it in the last box. You don’t need every answer to send the form.</p></div>'

start_main = page_head('Tell me about <em>your business.</em>', 'Six quick questions, about two minutes. I read every answer, and you’ll hear from me within five days. The rest we work out on a call.',
                       ['About 2 minutes', 'Most answers are optional', 'A reply within 5 days'], cls=' page-head-start') + f'''
    <section class="section section-tight start-section" aria-label="The questions">
      <div class="wrap start-grid">
        <h2 id="start-h" class="visually-hidden">The questions</h2>
        {form}
        <div class="start-aside">
          <div class="aside-block">
            <h2 class="aside-h">What happens next</h2>
            <ol class="next-steps" role="list">
              <li><strong>Within 5 days</strong>I read your answers and reply. If it’s not something I can do well, I’ll say so.</li>
              <li><strong>Before anything starts</strong>You get a price in writing.</li>
              <li><strong>Your 10%</strong>You send the words, photos and logo.</li>
              <li><strong>About 30 days</strong>Your site goes live.</li>
            </ol>
          </div>
          {talk}
        </div>
      </div>
    </section>'''

page('start.html', 'Start a project | Stray Wolf Technology',
     'Six quick questions about your business and your website, about two minutes. Answer them and Jeremy replies within five days.',
     start_main, current='start.html', body_class='inner page-start')


# ---------------------------------------------------------------- Thanks and 404

def go_cards(links, label):
    return f'''          <nav aria-label="{label}"><ul class="go-cards" role="list">''' + ''.join(
        f'<li><a href="{href}"><span class="go-t"><strong>{text}</strong><small>{sub}</small></span>{ARROW}</a></li>' for href, ic, text, sub in links) + '</ul></nav>'


def end_page(h1, lead, inner, badge, side):
    return f'''    <section class="end-page" aria-labelledby="end-h">
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
            <li><span class="ts-n">4</span><span><strong>Your 10%</strong>You send the words, photos and logo.</span></li>
            <li><span class="ts-n">5</span><span><strong>Live in about 30 days</strong>Only once you’ve seen it and said yes.</span></li>
          </ol>
''' + go_cards([('index.html', 'arrow-left', 'Back to the homepage', 'Where you started'), ('work.html', 'layout', 'See the work', 'Sites I’ve built')], 'Where to next'),
    '', WOLF)

page('thanks.html', 'Thanks | Stray Wolf Technology', 'Your answers are in.', thanks_main)


lost_main = end_page('That page isn’t here.', 'The link may be old, or the address may have a typo. One of these should get you where you were going.',
                     go_cards([('index.html', 'compass', 'Home', 'Start from the top'), ('work.html', 'layout', 'Work', 'Sites I’ve built'),
                               ('about.html', 'person', 'About', 'One person, start to finish'), ('start.html', 'send', 'Start a project', 'About two minutes')], 'Pages on this site'),
                     '', '<p class="end-404">404</p>' + WOLF)

page('404.html', 'Page not found | Stray Wolf Technology', 'That page could not be found.', lost_main)


# ---------------------------------------------------------------- Pricing (FIRST DRAFT, Nov 9 2026)
# The numbers are settings at the top of tools/build.py (STARTER_FROM, LARGER_FROM, FIX_FROM). Every line here is
# Jeremy's to confirm or change before launch.

RATES = [
    ('A starter site', STARTER_FROM, 'Up to five pages: home, about, what you do, your work, contact. Written with you, designed and built by hand, made for phones. Domain and business email set up.', 'What most owner-run businesses need.'),
    ('A larger site', LARGER_FROM, 'More pages, or a site that does more: online booking, a menu or price list you change yourself, a gallery that grows, a small shop.', 'For a business with more to show, or more to sell.'),
    ('A fix, a page or a refresh', FIX_FROM, f'Something broken, fixed, from ${FIX_FROM}. One new page added to your site, from ${PAGE_FROM}. New photos and words across the pages you have, from ${REFRESH_FROM}. Days, not weeks.', 'For a website you already have.'),
]
INCLUDED = [
    ('Help with the words', 'You know your business. I help turn that into clear pages people actually read.'),
    ('Made for phones', 'Most visitors will be on one. Every page is built for small screens first.'),
    ('Domain and email set up', 'Your web address registered in your name, with a matching business email. The yearly domain fee goes to the registrar, about $15.'),
    ('Set up so Google can read it', 'Page titles, descriptions and a fast site. The basics done right, with no promises about rankings.'),
    ('Yours to keep', 'Your domain, your content and your site belong to you. Every account is in your name.'),
    ('Thirty days of fixes', 'Anything that isn’t right in the first month after launch, I fix at no charge.'),
]
EXTRA = [
    ('Photography', 'Good photos make the site. I’ll tell you what to shoot on your phone, or point you to a photographer near you.'),
    ('A shop or online payments', 'Setting up Stripe, Square or similar is quoted on its own, once I know what you sell.'),
    ('Writing everything from scratch', 'If you’d rather not write a word, I’ll quote for writing it all.'),
    ('A rush', 'Need it live in less than 30 days? Ask. Sometimes the answer is yes.'),
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
            <p class="rate-price"><small>From</small>${price}</p>
            <div class="rate-text"><p>{t}</p><p class="rate-who">{who}</p></div>
          </li>''' for n, price, t, who in RATES)

pricing_main = page_head('What a website <em>costs.</em>', 'One price for the whole site, in writing, before any work starts. Here’s where most projects land.',
                         ['A price in writing first', 'Half to start, half at launch', 'No monthly fees, ever']) + f'''
    <section class="section" aria-labelledby="rates-h">
      <div class="wrap">
        <header class="sec-head">
          <h2 id="rates-h" class="h2" data-reveal>What projects usually cost.</h2>
          <p class="lead" data-reveal>Every site is priced on its own. These are the starting points, so you know before we talk.</p>
        </header>
        <ul class="rates" role="list">{rates_html}
          <li class="rate" data-reveal>
            <h3 class="rate-name">After launch</h3>
            <p class="rate-price"><small>Monthly</small>$0</p>
            <div class="rate-text"><p>No monthly fee, no contract. The site is yours, the hosting I set up costs nothing a month, and any change later is quoted on its own.</p></div>
          </li>
        </ul>
      </div>
    </section>
    <section class="section on-stone" aria-labelledby="incl-h">
      <div class="wrap">
        <header class="sec-head">
          <h2 id="incl-h" class="h2" data-reveal>In every price.</h2>
          <p class="lead" data-reveal>Whatever the size of the site, these come with it.</p>
        </header>
        <ul class="pledges" role="list">{''.join(f'<li class="pledge" data-reveal><h3>{h}</h3><p>{t}</p></li>' for h, t in INCLUDED)}</ul>
      </div>
    </section>
''' + two_col('extra-h', 'What costs extra.', 'Quoted on their own, and always before, never after.', ruled(EXTRA)) + '\n' \
  + f'''
{close_section('pricing-close-h', 'Want a number for yours?')}'''

page('pricing.html', 'Pricing | Stray Wolf Technology',
     f'What a hand-built website costs: starter sites from ${STARTER_FROM}, larger sites from ${LARGER_FROM}, one price in writing before anything starts.',
     pricing_main, current='pricing.html')


# ---------------------------------------------------------------- Reviews (real quotes from REVIEWS in tools/build.py; "coming soon" while it is empty)

sites_rows = ''.join(f'''<li data-reveal><h3>{s["name"]}</h3><p>{s["about"]}</p>{visit(s, 'link-arrow ruled-go').replace('Visit the site', '<span>Visit the site</span>')}</li>''' for s in SITES)

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
    </section>
{close_section('reviews-close-h', 'Ready to start yours?')}'''
    reviews_desc = 'What clients say about working with Stray Wolf Technology, in their own words.'
else:
    reviews_main = page_head('What clients <em>say.</em>', 'This page is waiting on real words. The first sites launched recently, and I’d rather show what people actually said than fill the space.') + \
      two_col('soon-h', 'Coming soon.', 'Real words from real clients, as they come in. Until then, the work speaks for itself.',
              f'<ul class="ruled ruled-sites" role="list">{sites_rows}</ul>') + f'''
{close_section('reviews-close-h', 'Ready to start yours?')}'''
    reviews_desc = 'What clients say about working with Stray Wolf Technology. Coming soon, as the first sites settle in.'

page('reviews.html', 'Reviews | Stray Wolf Technology', reviews_desc, reviews_main, current='reviews.html')


# ---------------------------------------------------------------- Privacy

delete_how = (f'Email {CONTACT["email"]} and ask' if CONTACT['email'] else 'Reply to any email from Jeremy and ask')
sections = [
    ('collects', 'What this site collects', '<p>Only what you send. When you answer the questions on the Start a project page, that’s your name, your business name, your email and anything else you choose to add, like a phone number, a link or a note.</p>'),
    ('used', 'How it’s used', '<p>To reply to you and plan your project. That’s it. Your details aren’t sold or shared for marketing, and you won’t be added to a mailing list.</p>'),
    ('kept', 'Where it’s kept', '<p>The form is delivered by Web3Forms, a form service, which passes your answers on to Jeremy’s email. What Web3Forms itself keeps is covered by the privacy policy on <a href="https://web3forms.com/">web3forms.com</a>. If the form opens your email app instead, your answers go straight from your email to Jeremy.</p>'),
    ('hosting', 'Hosting', '<p>The site is hosted on GitHub Pages. Like most web hosts, GitHub keeps basic technical logs, such as IP addresses, to keep the service secure. This site uses no cookies, ads or tracking.</p>'),
    ('delete', 'Deleting your details', f'<p>{delete_how}. Anything Stray Wolf Technology has from you will be deleted.</p>'),
    ('changes', 'Changes', '<p>If this page changes, the date below changes too. Last updated November 9, 2026.</p>'),
]
SUMMARY = [('cookie', 'No cookies, ads or tracking', 'Nothing follows you around after you leave.'),
           ('send', 'Only what you send', 'The form answers, used to reply and plan your project.'),
           ('trash', 'Deleted when you ask', 'Ask once and anything I have from you is gone.')]

privacy_main = page_head('Privacy, in <em>plain English.</em>', 'The short version: this site only collects what you send, and only uses it to reply to you and plan your project.', cls=' page-head-privacy') + f'''
    <section class="section section-tight" aria-label="Privacy details">
      <div class="wrap">
        <ul class="pv-cards" role="list">{''.join(f'<li data-reveal><h2 class="pv-h">{h}</h2><p>{t}</p></li>' for i, h, t in SUMMARY)}</ul>
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

page('privacy.html', 'Privacy | Stray Wolf Technology', 'What this website collects, how it’s used and how to have your details deleted. No cookies, ads or tracking.', privacy_main)
