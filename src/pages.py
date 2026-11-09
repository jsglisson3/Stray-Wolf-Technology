"""Content for the inner pages. tools/build.py runs this file and provides:
   page(file, title, desc, main, current=None, body_class='inner', banner=True)   writes docs/<file>
   form                      the fourteen questions (src/partials/intake-form.html, with the settings filled in)
   SITES, work_list(sites)   the Work list (src/sites.py) as a plain two-across grid
   services()                the "What I do" list
   close_section(hid, line)  the charcoal closing band
   read(name)                a partial from src/partials
   CONTACT, WAYS             the email, phone and booking links, or '' while not set
Voice: first person, plain and short. Jeremy by first name only. Nothing unconfirmed goes on a page."""

CHECK = '<svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>'


def page_head(h1, lead):
    return f'''    <div class="wrap page-head">
      <h1 class="h1">{h1}</h1>
      <p class="lead">{lead}</p>
    </div>'''


# ---------------------------------------------------------------- Work

work_main = page_head('Work', 'Websites I’ve designed and built by hand. Tap one to see it live.') + f'''
    <section class="section section-tight" aria-label="Websites">
      <div class="wrap">
{work_list(SITES)}
      </div>
    </section>
{close_section('work-close-h', 'Want yours on this list?')}'''

page('work.html', 'Work | Stray Wolf Technology',
     'Websites Stray Wolf Technology has designed and built by hand for small businesses.',
     work_main, current='work.html')


# ---------------------------------------------------------------- About

about_main = page_head('Who you’ll work with', 'A stray wolf doesn’t run with a pack, and neither do I. I build websites on my own, for businesses that want to stand out.') + f'''
    <section class="section section-tight" aria-labelledby="fit-h">
      <div class="wrap split">
        <h2 id="fit-h" data-reveal>Who it’s for</h2>
        <div class="split-body" data-reveal>
          <p>Owner-run businesses anywhere in the US: the shop, the trade, the practice, the one-truck outfit. Most people find me through someone I’ve already built a site for.</p>
          <p>I only take work by referral, and only a few clients at a time, so every site gets my full attention. If you’re a franchise with a head office, a large online store, or you need a full agency team, I’m probably not the right fit, and I’ll say so up front.</p>
        </div>
      </div>
    </section>

    <section class="section on-stone" aria-labelledby="offer-h">
      <div class="wrap">
        <div class="sec-head"><h2 id="offer-h" class="h2" data-reveal>What I do</h2></div>
{services()}
      </div>
    </section>

    <section class="section section-tight" aria-labelledby="how-h">
      <div class="wrap split">
        <h2 id="how-h" data-reveal>How I work</h2>
        <ul class="ticks" role="list" data-reveal>
          <li>{CHECK}<span>Hand-built for your business. No templates, no page builders.</span></li>
          <li>{CHECK}<span>I get to know you and what you want out of a website before I design anything.</span></li>
          <li>{CHECK}<span>Everything in plain English, no jargon.</span></li>
          <li>{CHECK}<span>A price in writing before anything starts.</span></li>
          <li>{CHECK}<span>Nothing goes live until you’ve seen it and said yes.</span></li>
          <li>{CHECK}<span>Your domain, your content and your site are yours to keep.</span></li>
          <li>{CHECK}<span>One person to call, before and after launch.</span></li>
        </ul>
      </div>
    </section>

    <section class="section on-white" aria-labelledby="story-h">
      <div class="wrap split">
        <div>
          <img class="story-mark" src="images/brand/stray-wolf-symbol-color.svg" width="200" height="200" alt="" loading="lazy" decoding="async">
          <h2 id="story-h" data-reveal>Why “Stray Wolf”</h2>
        </div>
        <div class="split-body" data-reveal>
          <p>A stray wolf doesn’t run with a pack. There’s no agency behind me and no account manager between us. You talk to the person building your site.</p>
          <p>The internet is full of giants, and a small business can get lost in their shade. My job is to build the site that stands out among them.</p>
        </div>
      </div>
    </section>
{close_section('about-close-h')}'''

page('about.html', 'About | Stray Wolf Technology',
     'Stray Wolf Technology is Jeremy: one designer building bespoke, hand-built websites for businesses anywhere in the US, by referral.',
     about_main, current='about.html')


# ---------------------------------------------------------------- Start a project (the intake)

if WAYS:
    talk = '<div><h2 class="aside-h">Rather talk first?</h2>\n            <ul class="reach-list" role="list">' + ''.join(f'<li>{x}</li>' for x in WAYS) + '</ul></div>'
else:
    talk = '<div><h2 class="aside-h">Just have a question?</h2>\n            <p class="muted">Put it in the last box. You don’t need all fourteen answers to send the form.</p></div>'

start_main = page_head('Start a project', 'Fourteen questions, about five minutes. I read every answer before I start, and you’ll hear from me within five days.') + f'''
    <section class="section section-tight" aria-label="The questions">
      <div class="wrap start-grid">
        <h2 id="start-h" class="visually-hidden">The fourteen questions</h2>
        {form}
        <div class="start-aside" role="group" aria-label="What happens next">
          <div>
            <h2 class="aside-h">What happens next</h2>
            <ol class="next-steps">
              <li>I read your answers and reply within five days.</li>
              <li>You get a price in writing before anything starts.</li>
              <li>Your site goes live in about 45 days.</li>
            </ol>
          </div>
          {talk}
        </div>
      </div>
    </section>'''

page('start.html', 'Start a project | Stray Wolf Technology',
     'Fourteen quick questions about your business and your website. Answer them and Jeremy replies within five days.',
     start_main, current='start.html')


# ---------------------------------------------------------------- Thanks (where the form lands)

thanks_main = page_head('Got it. Thanks.', 'Your answers are in. You’ll hear from me within five days.') + '''
    <section class="section section-tight" aria-label="What to do next">
      <div class="wrap">
        <ul class="trail" role="list">
          <li><a class="link" href="index.html">Back to the start</a></li>
          <li><a class="link" href="work.html">See the work</a></li>
        </ul>
      </div>
    </section>'''

page('thanks.html', 'Thanks | Stray Wolf Technology', 'Your answers are in.', thanks_main)


# ---------------------------------------------------------------- 404

lost_main = page_head('That page isn’t here.', 'The link may be old, or the address may have a typo.') + '''
    <section class="section section-tight" aria-label="Where to go next">
      <div class="wrap">
        <ul class="trail" role="list">
          <li><a class="link" href="index.html">Home</a></li>
          <li><a class="link" href="work.html">Work</a></li>
          <li><a class="link" href="about.html">About</a></li>
          <li><a class="link" href="start.html">Start a project</a></li>
        </ul>
      </div>
    </section>'''

page('404.html', 'Page not found | Stray Wolf Technology', 'That page could not be found.', lost_main)


# ---------------------------------------------------------------- Privacy

delete_how = (f'Email {CONTACT["email"]} and ask' if CONTACT['email'] else 'Reply to any email from Jeremy and ask')
sections = [
    ('What this site collects', '<p>Only what you send. When you answer the questions on the Start a project page, that’s your name, your business name, your email and anything else you choose to add, like a phone number, a link or a note.</p>'),
    ('How it’s used', '<p>To reply to you and plan your project. That’s it. Your details aren’t sold or shared for marketing, and you won’t be added to a mailing list.</p>'),
    ('Where it’s kept', '<p>The form is delivered by Web3Forms, a form service, which passes your answers on to Jeremy’s email. What Web3Forms itself keeps is covered by the privacy policy on <a href="https://web3forms.com/">web3forms.com</a>. If the form opens your email app instead, your answers go straight from your email to Jeremy.</p>'),
    ('Hosting', '<p>The site is hosted on GitHub Pages. Like most web hosts, GitHub keeps basic technical logs, such as IP addresses, to keep the service secure. This site uses no cookies, ads or tracking.</p>'),
    ('Deleting your details', f'<p>{delete_how}. Anything Stray Wolf Technology has from you will be deleted.</p>'),
    ('Changes', '<p>If this page changes, the date below changes too. Last updated November 9, 2026.</p>'),
]
privacy_main = page_head('Privacy', 'The short version: this site only collects what you send, and only uses it to reply to you and plan your project.') + '''
    <section class="section section-tight" aria-label="Privacy details">
      <div class="wrap prose">
''' + '\n'.join(f'        <section data-reveal><h2>{h}</h2>{t}</section>' for h, t in sections) + '''
      </div>
    </section>'''

page('privacy.html', 'Privacy | Stray Wolf Technology', 'What this website collects and what happens to it.', privacy_main)
