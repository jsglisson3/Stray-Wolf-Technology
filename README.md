# Stray Wolf Technology website

The website for Stray Wolf Technology: bespoke, hand-built websites, by referral, for businesses anywhere in the US.
This is the rebrand of the Firemark site. The Firemark site and its notes stay in the old `jsglisson3/Firemark` repository.

Start with **PICKUP.md**. It has where things stand, the before-launch list and how to publish.

## What's where

| Folder or file | What it is |
|---|---|
| `docs/` | **The website itself.** Everything GitHub Pages publishes. Open `docs/index.html` to see it. |
| `docs/css/site.css` | All the styles. Edit this file directly. |
| `docs/js/site.js` | The header and phone menu, the hero's rotating thumbnail, the 30-day ruler, the service tabs, the work carousel, the fit check and the Start a project form. Edit directly. |
| `docs/images/brand/` | Logo files (SVG): full logo, stacked logo, symbol and wordmark, in colour, reverse and one-colour versions. |
| `docs/fonts/` | Zilla Slab (headings) and Bricolage Grotesque (text), self-hosted. |
| `src/` | The page sources. **Edit these, not the `.html` files in `docs/`,** then run the build. |
| `src/layout.html` | The shell every page shares: head, header, footer. |
| `src/home.html` | The homepage's order of sections (each section is built in `tools/build.py`). |
| `src/pages.py` | Work, Pricing, Reviews, About, Start a project, thanks, privacy and the 404 page. |
| `src/sites.py` | The list of websites shown on the Work page and in the homepage carousel. |
| `src/partials/` | The six questions (`intake-form.html`) and the icon set. |
| `tools/build.py` | Rebuilds every page in `docs/` from `src/`. The settings block at the top holds the domain, the version number, the contact details and the prices. |
| `tools/` (other) | Helpers: accessibility checker (`a11y-check.js`), share-image source (`og-card.html`), the small logo files (`make-icons.js`: tab icon, phone home-screen icons, the logo for Google), screenshot tool (`shot.js`), curly-quote pass (`typeset.py`). |

## Preview it

Open `docs/index.html` in a browser, or in VS Code right-click it and choose **Open with Live Server**.
The 404 page only looks right on the real domain, because its links start with `/`.

## Change a page

1. Edit the text in `src/home.html` (homepage), `src/pages.py` (other pages) or `tools/build.py` (hero, steps, services, work, questions, the closing section).
2. In a terminal in this folder, run `python tools/build.py` (on Windows, `py tools/build.py` also works). No Python on the PC? Ask Claude to run it.
3. Refresh the page in your browser. The build also turns straight quotes into curly ones.

## Publish

Commit and sync in VS Code. GitHub Pages publishes the `docs/` folder on `main`. Don't delete `docs/CNAME`; it holds the domain.
