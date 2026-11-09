# Pick up here (Stray Wolf Technology)

Last updated November 9, 2026, after the clean rebuild. This repository (`jsglisson3/Stray-Wolf-Technology`) replaces `jsglisson3/Firemark` for the new brand.

## Where things stand

The site is rebuilt as **Stray Wolf Technology** (the rebrand of Firemark), in a clean, plain style: paper, charcoal, one orange, the Zilla Slab logo face for headings. No illustration. Still a hidden **draft** (yellow banner, noindex) until launch.

Pages: Home, Work, About, Start a project (the fourteen questions), thanks, privacy, 404. `contact.html` and `brand.html` (old Firemark addresses) redirect.

Homepage (v5), top to bottom: the hero (words on paper, and a charcoal panel where a small example website goes from sketch to finished), 01 The difference (the usual way vs. Stray Wolf), 02 How it works (four steps on a line that fills as you scroll), 03 What I do (four service tiles), 04 Who you'll work with (the story and four numbers), 05 Recent work (carousel in browser frames, TVIS first), 06 Questions (accordion), the closing card (type a business name, it carries into the form), the footer. The design system (colours, type, spacing, shadows, buttons, fields) is the `:root` block and the sections of `docs/css/site.css`; icons are in `src/partials/sprite.html`.

Checks on this build:
- Accessibility scan (axe): 0 issues on all seven pages at phone and desktop widths.
- No `[PLACEHOLDER]` or `[CONFIRM]` tags anywhere. The build stops if one would reach a page.

Preview of the current build: https://claude.ai/artifact/SNZHsAUkCtkusqKsvuurt5

## Decisions (Nov 8 and 9, 2026)

- Name **Stray Wolf Technology**; brand shows "Stray Wolf" with small "Technology". Logo locked (Zilla Slab wordmark with the cactus t, faceted wolf).
- Headline: **"A website built around your needs."**
- Positioning on the site: bespoke, hand-built websites; one person; by referral only; a few clients at a time.
- Services (What I do): website design and build; domain registration and setup; hosting and small updates; email at your own domain (setup). **Not** Google Business Profile or social media.
- Client sites: a simple list, one clean image and a link each, never case studies. On the homepage they sit near the end, in a carousel.
- No Texas or personal-background copy on the site. Jeremy by first name only. Pricing stays "a price in writing", no numbers.
- Promises: reply within five days; a price in writing before anything starts; live in about 45 days.
- Hero: the B layout (paper words, charcoal panel). The panel shows the sketch-to-site demo until `HEADSHOT = True`, then your photo.

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
