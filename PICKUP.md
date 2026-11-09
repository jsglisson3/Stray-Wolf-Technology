# Pick up here (Stray Wolf Technology)

Last updated November 9, 2026, after the v9 round (the About page rebuilt from scratch; the numbers strip removed at Jeremy's request). This repository (`jsglisson3/Stray-Wolf-Technology`) replaces `jsglisson3/Firemark` for the new brand.

## Where things stand

The site is rebuilt as **Stray Wolf Technology** (the rebrand of Firemark), in a clean, plain style: paper and stone, charcoal type, one orange. Headings are Outfit at medium weight (the orange accent at 600); text is Bricolage Grotesque; Zilla Slab lives in the logo only. (Nov 9: Zilla headings in v5, Instrument Serif in v7, Outfit from v8. The two instrument-serif woff2 files and their LICENSE in docs/fonts are unused now and safe to delete.) No illustration. Still a hidden **draft** (yellow banner, noindex) until launch.

Pages: Home, Work, About, Start a project (the fourteen questions), thanks, privacy, 404.

About (v9, rebuilt Nov 9 at Jeremy's request): hero "One person, start to finish." with a profile card (the logo until `HEADSHOT = True`, then the photo; name, "Taking a few projects at a time", three facts) → "Six things you can count on" (a sticky heading beside six numbered pledges that light up as you scroll) → "Is this a fit?" (three yes/no questions answered on the page by site.js, nothing sent; the answer text lives in site.js) → "No pack. One person." (the wolf on stone, the name story) → the closing card. No services block on About any more (it is on the homepage). `contact.html` and `brand.html` (old Firemark addresses) redirect.

Homepage (v8), top to bottom: the hero (an Outfit headline with "your needs." in orange; three promises: hand-built, yours to keep, about 30 days; and a light stone panel where the real client sites sit stacked like windows and turn every few seconds, with a "Recent work, live now" label, a count and arrows on top and the name underneath), 01 How it works (four steps on a line that fills as you scroll), 02 What I do (four tabs; each plays a short scene of that service, and the tabs move on by themselves until someone picks one), 03 Recent work (big centred slides that rotate by themselves, with pause, arrows and dots; TVIS first), 04 Questions (accordion), the closing card (type a business name, it carries into the form), the footer. Removed in v6 at Jeremy's request: the comparison section and "Who you'll work with" (the story and numbers still live on About). The design system (colours, type, spacing, shadows, buttons, fields) is the `:root` block and the sections of `docs/css/site.css`; icons are in `src/partials/sprite.html`.

Checks on this build:
- Accessibility scan (axe): 0 issues on all seven pages at phone and desktop widths.
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
- [ ] **Email at the new domain**: Google Workspace on straywolftech.com (jeremy@ as the user, hello@ as a free alias), then set `EMAIL` and swap `FALLBACK_EMAIL`.
- [ ] **Form service: Web3Forms**. Sign up at web3forms.com with the address the form should deliver to (free plan is enough). Paste the access key into `WEB3FORMS_KEY`, rebuild, send yourself a test. Until then the form opens a pre-filled email, so nothing is broken meanwhile.
- [ ] **Headshot** (optional): save as `docs/images/jeremy.webp` (4:3, 1200px wide or more), set `HEADSHOT = True`. It replaces the demo in the hero and the logo panel on the About page.
- [ ] Phone and booking link, if wanted (`PHONE`, `BOOKING_URL`).
- [ ] Install the Claude GitHub App on this repository so Claude can push changes: https://github.com/apps/claude/installations/select_target

### Launch day
1. In `tools/build.py`, set `LAUNCHED = True`, then run `python tools/build.py`. That removes the draft banners and the noindex tags.
2. Commit and sync in VS Code. Don't delete `docs/CNAME`.
3. After launch: add the site to Google Search Console, submit `sitemap.xml`, send yourself a test from the form.

- Copy rule (Jeremy, Nov 9): never say "anywhere in the US" (or "nationwide") on the site; say "for owner-run businesses" instead. Never "small business". The About name story is two short paragraphs after "A stray wolf doesn't run with a pack."
