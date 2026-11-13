# SYNC: what is happening right now

The one shared notebook for every Claude thread working on these repositories. Read it before starting, update it before handing files over.
How the system fits together is in `README.md`; the Site Notes service is in `worker/README.md`; past versions are in `CHANGELOG.md`.
Last updated: Nov 13 2026, 22:50 UTC (V49: code cleanup + header moon).

## Working now

One line per thread that is changing files: `- what, which files (time UTC)`. Remove your line when your files are written.

- (nobody)

## Current versions

- **Site:** V49 (`VERSION` in `tools/build.py`). Next site change is V50. Before naming a version, also check the last lines of `.git/logs/HEAD`.
- **Worker:** `2026-11-13k` live in Cloudflare and saved in `worker/worker.js`. `2026-11-13l` (report retried with different date ranges) was built and tested as a backup, never deployed; its copy is outside the repo. Next unused letter: **`2026-11-13l`** (or `YYYY-MM-DDa` on a new day).
- **Tests:** `node worker/test-worker.mjs`. GitHub runs it, the build check and the HTML check on every push (Actions tab).

## Rules for every thread

1. **Start:** read this file from Jeremy's folder `C:\Users\jsgli\Documents\Websites\Stray-Wolf-Technology` (it can be newer than GitHub). Add a **Working now** line. If another thread is in the same files, wait.
2. **Build on Jeremy's current files**, never on older copies. Check his folder matches GitHub `main` before writing; write only the files you changed.
3. **Never push or commit.** Write files into his folder, then give him the exact commit message, one per repo.
4. **Site:** edit `src/`, run `python tools/build.py` and ship the rebuilt `docs/` (his PC has no Python). Bump `VERSION` when `site.css` or `site.js` change.
5. **Worker:** take the next letter above, run the tests, save `worker/worker.js` the same time it is pasted into Cloudflare, update **Current versions**.
6. **Admin page:** its Content-Security-Policy lists `sha256` hashes of its inline scripts. Change a script, recompute the hash, or the page goes blank.
7. **Portal:** `site-notes.js` must stay byte-identical in TVIS (`src/assets/site-notes.js`), FOTCL (`site-notes.js`) and the kit. Per-client words go in `data-` settings on the script tag.
8. **End:** remove your Working now line, add one Log line, update Pending.

## Pending (waiting on Jeremy or a decision)

- Hash client passwords? Today they are stored readable in KV so the admin can show them. Hashing means a password can only be shown right after it is set.
- Make the repository private (Cloudflare Pages, free, also allows real security headers) or keep it public. While public, keep secrets out of every file.
- New Web3Forms key registered to info@ (today's key sends leads to the personal Gmail).
- Google hours feature (read-only pull from Google Places) is built but not installed; files outside the repo.
- Code cleanup still to do: move the admin page's script and styles into their own files (no more CSP hashes), and tidy the Worker (route table, remove the `&test=2/3` debug probes) once analytics is settled.
- Owner tasks: request indexing in Search Console, Bing import, check the firemarktech.com redirect, Google Business Profile ownership/description/hours/photos, check SPF/DKIM/DMARC.

## Log (newest first, one line each)

- 2026-11-13 22:50 UTC: V49. Code cleanup: README with an architecture diagram, `worker/README.md` (routes, KV keys, deploy, versions), `CHANGELOG.md` (replaces PICKUP.md), this file slimmed to one project, GitHub checks (`.github/workflows/checks.yml`), 9 unused images/fonts and unused CSS removed (72 full-page screenshots identical), Pricing shows no dollar amounts ("Let's talk"). Header moon: hold it 2 s to open the admin, same as the footer moon. TVIS + FOTCL: `site-notes.js` now identical (caption example moved to `data-caption-example`), FOTCL `notes/brand/` removed.
- 2026-11-13 16:15 UTC: 13j live (15:58) but `&test=1` still fails: sign-in OK, the very first report (visitors) gets no answer in 6 s, twice. So it is not the parallel calls. Robot confirmed Viewer on 563451944 (Jeremy). Worker 2026-11-13k written to `worker/worker.js` (not pasted yet): 13j + `&test=3`, which tries 8 small Google calls (discovery, tokeninfo, GA admin, metadata GET, checkCompatibility POST, runReport with header / with token in the address) and shows which answer. Tests 138 pass.
- 2026-11-13 16:10 UTC: Worker 2026-11-13j written to `worker/worker.js` (not pasted yet). Analytics fix: the 6 Google reports now go one after another, each with its own stop switch and a 6 s limit that also covers reading the answer, one retry if Google hangs or errors (5xx), whole fetch ends by 16 s (admin waits 20 s), last saved numbers shown if Google still fails. `/api/check?...&test=1` now times sign-in and each of the 3 headline reports (`&test=2` asks them all at once, to compare). Tests 135 pass. Wrangler debug (13k-debug) skipped; 13k is free. Hours "Working now" line cleared (hours work still paused).
- 2026-11-13 15:27 UTC, Client Portal (main project thread): TVIS + FOTCL portal Edit mode card now shows a light framed picture of their website (brand/site-preview.jpg). Pushed: TVIS 462f8b2, FOTCL ec32571. (Main)
- Nov 13 2026: Main signed off Portal's handoff: SYNC.md, README.md, PICKUP.md pointer, worker/ (worker.js 13i, tests 118 pass). TVIS 04de78a and FOTCL cda6ceb already committed; admin page unchanged since 52bd60a. (Main)
- Nov 13 2026: Worker 2026-11-13i live in Cloudflare and saved to `worker/worker.js`; shared state and sign-off entry added here. (Portal)
- Nov 13 2026: Worker 2026-11-13i checked: login sessions (admin 30 min idle / 8 h max, clients 2 h / 24 h, real log out, new password ends logins, per-login lockout, picture checks, admin answers only straywolftech.com) all pass with invoices: 118 checks + invoice checks in `worker/test-worker.mjs` (`node worker/test-worker.mjs`). No Worker code change. (Portal)
- Nov 13 2026: SYNC.md added; it is the one shared notebook (PICKUP.md keeps the version history). Only the main project gives Jeremy commits. (Main)
- Nov 13 2026: Admin: login time-outs, real Log out, Invoices tab, Analytics fixes. (Portal)
- Nov 12 2026: V48 moon door to /admin, Stray Wolf Admin login. (Main + Portal)
- Nov 11 2026: V47 sharper work frames and chat card. (Main)
- Nov 11 2026: V39 to V42 Google Business Profile, review button, G mark. (SEO)

## Other repos

- Client sites: `jsglisson3/TVIS-Site-Work-and-Construction`, `jsglisson3/FOTCL` (both with `/portal`), `jsglisson3/GLP-Home-Options`. Same rules: one writer at a time, build on Jeremy's current files.
