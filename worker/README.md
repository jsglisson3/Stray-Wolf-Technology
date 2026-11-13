# Site Notes service

A Cloudflare Worker (`site-notes`, https://site-notes.jsglisson.workers.dev). It sits between the client portals
and the admin page: it checks passwords, keeps logins, stores notes and pictures, keeps invoices, and fetches a
few headline numbers from Google Analytics.

| File | What it is |
|---|---|
| `worker.js` | The whole service, one file with no imports, so it can be pasted into the Cloudflare editor. **This file is the record of what is live.** |
| `test-worker.mjs` | Tests: runs the Worker in Node against an in-memory KV and a fake Google. `node worker/test-worker.mjs` (Node 20+). |
| `fakekv.mjs` | The in-memory KV the tests use. |

## Deploy

There is no build step.

1. Change `worker.js`, set `VERSION` at the top to the next letter (`2026-11-13k` → `2026-11-13l`; first change on a new day is `YYYY-MM-DDa`). Take the letter from `SYNC.md`, so two changes never share one.
2. Run `node worker/test-worker.mjs`. Everything must pass.
3. Cloudflare → Workers & Pages → `site-notes` → Edit code → select all, paste → **Deploy** (Save alone doesn't publish).
4. Open https://site-notes.jsglisson.workers.dev/api/check?site=tvis-construction and confirm `version` shows the new letter.
5. Commit `worker.js` the same day, and update the Worker line in `SYNC.md`.

Rollback: Cloudflare → `site-notes` → Deployments → pick the previous one → Rollback.

## Settings (Cloudflare dashboard)

| Name | Kind | What it does |
|---|---|---|
| `NOTES` | KV binding (namespace `site-notes`) | All storage. |
| `ADMIN_PASSWORD` | Secret | The admin login. Changing it logs the admin out everywhere. |
| `GA_SA_JSON` | Secret, optional | The Google service account key file (whole JSON). Only needed for analytics. The account needs Viewer on each GA4 property. |
| `ADMIN_ORIGINS` | Variable, optional | Web addresses allowed to call `/api/admin/*`, space separated. Default `https://straywolftech.com https://www.straywolftech.com`. |

## Routes

Every answer is JSON (`{ ok: true, ... }` or `{ ok: false, error }`) unless it is a picture.
Logged-in calls send `Authorization: Bearer <login key>`.

**Public**

| Method | Path | What it does |
|---|---|---|
| GET | `/api` | Says the service is running and its `version`. |
| GET | `/api/check?site=<name>` | Setup check, yes/no only (never IDs or keys). `&test=1` times the Google sign-in and the headline reports, at most once a minute per site. |

**Client** (any origin; the login key is the only credential)

| Method | Path | What it does |
|---|---|---|
| POST | `/api/login` | `{site, password}` → login key. Lockout after 8 wrong tries from one IP or 20 for one login, for 15 minutes. |
| POST | `/api/logout` | Ends this login on the server. |
| POST | `/api/pic` | One picture as the raw body (JPG, PNG or WebP, checked by its first bytes, 3 MB max) → its key. |
| POST | `/api/notes` | One batch of notes (text, pictures, captions, where on the page, snapshot). |
| POST | `/api/stats` | Headline Google Analytics numbers for the client's own site. |
| POST | `/api/my-photos` | The client's photos, newest first, each marked on the website or not. |
| POST | `/api/my-photo` | `{key}` → one of the client's own pictures. |

**Admin** (only from `ADMIN_ORIGINS`; everything except login needs an admin login)

| Method | Path | What it does |
|---|---|---|
| POST | `/api/admin/login`, `/api/admin/logout` | Admin login and logout. |
| GET | `/api/admin/data` | Everything for the admin page: clients, batches, invoices. |
| GET | `/api/admin/pic?key=` | A stored picture. |
| POST | `/api/admin/client` | Create or update a client (name, url, password, contacts). A new password logs that client out everywhere. |
| POST | `/api/admin/client/delete` | Delete a client and its logins. |
| POST | `/api/admin/done` | Tick a note done or not done. |
| POST | `/api/admin/pic-used` | Mark one of a note's pictures as on the client's website. |
| POST | `/api/admin/batch/delete` | Delete a batch and its pictures. |
| POST | `/api/admin/stats` | Headline numbers for any site. |
| POST | `/api/admin/invoice`, `/api/admin/invoice/delete` | Save or delete an invoice. |

## Logins

Logging in returns a random key. Only its SHA-256 is stored (`sess:{hash}`), so the stored list can't be used to log in.

| | Ends after no use for | Ends after login, at most |
|---|---|---|
| Admin | 30 minutes | 8 hours |
| Client | 2 hours | 24 hours |

A login also ends on Log out, and when the password changes. "Last used" is saved at most every 5 minutes to keep KV writes low.

## KV keys

| Key | Holds | Expires |
|---|---|---|
| `client:{site}` | `{site, name, url, password, created, pwAt, contacts[]}` | never |
| `batch:{id}` | One send from a client: `{id, site, at, notes[]}`. Each note: `n, page, title, on, text, pics[], picNotes[], done, url, sel, path, fx, fy, py, snip, vw, shot, onSite[]` | never |
| `pic:{site}:{id}` | Picture bytes (type in metadata) | deleted with its batch |
| `sess:{hash}` | `{k: "a"/"c", s: site, at, seen, v: password version}` | when unused |
| `fail:{ip}`, `fail:acct:{site}` | Wrong-password counters | 15 minutes |
| `ga:{site}` | That site's GA4 property ID, typed in by hand | never |
| `stats:{site}` | Last numbers from Google | 6 hours |
| `statslast:{site}` | Last good numbers, shown marked stale if Google fails | until replaced |
| `gatoken` | Google access token | 50 minutes |
| `gaerr:{site}` | Last Google problem, shown on `/api/check` | 1 day |
| `gatest:{site}` | "Tested less than a minute ago" lock for `&test=` | 1 minute |
| `inv:{number}` | One invoice, for example `inv:SW-0002` | never |

Site short names in use: `tvis-construction`, `friends-of-the-colony-public-library`, `stray-wolf` (this site, shown in the admin as "Your website").

## Google Analytics numbers

For each site: visitors, phone call taps (`phone_call_click`), form requests (`generate_lead`) and where people came from,
for the last 28 days and the 28 before, plus a daily series and the top pages. The reports run one after another,
each with its own time limit and one retry. The answer is cached 6 hours, so Google is asked at most 4 times a day
per site, and the portal and the admin share it. If Google fails, the last good numbers are shown, marked stale.

## Versions

| Version | What changed |
|---|---|
| 2026-11-13k | `/api/check` `&test=3` probes which Google calls answer from Cloudflare. **Live.** |
| 2026-11-13j | Google reports asked one at a time, each with its own time limit and one retry; timings on the check page. |
| 2026-11-13i | Server-side logins with time limits and real log out, per-login lockout, picture type checks, admin answers only its own origin, invoices. |
| 2026-11-13h | Logins and security (merged into 13i; the other 13h, with invoices, was never live). |
| 2026-11-13g | Batched Google reports, time limits, stale fallback. |
| 2026-11-13f | Which photos are on the client's site (`pic-used`, `my-photos`, `my-photo`). |
| 2026-11-13e | Snapshot of the spot where a note was left. |
| 2026-11-13d | Where on the page each note was left. |
| 2026-11-13c | Daily series and top pages. |
| 2026-11-13b | Contacts, Google Analytics numbers, photo captions, `/api/check`. |
