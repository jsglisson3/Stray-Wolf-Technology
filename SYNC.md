# SYNC: read this first, update it last

Jeremy runs three Claude projects on this repository at the same time. They cannot see each other's chats or memory.
**This file is the shared memory.** Every project reads it before starting work and updates it before handing files over.
Last updated: Nov 13 2026, 15:25 UTC (main project: signed off the Portal handoff).

## The three projects and who owns what

| Project | Owns | Never touches without saying so here |
|---|---|---|
| **Stray Wolf Tech** (main: site and brand) | `src/`, `tools/build.py` (except the SEO settings), the pages in `docs/`, `docs/css/site.css`, `docs/js/site.js` (except the Moon door block at the end), images, logo, copy, `PICKUP.md` version notes | `docs/admin/`, the Worker |
| **SEO / Google** | `docs/js/analytics.js`, `docs/sitemap.xml`, `docs/robots.txt`, `docs/review/`, meta tags and structured data, the settings `GA4_ID`, `SEARCH_CONSOLE`, `BING_VERIFY`, `SAME_AS`, `GOOGLE_PROFILE_URL`, `GOOGLE_REVIEW_URL`, `SERVICE_AREAS`, the Google bits in `src/pages.py` | page design and layout |
| **Client Portal / Admin** | `docs/admin/`, the Site Notes Worker (`site-notes.jsglisson.workers.dev`), `site-notes.js` and `/portal` on client sites, the Moon door block at the end of `docs/js/site.js` | page design and layout |

Shared files (`tools/build.py`, `docs/css/site.css`, `src/layout.html`): change only the lines you need, say which in the log below, and never rewrite the whole file from an old copy.

## Version numbers (shared by all three projects)

- Site versions are one sequence for everyone: V47, V48, V49... Any project that changes the site's look, CSS or JS takes the next one and bumps `VERSION` in `tools/build.py` (that also busts the `?v=` cache).
- **Before naming a version:** read the last lines of `.git/logs/HEAD` in Jeremy's folder (or `git log -5`) AND the log below. Next number = highest V you see + 1.
- Admin-only commits start `Admin:` and take no V number.
- Current site version: **V48** (pushed Nov 12).

## Start of every task

1. Jeremy: in VS Code, **Sync** first so your folder matches GitHub.
2. Claude: read this file from Jeremy's folder `C:\Users\jsgli\Documents\Websites\Stray-Wolf-Technology` (it can be newer than GitHub), then the part of `PICKUP.md` you need.
3. Check **Working now** below. If another project is in the same files, stop and tell Jeremy.
4. Add your line to **Working now**.

## End of every task

1. Copy Jeremy's current files from his folder and merge with yours before writing (never overwrite with an older copy).
2. Write your files to his folder. Only one project writes at a time.
3. Update this file: remove your **Working now** line, add one **Log** line, update **Pending**.
4. SEO and Portal: add your files to **Ready for sign-off** and tell Jeremy to check with the main project (no commit message). Main project: end the reply with the exact commit message. Jeremy commits and Syncs **before** switching to another project.

## Shared state (update this whenever you change the Worker, the admin page or site-notes.js)

- **Live Worker:** `2026-11-13i`, pasted and live in Cloudflare. Its source is `worker/worker.js` in this repo, an exact copy of what's live. Tests: `node worker/test-worker.mjs`.
- **Worker rule:** whoever changes the Worker takes the next unused version letter (next is `2026-11-13j`, or `YYYY-MM-DDa` on a new day), sets `VERSION` in `worker/worker.js`, saves the file here, and updates this line. Never paste a Worker into Cloudflare that isn't also saved here.
- **Admin and site-notes.js rule:** start from Jeremy's current file (`docs/admin/index.html` here, `site-notes.js` in FOTCL, `src/assets/site-notes.js` in TVIS), never from an older copy. The admin page has a Content-Security-Policy with `script-src` hashes, so recompute them whenever its scripts change.
- **Latest commits (Nov 13):** Stray-Wolf-Technology `52bd60a` (login sessions), TVIS `04de78a` (login sessions), FOTCL `cda6ceb` (login sessions).

## Who gives Jeremy commits (Jeremy, Nov 13 2026)

**Only the main project (Stray Wolf Tech) gives Jeremy commit messages.** The SEO and Portal projects never do. When they finish, they list their work under **Ready for sign-off** below and tell Jeremy to check with the main project. The main project reviews it (diff against GitHub, checks nothing clashes), writes one commit message per repo, then moves the lines to the Log.

## Ready for sign-off

Format: `- [Project] repo: changed files. One-line summary. (time UTC)`

- (nothing waiting)

## Working now

- (nobody)

## Pending (things waiting on Jeremy or a push)

- Confirm the website numbers show in the admin again with Worker 13i. (Portal project)
- Client passwords are stored readable in KV; hashing them is still open. Hashing means the admin can only show a client's password right after setting it (no Copy password later). Jeremy's call. (Portal project)
- Prices in `tools/build.py` are drafts to confirm. Headshot, phone, booking link still empty. (Main project)
- Search Console and Bing verification values still empty. (SEO project)

## Log (newest first, one line each)

- Nov 13 2026: Main signed off Portal's handoff: SYNC.md, README.md, PICKUP.md pointer, worker/ (worker.js 13i, tests 118 pass). TVIS 04de78a and FOTCL cda6ceb already committed; admin page unchanged since 52bd60a. (Main)
- Nov 13 2026: Worker 2026-11-13i live in Cloudflare and saved to `worker/worker.js`; shared state and sign-off entry added here. (Portal)
- Nov 13 2026: Worker 2026-11-13i checked: login sessions (admin 30 min idle / 8 h max, clients 2 h / 24 h, real log out, new password ends logins, per-login lockout, picture checks, admin answers only straywolftech.com) all pass with invoices: 118 checks + invoice checks in `worker/test-worker.mjs` (`node worker/test-worker.mjs`). No Worker code change. (Portal)
- Nov 13 2026: SYNC.md added; it is the one shared notebook (PICKUP.md keeps the version history). Only the main project gives Jeremy commits. (Main)
- Nov 13 2026: Admin: login time-outs, real Log out, Invoices tab, Analytics fixes. (Portal)
- Nov 12 2026: V48 moon door to /admin, Stray Wolf Admin login. (Main + Portal)
- Nov 11 2026: V47 sharper work frames and chat card. (Main)
- Nov 11 2026: V39 to V42 Google Business Profile, review button, G mark. (SEO)

## Other repos

- Client sites: `jsglisson3/TVIS-Site-Work-and-Construction`, `jsglisson3/FOTCL` (both with `/portal`), `jsglisson3/GLP-Home-Options`. Same rules: read their notes file first, one writer at a time.
- The Site Notes Worker lives in this repo at `worker/worker.js` (Jeremy doesn't want a separate repo). Cloudflare runs a pasted copy, so this file is the record of what's live.
- Project instructions for all three projects: see the bottom of this file.

## Project instructions (paste into each project's settings)

Same text for all three, only the first line changes. Add jsglisson3/Stray-Wolf-Technology to each project's repositories too.

```
This is the [MAIN SITE / SEO AND GOOGLE / CLIENT PORTAL AND ADMIN] project for Stray Wolf Technology.
Two other Claude projects work on the same repos at the same time. GitHub is our shared memory.
Before any work: read SYNC.md in the repo (from my folder C:\Users\jsgli\Documents\Websites\Stray-Wolf-Technology if you can reach it), and follow its start and end steps.
Stay inside what SYNC.md says this project owns. If a change needs another project's files, say so instead of doing it.
Version numbers are shared: check .git/logs/HEAD and the SYNC.md log before naming a site version. The live Worker source is worker/worker.js in that repo; read it before changing the Worker, the admin page or site-notes.js, and take the next Worker version letter from SYNC.md's Shared state.
Never push from the cloud. Write files to my local folder, only after merging with what is there.
Before you hand over files, update SYNC.md (Working now, Pending, one Log line).
SEO and Portal projects only: Do NOT give Jeremy commit messages. When done, list your changed files under 'Ready for sign-off' in SYNC.md and tell him to check with the main project.
Main project only: you are the only project that gives Jeremy commit messages. Review everything under 'Ready for sign-off' first.
```
