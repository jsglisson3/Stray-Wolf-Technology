# Pick up here (Stray Wolf Technology)

Last updated November 9, 2026, after the V12 round (V11's "print plate" redesign of the whole site, then a much calmer hero and three new pages: Pricing, Care plan and Reviews). This repository (`jsglisson3/Stray-Wolf-Technology`) replaces `jsglisson3/Firemark` for the new brand.

## Where things stand

The site is rebuilt as **Stray Wolf Technology** (the rebrand of Firemark), in a clean, plain style: paper and stone, charcoal type, one orange. Headings are Outfit at medium weight (the orange accent at 600); text is Bricolage Grotesque; Zilla Slab lives in the logo only. (Nov 9: Zilla headings in v5, Instrument Serif in v7, Outfit from v8. The two instrument-serif woff2 files and their LICENSE in docs/fonts are unused now and safe to delete.) No illustration. Still a hidden **draft** (yellow banner, noindex) until launch.

Pages: Home, Work, Pricing (first draft, no monthly fees), Reviews (coming soon until REVIEWS is filled), About, Start a project (the six questions), thanks, privacy, 404. care.html only redirects to Pricing.

About (v9 content, V11 look): hero "One person, start to finish." with a profile panel (the logo until `HEADSHOT = True`, then the photo; name, "Taking a few projects at a time", three facts) → "Six things you can count on" (six plain promises on a ruled grid) → "Is this a fit?" (three yes/no questions answered on the page by site.js, nothing sent; the answer text lives in site.js) → "No pack. One person." (the wolf on stone, the name story) → the closing card. No services block on About any more (it is on the homepage). `contact.html` and `brand.html` (old Firemark addresses) redirect.

Homepage (V12), top to bottom: the hero (the headline with "your needs." in orange on the left; the lead, the buttons and one small "Recently built" thumbnail that changes every 3 seconds on the right; nothing else), How it works ("From first call to launch.", the 30-day ruler with four steps), What I do (four services set large; each plays a short scene on a stone stage, and they move on by themselves until someone picks one), Recent work (one site at a time on its mount, with pause, arrows and bars; TVIS first), Questions (accordion), the close (type a business name, it carries into the form), the footer. The design system (colours, type, rules, buttons, fields) is the `:root` block and the sections of `docs/css/site.css`; icons are in `src/partials/sprite.html`. See "V11" at the bottom for the details.

Checks on this build:
- Accessibility scan (axe): 0 issues on all ten pages at phone and desktop widths.
- No `[PLACEHOLDER]` or `[CONFIRM]` tags anywhere. The build stops if one would reach a page.

Preview of the current build: https://claude.ai/artifact/4Ra3dXbmWZopH7tLtSyNQQ

## Decisions (Nov 8 and 9, 2026)

- Name **Stray Wolf Technology**; brand shows "Stray Wolf" with small "Technology". Logo locked (Zilla Slab wordmark with the cactus t, faceted wolf).
- Headline: **"A website built around your needs."**
- Positioning on the site: bespoke, hand-built websites; one person; by referral only; a few clients at a time.
- Services (What I do): website design and build; domain registration and setup; hosting and small updates; business email setup (renamed from "email at your own domain" Nov 9: a professional address instead of a Gmail, set up and handed over). **Not** Google Business Profile or social media.
- Client sites: a simple list, one clean image and a link each, never case studies. On the homepage they sit near the end, in a carousel.
- No Texas or personal-background copy on the site. Jeremy by first name only. Pricing stays "a price in writing", no numbers.
- Promises: reply within five days; a price in writing before anything starts; live in about 30 days (changed from 45 by Jeremy, Nov 9).
- Hero: the B layout (paper words, a light stone panel; charcoal panels were lightened Nov 9 because Jeremy found them a bit dark and bold). The panel shows the stacked real sites (v7; the sketch-to-site demo was dropped Nov 9) until `HEADSHOT = True`, then your photo. No "by referral" pill above the headline, and "price in writing" is no longer a hero promise (both Jeremy, Nov 9).

## Settings block (top of `tools/build.py`)

`DOMAIN`, `LAUNCHED`, `VERSION`, `EMAIL`, `PHONE`, `BOOKING_URL`, `HEADSHOT`, `WEB3FORMS_KEY`, `FALLBACK_EMAIL`. Anything empty is left off the site. Change a setting, rebuild, commit.

## Add a site to Work

1. Open `src/sites.py`. Copy one block, from `{` down to `},`, and paste it at the top of the list so the newest site comes first.
2. Change `name`, `about` (one line), `link`, `image` (a short lowercase name) and `tag` (leave `""`, or "Volunteer concept, not the official site").
3. Send Claude the link. Claude takes the screenshot, saves the `docs/images/work/<image>-desktop-*.webp` sizes, runs the build and hands the files back.

## Before launch

- [ ] **Turn on GitHub Pages for this repository**: Settings > Pages > Build and deployment > Source: **Deploy from a branch**, Branch: **main**, folder **/docs**, Save.
- [ ] **Point straywolftech.com at it** (bought Nov 8, 2026 at Cloudflare Registrar, 2 years, auto-renew):
  1. In Cloudflare DNS for straywolftech.com, add four **A** records for `@` (DNS only, grey cloud): `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, and a **CNAME** `www` pointing to `jsglisson3.github.io` (DNS only).
  2. `docs/CNAME` already says `straywolftech.com` and `DOMAIN` in `tools/build.py` matches. In Settings > Pages, check the custom domain shows `straywolftech.com`, then tick **Enforce HTTPS** once the certificate is issued (can take up to an hour).
  3. For firemarktech.com: once Stray Wolf is live, add a Cloudflare **Redirect Rule** from `firemarktech.com/*` and `www.firemarktech.com/*` to `https://straywolftech.com/${1}` (301), and turn off Pages on the old Firemark repository so the two don't compete. Keep firemarktech.com registered while any old links exist.
- [x] **Email at the new domain**: Cloudflare Email Routing forwards info@ and jeremy@straywolftech.com to Jeremy's Gmail (he found Google Workspace too expensive). `EMAIL` and `FALLBACK_EMAIL` are info@straywolftech.com since Nov 9, 2026: it shows in the footer, on the Start page ("Rather talk first?") and on the privacy page. Replies to clients should go out from info@ too (Gmail "Send mail as").
- [x] **Form service: Web3Forms**: the access key went into `WEB3FORMS_KEY` on Nov 9, 2026, so Send delivers the answers to the inbox the key was registered with and lands the visitor on thanks.html. The cloud session could not reach web3forms.com to test it: after committing, open straywolftech.com/start.html, fill in the four required answers and press Send once.
- [ ] **Prices (V12 first draft)**: `STARTER_FROM`, `LARGER_FROM` and `CARE_MONTH` at the top of `tools/build.py` are Claude's suggestions, not Jeremy's decisions. Confirm or change them, and read every line of `pricing.html` and `care.html` (the words are in `src/pages.py` under Pricing and Care plan) before launch.
- [ ] **Reviews**: `reviews.html` says "Coming soon" and lists the three sites. Once two or three clients have sent real words (with their OK), replace the list with their quotes.
- [ ] **Headshot** (optional): save as `docs/images/jeremy.webp` (4:3, 1200px wide or more), set `HEADSHOT = True`. It replaces the logo panel on the About page.
- [ ] Phone and booking link, if wanted (`PHONE`, `BOOKING_URL`).
- [ ] Install the Claude GitHub App on this repository so Claude can push changes: https://github.com/apps/claude/installations/select_target

### Launch day
1. In `tools/build.py`, set `LAUNCHED = True`, then run `python tools/build.py`. That removes the draft banners and the noindex tags.
2. Commit and sync in VS Code. Don't delete `docs/CNAME`.
3. After launch: add the site to Google Search Console, submit `sitemap.xml`, send yourself a test from the form.

- Copy rule (Jeremy, Nov 9): never say "anywhere in the US" (or "nationwide") on the site; say "for owner-run businesses" instead. Never "small business". The About name story is one short paragraph starting "A stray wolf doesn't run with a pack."

## V10 (Nov 9, 2026): the hero, redone from Dribbble research
- The homepage hero is now: three promises and a "Taking a few projects at a time" status small on the left, the headline in the middle, and the bottom row is the Stray Wolf wordmark (images/brand/stray-wolf-wordmark-color.svg) set across eight columns with one real client site mounted on stone beside it. Built by `hero()` in tools/build.py; styles in docs/css/site.css under "Hero"; script block "The hero" in docs/js/site.js.
- The site panel rotates through SITES from src/sites.py every 5.2 seconds (first site first), with the name, domain and link following. A mouse over it, keyboard focus or the Next button stops it; reduced motion never rotates. Images come from docs/images/work/<image>-desktop-{640,960,1440}.webp, cropped from the top-left corner.
- When HEADSHOT = True the panel shows the photo instead (images/jeremy.webp).
- The old stacked "deck" (build_deck, data-deck) is gone. VERSION is '10'.
- Dribbble research that drove it lives on Jeremy's PC: Documents\FiremarkTech\research-shots\stray-wolf-hero (research.md, shots.csv, 60 shots).

## V11 (Nov 9, 2026): the whole site, redone the same way as the V10 hero
Jeremy asked for "a full site overhaul the same way" as the V10 hero, and said the hero still needed work. The look is now "the print plate", taken from the Dribbble research: paper and stone, charcoal type, one orange; square corners; flat surfaces with no resting shadows, gradients or grid textures; thin charcoal rules where a list or a zone needs one; no small uppercase labels above headings; real client sites shown on stone "mounts".
- Hero: the headline, lead and buttons top left; the full colour wordmark under them (drawn into the page so the cactus grows in after the name wipes on); three promises on a ruled strip along the bottom; one real client site on a stone panel that runs from the header to the bottom rule and off the right edge of the screen. The site still changes every 5.2 seconds; a thin orange line along the rule shows when, and a "1 / 3" count sits by the Next button. On phones: text, wordmark, site, promises.
- How it works: a 30-day ruler. An orange line runs along it as you scroll, and each of the four steps lights up when the line reaches its day (STEPS in tools/build.py now starts each step with its day).
- What I do: the four services set large as a list (the chosen one in charcoal with an orange timer line), the scene on a flat stone stage, and the description as a caption under the scene.
- Recent work: one site at a time on its stone mount (with its phone view when there is one), the name and words beside it; bars, pause and arrows underneath. TVIS first.
- Questions and the close: ruled rows; the close is a full-width stone band with "Let’s talk about yours." set very large and the business-name box.
- Header: a plain paper bar, the current page underlined in orange, a charcoal rule once you scroll. Footer: stone, a charcoal rule, plain columns; "Built with love, one site at a time." unchanged.
- Work page: each site big on its mount, a second page of it beside when `extra` is set in src/sites.py (GLP: the net sheet; FOTCPL: the membership section), words under a rule.
- About: the same head, the profile on a stone panel off the right edge, the six promises as a ruled grid (no numbers or icons), square Yes/No buttons, the wolf on stone beside the name story (story text unchanged).
- Start a project: sections under charcoal rules with a "1 / 6" count, square fields and choices, the progress list and "What happens next" as ruled lists. The Web3Forms key slot and the email fallback are untouched.
- Privacy, thanks and 404 follow the same heads and rules.
- VERSION is '11'. docs/css/site.css was rewritten from scratch; the old "light pass" overrides are gone.
- Checks: axe 0 issues on all seven pages at 390 and 1440; no sideways scroll from 320 to 1920; the hero rotation, ruler, service tabs, carousel, questions, close form, start form, fit check and phone menu all tested with no console errors.

## V12 (Nov 9, 2026): a much calmer hero, and three new pages
Jeremy on the V10/V11 hero: "there is so much going on"; the site previews "need to be much much smaller and subtle", but keep "the natural rotation every couple of seconds". He picked option C of three.
- Hero: only the words. The headline on the left (three lines on a laptop); on the right the lead, the two buttons and one small "Recently built" line under a thin rule: an 88px thumbnail of a client site that changes every 3.2 seconds (`data-every` on the `data-sites` box; site.js reads it), the site's name, and "See the work" to the Work page. The wordmark, the promises strip, the status line and the big stone panel are gone from the hero. Hovering the line pauses it; reduced motion never rotates.
- How it works is now headed "From first call to launch." (Jeremy wanted "Four steps. One person. No surprises." changed).
- New pages, all first drafts for Jeremy to confirm: **pricing.html** (what projects usually cost: a starter site from $1,800, a larger site from $3,500, the care plan after launch; what's in every price; what costs extra; how paying works, half to start and half at launch), **care.html** (the care plan: hosting, domain watched, small changes up to an hour a month within five days, fixes, backups, a monthly check; what's not covered; how it works), **reviews.html** (coming soon, with the three sites listed until real quotes exist). The numbers are the `STARTER_FROM`, `LARGER_FROM`, `CARE_MONTH` settings at the top of tools/build.py. The homepage questions "How much does a website cost?" and "Can I make changes after it's live?" now point at these pages.
- Menu: Work, Pricing, Care plan, Reviews, About, Start a project. The phone menu now shows up to 1023px wide (it was 767px) and the header tagline only from 1280px up, so six items fit. Footer "Pages" and sitemap.xml list the new pages.
- Thanks and 404 pages: the small labels above the headings are gone. "Your colours" is now "Your colors".
- VERSION is '12'.
- Checks: axe 0 issues on all ten pages at 390 and 1440; no sideways scroll from 320 to 1920; the hero rotation, ruler, service tabs, carousel, questions, close form, start form, fit check and phone menu all tested with no console errors.

## V13 (Nov 9, 2026): smaller jobs, and a much shorter form
Jeremy wants fixes, single pages and refreshes offered as real work, not only whole sites (he just did one for Snip and Sprout Co). And he wants the Start a project form "much simpler", so nobody gets bogged down.
- Pricing: a third row, "A fix, a page or a refresh", from `FIX_FROM` ($150, a suggestion to confirm), with `PAGE_FROM` and `REFRESH_FROM` ($400, $900) in the settings for later.
- What I do: a new second tab, "Fixes and single pages", with its own little scene (a broken form fixed, one new page added). Five tabs now. The lead above the tabs mentions fixes and pages.
- Homepage question: "Do you take on smaller jobs?" (yes, days not weeks, from $150, price in writing first). "How much does a website cost?" and "Can I make changes after it's live?" still point at Pricing and Care plan.
- Start a project: fourteen questions in six sections became six questions and your contact details: what do you need (a new website, or changes to the one you have), business name, what you do and who your customers are, what the website should do (pick any), the link to the site you have, and anything else. Name, email and phone at the end. Only business name, what you do, name and email are required. The progress card, the sticky phone bar and the "ready" line are gone (site.js and the CSS too). Every mention of "fourteen questions, about five minutes" is now "six questions, about two minutes" (homepage steps and questions, close, footer, fit check).
- Field names Web3Forms will show: project_kind, business_name, what_you_do, goal_new_customers, goal_show_work, goal_calls_quotes, goal_bookings, goal_sell_online, current_site, anything_else, name, email, phone.
- VERSION is '13'.
- Checks: axe 0 issues on all ten pages at 390 and 1440; no sideways scroll from 320 to 1920; hero rotation, ruler, service tabs (five), carousel, questions, close form, start form (9 fields, 4 required, validation), fit check and phone menu all tested with no console errors.
- Still waiting on Jeremy: the prices (1,800 / 3,500 / 40 a month / 150 / 400 / 900), a live test send of the form, Dani's OK to list Snip and Sprout on Work.

## V14 (Nov 9, 2026): no monthly fees, the client's 10%, reviews wired, a Search Console slot
- Jeremy: "I don't want anything monthly, let's lose that, I feel like that's a selling point." The care plan is gone. care.html is now a redirect to pricing.html; it is out of the menu, the footer, the sitemap and the settings (no more CARE_MONTH). Pricing says "No monthly fees, ever" in the pledges and the lead, and the After launch row reads "Monthly $0". On the homepage, "Can I make changes after it's live?" and the "Hosting and small updates" line say the same: no monthly fee, changes quoted per job from $FIX_FROM.
- Jeremy: make it crystal clear that the client owns the first 10%: being clear about what they want, and the images, logo and text. How it works has five steps now (Day 1, Within 5 days, Your 10%, The build, About day 30). The lead says "The first 10% is yours: be clear about what you want, and send the words, photos and logo. The other 90% is mine." The question "What do you need from me?" says the same. The Start page's "What happens next" and the thanks page steps gained a "Your 10%" line.
- Reviews: a `REVIEWS` list in the settings (quote, name, business, link). Empty = the coming-soon page as before. Filled = one quote per row with the name, the business and a "Visit the site" link. Real words only, with the client's OK to be named. The message to ask clients with is in /mnt/project-files/rebrand/site-v14/review-request.md (also in the thread).
- Search Console: a `SEARCH_CONSOLE` setting prints the google-site-verification meta tag on every page once filled (that needs a rebuild, so it is Claude's to do). The easier routes need no build: the HTML-file method (drop Google's google….html file into docs/ and commit) or a DNS TXT record at Cloudflare. The sitemap is at /sitemap.xml and robots.txt points at it. Until LAUNCHED is True every page is noindex, so Google indexes nothing yet; verifying and submitting the sitemap now is still fine.
- VERSION is '14'.
- Checks: axe 0 issues on all nine pages at 390 and 1440; no sideways scroll from 320 to 1920; hero rotation, ruler (five steps), service tabs, carousel, questions, close form, start form, fit check and phone menu all tested with no console errors.
