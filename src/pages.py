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


def page_head(eyebrow, h1, lead, extra='', cls=''):
    """The top of an inner page: a label, a big title, one line, and (optionally) something beside it."""
    return f'''    <section class="page-head{cls}">
      <div class="wrap page-head-grid">
        <div class="page-head-text">
          <p class="eyebrow eyebrow-plain">{eyebrow}</p>
          <h1 class="h1">{h1}</h1>
          <p class="lead">{lead}</p>
        </div>
        {extra}
      </div>
    </section>'''


def chips(items):
    return '<ul class="meta-chips" role="list">' + ''.join(f'<li>{icon(i)}<span>{t}</span></li>' for i, t in items) + '</ul>'


# ---------------------------------------------------------------- Work

work_main = page_head('Work', 'Sites I’ve designed and built by hand.', 'Each one made for one business, from a blank page. Tap any of them to see it live.',
                      chips([('layout', f'{len(SITES)} sites'), ('craft', 'Built by hand'), ('phone', 'Made for phones too')])) + f'''
    <section class="section section-tight" aria-label="Websites">
      <div class="wrap">
{work_list(SITES)}
      </div>
    </section>
{close_section('work-close-h', 'Want yours on this list?')}'''

page('work.html', 'Work | Stray Wolf Technology',
     'Websites Stray Wolf Technology has designed and built by hand for owner-run businesses. Tap any one to see it live.',
     work_main, current='work.html')


# ---------------------------------------------------------------- About
# One person, start to finish: a profile card, the numbers, six pledges that light up as you scroll,
# a three-question fit check, and the story behind the name. No case studies, no personal background.

FACTS = [('person', 'Works alone'), ('chat', 'By referral'), ('craft', 'Hand-built')]

PLEDGES = [('craft', 'Hand-built', 'Designed and written for your business. No templates, no page builders.'),
           ('chat', 'You first, then the design', 'I get to know you and what you want from a website before I design anything. Everything in plain English.'),
           ('doc', 'A price in writing', 'Before anything starts. No tiers and no surprise add-ons.'),
           ('eye', 'Nothing goes live without you', 'You see the site before anyone else, and it launches when you say yes.'),
           ('key', 'Yours to keep', 'Your domain, your content and your site belong to you.'),
           ('person', 'One person to call', 'Me, before and after launch. No account manager in between.')]

FIT_QS = [('own', 'Do you own and run the business yourself?'),
          ('one', 'Do you want one person handling the whole site, start to finish?'),
          ('ref', 'Were you referred by someone I’ve built a site for?')]

profile_card = f'''<div class="profile{' has-photo' if HEADSHOT else ''}" data-reveal>
          <div class="profile-pic">
            <div class="hero-grid-lines" aria-hidden="true"></div>
            {photo_or_mark(dark=False)}
          </div>
          <div class="profile-body">
            <p class="profile-name">Jeremy<span>Designer and developer</span></p>
            <p class="profile-status"><span class="dot" aria-hidden="true"></span>Taking a few projects at a time</p>
            <ul class="profile-facts" role="list">{''.join(f'<li>{icon(i)}<span>{t}</span></li>' for i, t in FACTS)}</ul>
          </div>
        </div>'''

fit_rows = ''.join(f'''
            <div class="fq" data-fq="{k}">
              <p class="fq-q" id="fq-{k}">{q}</p>
              <div class="fq-pick" role="group" aria-labelledby="fq-{k}">
                <button type="button" data-ans="yes" aria-pressed="false">Yes</button>
                <button type="button" data-ans="no" aria-pressed="false">No</button>
              </div>
            </div>''' for k, q in FIT_QS)

about_main = f'''    <section class="about-hero" aria-labelledby="about-h">
      <div class="wrap about-hero-grid">
        <div class="about-text">
          <p class="eyebrow eyebrow-plain">About</p>
          <h1 id="about-h" class="h1">One person, <em>start to finish.</em></h1>
          <p class="lead about-lead">Hi, I’m Jeremy. I design and build websites on my own, for owner-run businesses. No account manager and no hand-offs: the person you talk to is the person doing the work.</p>
          <div class="button-row"><a class="button button-lg" href="start.html">Start a project{ARROW}</a><a class="button button-quiet button-lg" href="work.html">See the work</a></div>
        </div>
        {profile_card}
      </div>
    </section>

    <section class="section" aria-labelledby="how-h">
      <div class="wrap how-grid">
        <div class="how-side">
          <p class="eyebrow" data-reveal>How I work</p>
          <h2 id="how-h" class="h2" data-reveal>Six things you can count on.</h2>
          <p class="lead" data-reveal>The same promises on every project, written down so you can hold me to them.</p>
          <p data-reveal><a class="link link-arrow" href="index.html#how">See the four steps{ARROW}</a></p>
        </div>
        <ol class="pledges" role="list">{''.join(f"""
          <li class="pledge" data-reveal>
            <span class="pledge-n" aria-hidden="true">{n:02d}</span>
            <span class="pledge-ic">{icon(i)}</span>
            <div><h3>{h}</h3><p>{t}</p></div>
          </li>""" for n, (i, h, t) in enumerate(PLEDGES, 1))}
        </ol>
      </div>
    </section>

    <section class="section on-stone" aria-labelledby="fit-h">
      <div class="wrap fit-grid">
        <div class="fit-side">
          <p class="eyebrow" data-reveal>Who it’s for</p>
          <h2 id="fit-h" class="h2" data-reveal>Is this a fit?</h2>
          <p class="lead" data-reveal>Three quick questions and a straight answer. Nothing is sent anywhere.</p>
          <p class="muted" data-reveal>I only take a few clients at a time, so every site gets my full attention. Owner-run shops, trades, practices and one-truck outfits are my usual work.</p>
        </div>
        <div class="fitcheck" data-fitcheck data-reveal>
          <div class="fq-list">{fit_rows}
          </div>
          <div class="fit-result" data-fit-result aria-live="polite">
            <p class="fit-result-h">Answer the three questions and I’ll tell you honestly.</p>
            <p class="fit-result-p">If it’s not a fit, I’ll say so up front.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section story" aria-labelledby="story-h">
      <div class="wrap story-grid">
        <div class="story-art" aria-hidden="true">
          <div class="hero-grid-lines"></div>
          <img src="images/brand/stray-wolf-symbol-color.svg" width="200" height="200" alt="" loading="lazy" decoding="async">
        </div>
        <div class="story-text">
          <p class="eyebrow" data-reveal>The name</p>
          <h2 id="story-h" class="h2" data-reveal>No pack. <em>One person.</em></h2>
          <p data-reveal>A stray wolf doesn’t run with a pack. That’s how I work. I don’t start from a template, and I don’t farm the work out. Every site I put my name on, I designed and built myself.</p>
        </div>
      </div>
    </section>

{close_section('about-close-h')}'''

page('about.html', 'About | Stray Wolf Technology',
     'Stray Wolf Technology is Jeremy: one designer building hand-built websites for owner-run businesses, start to finish.',
     about_main, current='about.html')


# ---------------------------------------------------------------- Start a project (the intake)

SECTIONS = [('qs-business', 'About your business'), ('qs-goal', 'The goal'), ('qs-have', 'What you already have'),
            ('qs-look', 'Look and feel'), ('qs-practical', 'The practical stuff'), ('qs-reach', 'How to reach you')]

if WAYS:
    talk = '<div class="aside-block"><h2 class="aside-h">Rather talk first?</h2>\n            <ul class="reach-list" role="list">' + ''.join(f'<li>{x}</li>' for x in WAYS) + '</ul></div>'
else:
    talk = '<div class="aside-block aside-tip">' + icon('chat') + '<p><strong>Just have a question?</strong> Put it in the last box. You don’t need every answer to send the form.</p></div>'

progress = f'''<nav class="progress-card" aria-label="Form sections" data-progress>
            <div class="progress-top">
              <p class="progress-h">Your answers</p>
              <p class="progress-count" aria-live="polite"><span data-progress-done>0</span> of <span data-progress-total>17</span></p>
            </div>
            <div class="progress-bar" aria-hidden="true"><span data-progress-bar></span></div>
            <ol class="progress-list" role="list">{''.join(f'<li><a href="#{sid}" data-progress-link="{sid}"><span class="pl-n" aria-hidden="true">{n}</span><span>{name}</span><span class="pl-check" aria-hidden="true">{icon("check")}</span></a></li>' for n, (sid, name) in enumerate(SECTIONS, 1))}</ol>
          </nav>'''

start_main = page_head('Start a project', 'Tell me about your business.', 'Fourteen questions, about five minutes. I read every answer before I start, and you’ll hear from me within five days.',
                       chips([('clock', 'About 5 minutes'), ('list', 'Only 4 are required'), ('mail', 'A reply within 5 days')]), cls=' page-head-start') + f'''
    <section class="section section-tight start-section" aria-label="The questions">
      <div class="wrap start-grid">
        <h2 id="start-h" class="visually-hidden">The questions</h2>
        <div class="mini-progress" aria-hidden="true"><span class="mini-label" data-mini-label>About your business</span><span class="mini-count"><span data-progress-done>0</span>/<span data-progress-total>17</span></span><span class="mini-bar"><span data-progress-bar></span></span></div>
        {form}
        <div class="start-aside">
          {progress}
          <div class="aside-block">
            <h2 class="aside-h">What happens next</h2>
            <ol class="next-steps" role="list">
              <li><span class="ns-ic">{icon('mail')}</span><span><strong>Within 5 days</strong>I read your answers and reply.</span></li>
              <li><span class="ns-ic">{icon('doc')}</span><span><strong>Before anything starts</strong>You get a price in writing.</span></li>
              <li><span class="ns-ic">{icon('rocket')}</span><span><strong>About 30 days</strong>Your site goes live.</span></li>
            </ol>
          </div>
          {talk}
        </div>
      </div>
    </section>'''

page('start.html', 'Start a project | Stray Wolf Technology',
     'Fourteen quick questions about your business and your website. Answer them and Jeremy replies within five days.',
     start_main, current='start.html', body_class='inner page-start')


# ---------------------------------------------------------------- Thanks and 404

def go_cards(links, label):
    return f'''          <nav aria-label="{label}"><ul class="go-cards" role="list">''' + ''.join(
        f'<li><a href="{href}"><span class="go-ic">{icon(ic)}</span><span class="go-t"><strong>{text}</strong><small>{sub}</small></span>{ARROW}</a></li>' for href, ic, text, sub in links) + '</ul></nav>'


def end_page(h1, lead, inner, badge, side):
    return f'''    <section class="end-page" aria-labelledby="end-h">
      <div class="wrap end-grid">
        <div class="end-text">
          {badge}
          <h1 id="end-h" class="h1">{h1}</h1>
          <p class="lead">{lead}</p>
{inner}
        </div>
        <div class="end-side" aria-hidden="true">
          <div class="hero-grid-lines"></div>
          {side}
        </div>
      </div>
    </section>'''


WOLF = '<img src="images/brand/stray-wolf-symbol-reverse.svg" width="200" height="200" alt="">'

thanks_main = end_page('Got it. Thanks.', 'Your answers are in. Here’s what happens next.', f'''          <ol class="thanks-steps" role="list">
            <li class="is-done"><span class="ts-n">{icon('check')}</span><span><strong>Your answers are in</strong>Nothing else to do right now.</span></li>
            <li><span class="ts-n">2</span><span><strong>I reply within five days</strong>With questions, or a time to talk.</span></li>
            <li><span class="ts-n">3</span><span><strong>A price in writing</strong>Before anything starts.</span></li>
            <li><span class="ts-n">4</span><span><strong>Live in about 30 days</strong>Only once you’ve seen it and said yes.</span></li>
          </ol>
''' + go_cards([('index.html', 'arrow-left', 'Back to the homepage', 'Where you started'), ('work.html', 'layout', 'See the work', 'Sites I’ve built')], 'Where to next'),
    f'<span class="end-badge end-badge-ok">{icon("check")}Sent</span>', WOLF)

page('thanks.html', 'Thanks | Stray Wolf Technology', 'Your answers are in.', thanks_main)


lost_main = end_page('That page isn’t here.', 'The link may be old, or the address may have a typo. One of these should get you where you were going.',
                     go_cards([('index.html', 'compass', 'Home', 'Start from the top'), ('work.html', 'layout', 'Work', 'Sites I’ve built'),
                               ('about.html', 'person', 'About', 'One person, start to finish'), ('start.html', 'send', 'Start a project', 'About five minutes')], 'Pages on this site'),
                     '<span class="end-badge">Error 404</span>', '<p class="end-404">404</p>' + WOLF)

page('404.html', 'Page not found | Stray Wolf Technology', 'That page could not be found.', lost_main)


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

privacy_main = page_head('Privacy', 'Privacy, in plain English.', 'The short version: this site only collects what you send, and only uses it to reply to you and plan your project.') + f'''
    <section class="section section-tight" aria-label="Privacy details">
      <div class="wrap">
        <ul class="pv-cards" role="list">{''.join(f'<li data-reveal><span class="tile-ic">{icon(i)}</span><h2 class="pv-h">{h}</h2><p>{t}</p></li>' for i, h, t in SUMMARY)}</ul>
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
