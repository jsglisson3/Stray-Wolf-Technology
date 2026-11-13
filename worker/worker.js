/*
 * Site Notes service  ·  Stray Wolf Technology
 * A Cloudflare Worker. Checks passwords, stores client notes and pictures,
 * and hands them to the admin page.
 *
 * Needs (set in the Cloudflare dashboard):
 *   - a KV namespace bound as  NOTES
 *   - a secret named           ADMIN_PASSWORD   (changing it logs the admin out everywhere)
 *   - (optional) a secret named GA_SA_JSON: the Google service account key file
 *     (the whole JSON). Only needed for the Google Analytics numbers.
 *   - (optional) a variable named ADMIN_ORIGINS: the web addresses allowed to use the admin
 *     side, separated by spaces. Default: https://straywolftech.com https://www.straywolftech.com
 *
 * Logins (sessions)
 *   Logging in hands back a random login key. Only its fingerprint (SHA-256) is stored, as
 *   sess:{fingerprint}, so the stored list can't be used to log in. A login ends when:
 *     - it's been unused for a while   (admin 30 minutes, clients 2 hours)
 *     - it's simply too old            (admin 8 hours, clients 24 hours)
 *     - Log out is pressed             (the service deletes it)
 *     - the password changes           (admin: the ADMIN_PASSWORD secret; client: a new
 *                                       password in the admin, or the client is deleted)
 *   Login keys from before this version are no longer accepted: everyone logs in once more.
 *
 * KV keys
 *   client:{site}        {site, name, url, password, created, pwAt?, contacts:[{name, role, phone, email, note}]}
 *                        pwAt = when the password was last set (older logins for that client stop working)
 *   batch:{id}           {id, site, at, notes:[{n, page, title, on, text, pics:[key], picNotes?:[caption], done,
 *                          url?, sel?, path?, fx?, fy?, py?, snip?, vw?,   (where on the page it was left)
 *                          shot?,                                         (pic key of a small snapshot of that spot)
 *                          onSite?:[key]}]}                               (which of its pics Stray Wolf put on the website)
 *   pic:{site}:{id}      picture bytes (type in metadata). Uploaded one at a time,
 *                        as raw files, so the free plan's small CPU budget is never a problem.
 *   sess:{fingerprint}   {k: "a" admin | "c" client, s: site, at: logged in, seen: last used, v: password version}
 *                        expires by itself when unused (KV expirationTtl)
 *   fail:{ip}            failed-login counter for one place, expires after 15 minutes
 *   fail:acct:{site}     failed-login counter for one login (fail:acct:admin for the admin), 15 minutes
 *   ga:{site}            that site's GA4 property ID, typed in by hand (for example 512345678)
 *   stats:{site}         the last Google Analytics numbers, kept 6 hours
 *   statslast:{site}     the last good numbers, kept until replaced (shown, marked stale, if Google has a problem)
 *   gatoken              the short-lived Google access token, kept 50 minutes
 *   gaerr:{site}         the last problem Google Analytics reported for that site, kept 1 day (shown on /api/check)
 *   inv:{number}         one invoice, for example inv:SW-0002 (see cleanInvoice for its fields)
 */

const VERSION = "2026-11-13i (contacts, analytics with each day and top pages, captions, where each note was left, snapshot of the spot, which photos are on the site, invoices; server-side logins with time limits and a real log out, per-login lockout, picture checks, admin answers only its own page)";
const LIMITS = { notes: 40, text: 2000, label: 300, caption: 140, pics: 20, picBytes: 3 * 1024 * 1024, contacts: 25, jsonBytes: 256 * 1024 };
const PIC_TYPES = { "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp" };
const PIC_KEY = /^pic:[a-z0-9-]+:[\w-]+$/;
const SITE_ID = /^[a-z0-9][a-z0-9-]{1,39}$/;
// How long a login lasts, in minutes. idle: unused this long = logged out. max: logged out this long after logging in.
// The admin page and the client portal use the same numbers to log out on screen.
const SESSION = { a: { idle: 30, max: 8 * 60 }, c: { idle: 2 * 60, max: 24 * 60 } };
const TOUCH_MIN = 5;                    // "last used" is saved at most every 5 minutes (keeps KV writes low)
const MAX_FAILS = 8, MAX_ACCOUNT_FAILS = 20, FAIL_SECONDS = 900;
const DEFAULT_ADMIN_ORIGINS = ["https://straywolftech.com", "https://www.straywolftech.com"];

/* ---------- responses ---------- */

// Every answer: no sniffing, never framed, no referrer, nothing runs if one is opened directly.
const SAFE = {
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
  "x-frame-options": "DENY",
  "content-security-policy": "default-src 'none'; frame-ancestors 'none'; sandbox",
  "cross-origin-resource-policy": "cross-origin",
};
// CORS. The client side is used from each client's own website, so any site may call it: there are
// no cookies, and every call needs the login key in the Authorization header, so another site
// can't act for a logged-in client. The admin side only answers the admin page's own address.
function corsFor(req, env, path) {
  const base = { "access-control-allow-methods": "GET, POST, OPTIONS", "access-control-allow-headers": "authorization, content-type", "access-control-max-age": "86400" };
  if (!path.startsWith("/api/admin/")) return { ...base, "access-control-allow-origin": "*" };
  const allowed = env.ADMIN_ORIGINS ? String(env.ADMIN_ORIGINS).split(/[\s,]+/).filter(Boolean) : DEFAULT_ADMIN_ORIGINS;
  const origin = req.headers.get("origin") || "";
  return allowed.includes(origin) ? { ...base, "access-control-allow-origin": origin, vary: "Origin" } : { vary: "Origin" };
}
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...SAFE, "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const fail = (status, error) => json({ ok: false, error }, status);

/* ---------- small helpers ---------- */

const enc = new TextEncoder();
const b64url = (bytes) => btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const str = (v, max) => String(v == null ? "" : v).replace(/\u0000/g, "").trim().slice(0, max);
const sha = async (text) => b64url(await crypto.subtle.digest("SHA-256", enc.encode(text)));

async function hmac(env, text) {
  const key = await crypto.subtle.importKey("raw", enc.encode("site-notes|" + env.ADMIN_PASSWORD), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64url(await crypto.subtle.sign("HMAC", key, enc.encode(text)));
}
// Compare without leaking where the strings differ.
function same(a, b) {
  a = String(a); b = String(b);
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}
// JSON bodies are small; anything bigger than LIMITS.jsonBytes is refused before it's read.
async function body(req) {
  if (Number(req.headers.get("content-length")) > LIMITS.jsonBytes) return null;
  try { const t = await req.text(); return t.length > LIMITS.jsonBytes ? null : JSON.parse(t); } catch { return null; }
}

/* ---------- logins (sessions) ---------- */

// Which version of the password a login belongs to. Admin: tied to the ADMIN_PASSWORD secret.
// Client: the time their password was last set.
const adminVersion = (env) => hmac(env, "admin-session");
const clientVersion = (client) => String(client.pwAt || client.created || "");
const bearer = (req) => { const m = (req.headers.get("authorization") || "").match(/^Bearer\s+([\w-]{43})$/); return m ? m[1] : null; };

async function startSession(env, kind, site, v) {
  const token = b64url(crypto.getRandomValues(new Uint8Array(32))), now = Date.now();
  await env.NOTES.put("sess:" + (await sha(token)), JSON.stringify({ k: kind, s: site, at: now, seen: now, v }), { expirationTtl: SESSION[kind].idle * 60 });
  return token;
}
// The login behind this request, or null. Checks the time limits and the password version, and
// pushes the "unused" limit back (saving at most every TOUCH_MIN minutes).
async function readSession(env, req, kind) {
  const token = bearer(req); if (!token) return null;
  const key = "sess:" + (await sha(token)), s = await env.NOTES.get(key, "json");
  const lim = SESSION[kind], now = Date.now();
  if (!s || s.k !== kind) return null;
  if (now - s.seen >= lim.idle * 6e4 || now - s.at >= lim.max * 6e4) { await env.NOTES.delete(key); return null; }
  let client = null;
  if (kind === "a") { if (!same(s.v, await adminVersion(env))) { await env.NOTES.delete(key); return null; } }
  else {
    client = await env.NOTES.get("client:" + s.s, "json");
    if (!client || !same(s.v, clientVersion(client))) { await env.NOTES.delete(key); return null; }
  }
  if (now - s.seen >= TOUCH_MIN * 6e4) {
    s.seen = now;
    // never past the hard limit: the stored copy disappears by itself at whichever comes first
    const ttl = Math.max(60, Math.min(lim.idle * 60, Math.floor((s.at + lim.max * 6e4 - now) / 1000)));
    await env.NOTES.put(key, JSON.stringify(s), { expirationTtl: ttl });
  }
  return { k: s.k, s: s.s, client };
}
async function endSession(env, req) {
  const token = bearer(req);
  if (token) await env.NOTES.delete("sess:" + (await sha(token)));
  return json({ ok: true });
}

/* ---------- wrong passwords ---------- */
// Two counters, both forgotten after 15 minutes: one per place (IP address, 8 tries) and one per
// login (20 tries, so guessing one password from many places is stopped too).

async function tooManyFails(env, ip, acct) {
  const [a, b] = await Promise.all([env.NOTES.get("fail:" + ip), env.NOTES.get("fail:acct:" + acct)]);
  return Number(a) >= MAX_FAILS || Number(b) >= MAX_ACCOUNT_FAILS;
}
async function countFail(env, ip, acct) {
  const [a, b] = await Promise.all([env.NOTES.get("fail:" + ip), env.NOTES.get("fail:acct:" + acct)]);
  await Promise.all([
    env.NOTES.put("fail:" + ip, String((Number(a) || 0) + 1), { expirationTtl: FAIL_SECONDS }),
    env.NOTES.put("fail:acct:" + acct, String((Number(b) || 0) + 1), { expirationTtl: FAIL_SECONDS }),
  ]);
}
// a right password clears the wrong tries from that place and for that login
async function clearFails(env, ip, acct) {
  for (const k of ["fail:" + ip, "fail:acct:" + acct]) if (await env.NOTES.get(k) !== null) await env.NOTES.delete(k);
}
async function listKeys(env, prefix) {
  const names = []; let cursor;
  do {
    const page = await env.NOTES.list({ prefix, cursor });
    page.keys.forEach((k) => names.push(k.name));
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor && names.length < 2000);
  return names;
}

/* ---------- client side ---------- */

async function clientLogin(req, env) {
  const ip = req.headers.get("cf-connecting-ip") || "unknown";
  const d = await body(req); if (!d) return fail(400, "Bad request.");
  const site = str(d.site, 40).toLowerCase();
  if (!SITE_ID.test(site)) return fail(401, "That password isn't right.");
  if (await tooManyFails(env, ip, site)) return fail(429, "Too many tries. Please wait 15 minutes.");
  const client = await env.NOTES.get("client:" + site, "json");
  const ok = same(client ? client.password : "\u0000no-such-client", str(d.password, 100));
  if (!client || !ok) {
    await countFail(env, ip, site);
    return fail(401, "That password isn't right.");
  }
  await clearFails(env, ip, site);
  return json({ ok: true, name: client.name, token: await startSession(env, "c", site, clientVersion(client)),
    idleMinutes: SESSION.c.idle, maxMinutes: SESSION.c.max });
}

async function saveNotes(req, env) {
  const who = await readSession(env, req, "c");
  if (!who) return fail(401, "Please log in again.");
  const d = await body(req);
  if (!d || !Array.isArray(d.notes) || !d.notes.length) return fail(400, "There are no notes to send.");
  if (d.notes.length > LIMITS.notes) return fail(400, "That's too many notes for one send. Please send " + LIMITS.notes + " or fewer.");

  const id = Date.now() + "-" + b64url(crypto.getRandomValues(new Uint8Array(6)));
  const notes = []; let pictures = 0;
  for (const [i, raw0] of d.notes.entries()) {
    const raw = raw0 && typeof raw0 === "object" ? raw0 : {};
    const note = { n: i + 1, page: str(raw.page, 200), title: str(raw.title, LIMITS.label), on: str(raw.on, LIMITS.label), text: str(raw.text, LIMITS.text), pics: [], done: false };
    const rawPics = Array.isArray(raw.pics) ? raw.pics : [];
    // Optional words for each picture ("What is this?"), in the same order as pics. "" = none.
    if (Array.isArray(raw.picNotes)) {
      const caps = rawPics.map((_, k) => str(raw.picNotes[k], LIMITS.caption));
      if (caps.some(Boolean)) note.picNotes = caps;
    }
    Object.assign(note, cleanWhere(raw));
    // A small snapshot of the spot, uploaded first like a photo. Optional: a bad one is dropped, never blocks the send.
    if (typeof raw.shot === "string" && raw.shot.length <= 200 && PIC_KEY.test(raw.shot) && raw.shot.startsWith("pic:" + who.s + ":")) note.shot = raw.shot;
    for (const key of rawPics) {
      // Pictures were uploaded first (POST /api/pic). A client may only attach their own.
      if (typeof key !== "string" || !PIC_KEY.test(key) || !key.startsWith("pic:" + who.s + ":")) return fail(400, "One of the pictures couldn't be attached. Please add it again.");
      if (++pictures > LIMITS.pics) return fail(400, "That's too many pictures for one send. Please send " + LIMITS.pics + " or fewer.");
      note.pics.push(key);
    }
    if (note.text || note.pics.length) notes.push(note);
  }
  if (!notes.length) return fail(400, "There are no notes to send.");

  await env.NOTES.put("batch:" + id, JSON.stringify({ id, site: who.s, at: new Date().toISOString(), notes }));
  return json({ ok: true, id, notes: notes.length, pictures });
}

// Where on the page a note was left, so the admin can say "Home page, near the top, on a phone"
// and open the page with that exact spot highlighted (#sw-find=). Anything odd is dropped.
function cleanWhere(raw) {
  const out = {}, frac = (v) => (typeof v === "number" && isFinite(v) ? Math.round(Math.min(1, Math.max(0, v)) * 1000) / 1000 : undefined);
  const url = str(raw.url, 300); if (/^https?:\/\/[^\s]+$/i.test(url)) out.url = url;
  const sel = str(raw.sel, 300); if (sel) out.sel = sel;
  if (Array.isArray(raw.path) && raw.path.length && raw.path.length <= 40 && raw.path.every((n) => Number.isInteger(n) && n >= 0 && n < 5000)) out.path = raw.path;
  for (const k of ["fx", "fy", "py"]) { const v = frac(raw[k]); if (v !== undefined) out[k] = v; }
  const snip = str(raw.snip, 160); if (snip) out.snip = snip;
  if (Number.isInteger(raw.vw) && raw.vw >= 200 && raw.vw <= 10000) out.vw = raw.vw;
  return out;
}

// Is it really the kind of picture it says it is? (The first bytes of every JPG, PNG and WebP are fixed.)
function looksLike(type, b) {
  if (type === "image/jpeg") return b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff;
  if (type === "image/png") return [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a].every((x, i) => b[i] === x);
  if (type === "image/webp") return String.fromCharCode(...b.slice(0, 4)) === "RIFF" && String.fromCharCode(...b.slice(8, 12)) === "WEBP";
  return false;
}

// One picture per request, sent as the raw file. Stored as-is: no decoding, almost no CPU.
// (Picture storage lives in this one function and adminPic, so it can move elsewhere later.)
async function savePic(req, env) {
  const who = await readSession(env, req, "c");
  if (!who) return fail(401, "Please log in again.");
  const type = (req.headers.get("content-type") || "").split(";")[0].trim().toLowerCase();
  if (!PIC_TYPES[type]) return fail(400, "That picture isn't a JPG, PNG or WebP.");
  if (Number(req.headers.get("content-length")) > LIMITS.picBytes) return fail(413, "That picture is too big.");
  const bytes = await req.arrayBuffer();
  if (!bytes.byteLength) return fail(400, "That picture is empty.");
  if (bytes.byteLength > LIMITS.picBytes) return fail(413, "That picture is too big.");
  if (!looksLike(type, new Uint8Array(bytes, 0, Math.min(12, bytes.byteLength)))) return fail(400, "That picture isn't a JPG, PNG or WebP.");
  const key = "pic:" + who.s + ":" + Date.now() + "-" + b64url(crypto.getRandomValues(new Uint8Array(6)));
  await env.NOTES.put(key, bytes, { metadata: { type } });
  return json({ ok: true, key });
}

// The client's own photos, newest first, and whether each one is on their website yet.
async function myPhotos(req, env) {
  const who = await readSession(env, req, "c");
  if (!who) return fail(401, "Please log in again.");
  const keys = (await listKeys(env, "batch:")).sort().reverse().slice(0, 300);   // ids start with the time: newest first
  const batches = (await Promise.all(keys.map((k) => env.NOTES.get(k, "json")))).filter((b) => b && b.site === who.s);
  const photos = [], seen = new Set();
  for (const b of batches) for (const n of b.notes) (n.pics || []).forEach((key, k) => {
    if (photos.length >= 60 || seen.has(key)) return;
    seen.add(key);
    photos.push({ key, at: b.at, caption: (n.picNotes && n.picNotes[k]) || "", used: !!(n.onSite && n.onSite.includes(key)) });
  });
  return json({ ok: true, photos });
}

// A stored picture, as a download-safe response (served as its own type, never run as a page).
function picResponse(key, value, metadata) {
  const type = (metadata && PIC_TYPES[metadata.type] && metadata.type) || "image/jpeg";
  return new Response(value, { headers: { ...SAFE, "content-type": type, "cache-control": "private, max-age=3600",
    "content-disposition": 'inline; filename="' + key.replace(/[^\w-]/g, "-") + "." + PIC_TYPES[type] + '"' } });
}

// One of the client's own pictures (only their own).
async function myPhoto(req, env) {
  const who = await readSession(env, req, "c");
  if (!who) return fail(401, "Please log in again.");
  const d = await body(req), key = d ? str(d.key, 200) : "";
  if (!PIC_KEY.test(key) || !key.startsWith("pic:" + who.s + ":")) return fail(404, "That picture is gone.");
  const { value, metadata } = await env.NOTES.getWithMetadata(key, "arrayBuffer");
  if (!value) return fail(404, "That picture is gone.");
  return picResponse(key, value, metadata);
}

/* ---------- admin side ---------- */

async function adminLogin(req, env) {
  const ip = req.headers.get("cf-connecting-ip") || "unknown";
  if (await tooManyFails(env, ip, "admin")) return fail(429, "Too many tries. Please wait 15 minutes.");
  const d = await body(req);
  if (!d || !same(env.ADMIN_PASSWORD, str(d.password, 200))) { await countFail(env, ip, "admin"); return fail(401, "That password isn't right."); }
  await clearFails(env, ip, "admin");
  return json({ ok: true, token: await startSession(env, "a", "", await adminVersion(env)), idleMinutes: SESSION.a.idle, maxMinutes: SESSION.a.max });
}

async function adminData(env) {
  const [clientKeys, batchKeys] = await Promise.all([listKeys(env, "client:"), listKeys(env, "batch:")]);
  const recent = batchKeys.sort().reverse().slice(0, 300);          // ids start with the time, so this is newest first
  const [clients, batches] = await Promise.all([
    Promise.all(clientKeys.map((k) => env.NOTES.get(k, "json"))),
    Promise.all(recent.map((k) => env.NOTES.get(k, "json"))),
  ]);
  const invoices = (await Promise.all((await listKeys(env, "inv:")).map((k) => env.NOTES.get(k, "json")))).filter(Boolean);
  return json({ ok: true, clients: clients.filter(Boolean).sort((a, b) => a.name.localeCompare(b.name)), batches: batches.filter(Boolean), invoices });
}

// A website address the admin types: "tvisconstruction.com" or "https://example.github.io/Site/".
const SITE_URL = /^(https?:\/\/)?[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+(:\d{2,5})?(\/[^\s"'<>]*)?$/i;

async function adminClient(req, env) {
  const d = await body(req); if (!d) return fail(400, "Bad request.");
  const site = str(d.site, 40).toLowerCase();
  if (!SITE_ID.test(site)) return fail(400, "The short name can only use lowercase letters, numbers and dashes.");
  const url = str(d.url, 200);
  if (url && !SITE_URL.test(url)) return fail(400, "That website address doesn't look right. Type it like tvisconstruction.com.");
  const old = await env.NOTES.get("client:" + site, "json");
  const newPw = str(d.password, 100);
  const client = {
    site,
    name: str(d.name, 100) || (old && old.name) || site,
    url: url || (old && old.url) || "",
    password: newPw || (old && old.password) || "",
    created: (old && old.created) || new Date().toISOString(),
    // People at this client (admin Contacts tab). Sent only when the list changes; otherwise kept.
    contacts: Array.isArray(d.contacts) ? cleanContacts(d.contacts) : (old && Array.isArray(old.contacts) ? old.contacts : []),
  };
  if (client.password.length < 6) return fail(400, "The password needs at least 6 characters.");
  // A new password logs that client out everywhere; anything else leaves their logins alone.
  if (old && newPw && newPw !== old.password) client.pwAt = new Date().toISOString();
  else if (old && old.pwAt) client.pwAt = old.pwAt;
  await env.NOTES.put("client:" + site, JSON.stringify(client));
  return json({ ok: true, client });
}

function cleanContacts(list) {
  return list.slice(0, LIMITS.contacts).filter((p) => p && typeof p === "object").map((p) => ({
    name: str(p.name, 80), role: str(p.role, 80), phone: str(p.phone, 40), email: str(p.email, 120), note: str(p.note, 300),
  })).filter((p) => p.name);
}

async function adminClientDelete(req, env) {
  const d = await body(req); if (!d) return fail(400, "Bad request.");
  await env.NOTES.delete("client:" + str(d.site, 40).toLowerCase());   // their past requests are kept; their logins stop working
  return json({ ok: true });
}

async function adminDone(req, env) {
  const d = await body(req); if (!d) return fail(400, "Bad request.");
  const key = "batch:" + str(d.batch, 60), batch = await env.NOTES.get(key, "json");
  if (!batch) return fail(404, "That request is gone.");
  const note = batch.notes.find((x) => x.n === Number(d.n));
  if (!note) return fail(404, "That note is gone.");
  note.done = !!d.done;
  await env.NOTES.put(key, JSON.stringify(batch));
  return json({ ok: true });
}

// Mark one of a note's pictures as on the client's website (or not). Kept on the note as onSite, in pics order.
async function adminPicUsed(req, env) {
  const d = await body(req); if (!d) return fail(400, "Bad request.");
  const key = "batch:" + str(d.batch, 60), batch = await env.NOTES.get(key, "json");
  if (!batch) return fail(404, "That request is gone.");
  const note = batch.notes.find((x) => x.n === Number(d.n));
  if (!note) return fail(404, "That note is gone.");
  const pic = str(d.key, 200);
  if (!note.pics.includes(pic)) return fail(404, "That picture is gone.");
  const on = new Set(note.onSite || []);
  if (d.used) on.add(pic); else on.delete(pic);
  note.onSite = note.pics.filter((p) => on.has(p));
  if (!note.onSite.length) delete note.onSite;
  await env.NOTES.put(key, JSON.stringify(batch));
  return json({ ok: true });
}

async function adminBatchDelete(req, env) {
  const d = await body(req); if (!d) return fail(400, "Bad request.");
  const key = "batch:" + str(d.batch, 60), batch = await env.NOTES.get(key, "json");
  if (batch) for (const n of batch.notes) for (const p of n.shot ? n.pics.concat(n.shot) : n.pics) if (PIC_KEY.test(p)) await env.NOTES.delete(p);
  await env.NOTES.delete(key);
  return json({ ok: true });
}

async function adminPic(url, env) {
  const key = url.searchParams.get("key") || "";
  if (!PIC_KEY.test(key)) return fail(400, "Bad picture.");
  const { value, metadata } = await env.NOTES.getWithMetadata(key, "arrayBuffer");
  if (!value) return fail(404, "That picture is gone.");
  return picResponse(key, value, metadata);
}

/* ---------- Google Analytics headline numbers ---------- */
// A few numbers for the client's portal card and the admin Analytics tab:
// visitors, phone taps, form requests, and where most people came from, for the
// last 28 days compared with the 28 before. Not a replacement for GA4 itself.
// Each site needs  ga:{site}  in KV (its GA4 property ID), and the service needs
// the GA_SA_JSON secret. The answer is kept 6 hours, so Google is asked at most
// 4 times a day per site, and the portal and the admin share that answer.

const GA = { days: 28, cacheSeconds: 6 * 3600, events: { calls: "phone_call_click", leads: "generate_lead" },
  // the time zone the GA4 properties report in, used only to line up the "each day" numbers
  tz: "America/Chicago" };

async function statsFor(site, env) {
  const ga = await gaSetup(site, env);
  if (!ga.saved) return fail(404, "No Google Analytics set up for this site.");
  if (!ga.property) return fail(400, ga.problem);
  const property = ga.property;
  if (!env.GA_SA_JSON) return fail(503, "Google Analytics isn't connected to the notes service yet.");

  const cached = await env.NOTES.get("stats:" + site, "json");
  if (cached && cached.property === property && "daily" in cached) return json(cached);

  let token;
  try { token = await googleToken(env); }
  catch (e) { await gaProblem(env, site, "sign-in", e); return fail(502, "Couldn't sign in to Google Analytics. Check the GA_SA_JSON secret."); }
  try {
    const ranges = [
      { startDate: GA.days + "daysAgo", endDate: "yesterday" },
      { startDate: (GA.days * 2) + "daysAgo", endDate: (GA.days + 1) + "daysAgo" },
    ];
    const eventFilter = { filter: { fieldName: "eventName", inListFilter: { values: [GA.events.calls, GA.events.leads] } } };
    // The headline numbers: three small reports, the same way that worked from the start.
    const [users, events, sources] = await Promise.all([
      runReport(property, token, { dateRanges: ranges, metrics: [{ name: "activeUsers" }] }, 15000),
      // the names the site sends: tapping a phone number, and sending the estimate form
      runReport(property, token, { dateRanges: ranges, dimensions: [{ name: "eventName" }], metrics: [{ name: "eventCount" }], dimensionFilter: eventFilter }, 15000),
      runReport(property, token, { dateRanges: [ranges[0]], dimensions: [{ name: "sessionSource" }], metrics: [{ name: "sessions" }], orderBys: [{ metric: { metricName: "sessions" }, desc: true }], limit: 5 }, 15000),
    ]);
    // The extras (each day, top pages) come after, with a shorter wait. If they fail, the numbers still show.
    let extraErr = null;
    const extra = (q) => runReport(property, token, q, 8000).catch((e) => { extraErr = extraErr || e; return null; });
    const [dayUsers, dayEvents, pages] = await Promise.all([
      // each day of the last 28: visitors, and phone taps + form sends
      extra({ dateRanges: [ranges[0]], dimensions: [{ name: "date" }], metrics: [{ name: "activeUsers" }], limit: 100 }),
      extra({ dateRanges: [ranges[0]], dimensions: [{ name: "date" }, { name: "eventName" }], metrics: [{ name: "eventCount" }], dimensionFilter: eventFilter, limit: 500 }),
      // the pages people opened most
      extra({ dateRanges: [ranges[0]], dimensions: [{ name: "pagePath" }, { name: "pageTitle" }], metrics: [{ name: "screenPageViews" }], orderBys: [{ metric: { metricName: "screenPageViews" }, desc: true }], limit: 15 }),
    ]);
    const v = gaPick(users), c = gaPick(events, GA.events.calls), l = gaPick(events, GA.events.leads);
    const answer = {
      ok: true, days: GA.days, property,
      visitors: v[0], visitorsChange: gaChange(v), visitorsPrev: v[1],
      calls: c[0], callsChange: gaChange(c), callsPrev: c[1],
      leads: l[0], leadsChange: gaChange(l), leadsPrev: l[1],
      source: friendlySource(sources),
      daily: gaTry(() => (dayUsers && dayEvents ? gaDaily(dayUsers, dayEvents) : null), (e) => { extraErr = extraErr || e; }),
      pages: gaTry(() => (pages ? gaPages(pages) : null), (e) => { extraErr = extraErr || e; }),
      at: new Date().toISOString(),
    };
    // if the extras failed, try them again sooner (30 minutes) instead of waiting 6 hours
    await env.NOTES.put("stats:" + site, JSON.stringify(answer), { expirationTtl: extraErr ? 1800 : GA.cacheSeconds });
    await env.NOTES.put("statslast:" + site, JSON.stringify(answer));   // kept, in case Google has a bad moment later
    if (extraErr) await gaProblem(env, site, "each day / top pages", extraErr);
    else await env.NOTES.delete("gaerr:" + site);
    return json(answer);
  } catch (e) {
    if (e && e.status === 401) await env.NOTES.delete("gatoken");
    await gaProblem(env, site, "headline numbers", e);
    // Google had a problem: show the last numbers we got rather than nothing (marked stale), unless access was taken away.
    const last = e && e.status === 403 ? null : await env.NOTES.get("statslast:" + site, "json");
    if (last && last.property === property) return json({ ...last, stale: true });
    return fail(502, e && e.status === 403
      ? "Google Analytics said no. Add the service account as a Viewer on this site's GA4 property."
      : "Couldn't get the Google Analytics numbers" + (e && e.status ? " (Google said " + e.status + ")" : "") + ". Try again in a minute.");
  }
}

function gaTry(fn, onErr) { try { return fn(); } catch (e) { onErr(e); return null; } }

// Remember what went wrong, so /api/check can show it (no keys or IDs, just Google's words).
async function gaProblem(env, site, what, e) {
  const p = { at: new Date().toISOString(), what, status: (e && e.status) || 0, said: str((e && (e.detail || e.message)) || "unknown", 300) };
  try { await env.NOTES.put("gaerr:" + site, JSON.stringify(p), { expirationTtl: 86400 }); } catch {}
}

// Reads ga:{site} and forgives the usual slips: quotes, spaces, "properties/" in front.
async function gaSetup(site, env) {
  const raw = await env.NOTES.get("ga:" + site);
  if (raw == null || !String(raw).trim()) return { saved: false };
  const v = String(raw).trim().replace(/^["'\s]+|["'\s]+$/g, "").replace(/^properties\//i, "");
  if (/^\d{6,}$/.test(v)) return { saved: true, property: v };
  if (/^G-/i.test(v)) return { saved: true, problem: "ga:" + site + " holds the Measurement ID (G-...). It needs the Property ID instead: numbers only, from GA4 Admin > Property details." };
  return { saved: true, problem: "ga:" + site + " doesn't look like a GA4 Property ID. It should be numbers only, like 512345678." };
}

// Open in a browser to check the setup:  /api/check?site=tvis-construction
// Says only yes/no (never the ID or the key), so it is safe to leave public.
async function setupCheck(url, env) {
  const site = str(url.searchParams.get("site"), 40).toLowerCase();
  const out = { ok: true, version: VERSION, googleKeySaved: !!env.GA_SA_JSON };
  if (env.GA_SA_JSON) { try { const sa = JSON.parse(env.GA_SA_JSON); out.googleKeyLooksRight = !!(sa.client_email && sa.private_key); } catch { out.googleKeyLooksRight = false; } }
  if (site) {
    const ga = await gaSetup(site, env);
    out.site = site; out.propertyIdSaved = ga.saved; if (ga.saved) out.propertyIdLooksRight = !!ga.property;
    if (ga.problem) out.problem = ga.problem;
    out.numbersCached = (await env.NOTES.get("stats:" + site)) !== null;   // false just means nobody asked in the last 6 hours
    const prob = await env.NOTES.get("gaerr:" + site, "json");
    if (prob) out.lastGoogleProblem = prob;
    // &test=1 asks Google one tiny question right now and says how long it took (no numbers shown). Once a minute at most.
    if (url.searchParams.get("test") && ga.property && env.GA_SA_JSON) out.test = await gaTest(site, ga.property, env);
  }
  return json(out);
}

async function gaTest(site, property, env) {
  if (await env.NOTES.get("gatest:" + site)) return { skipped: "Tested less than a minute ago. Try again in a minute." };
  await env.NOTES.put("gatest:" + site, "1", { expirationTtl: 60 });
  const out = {}, t0 = Date.now();
  let token;
  try { await env.NOTES.delete("gatoken"); token = await googleToken(env); out.signIn = "ok"; }
  catch (e) { out.signIn = "failed: " + str(e && (e.detail || e.message), 200); }
  out.signInSeconds = (Date.now() - t0) / 1000;
  if (token) {
    const t1 = Date.now();
    try { await runReport(property, token, { dateRanges: [{ startDate: "7daysAgo", endDate: "yesterday" }], metrics: [{ name: "activeUsers" }] }, 20000); out.report = "ok"; }
    catch (e) { out.report = "failed" + (e && e.status ? " (" + e.status + ")" : "") + ": " + str(e && (e.detail || e.message), 200); }
    out.reportSeconds = (Date.now() - t1) / 1000;
  }
  return out;
}

// With two date ranges GA adds a "dateRange" dimension: date_range_0 = now, date_range_1 = before.
function gaPick(rep, match) {
  const out = [0, 0];
  for (const r of rep.rows || []) {
    const dims = (r.dimensionValues || []).map((d) => d.value);
    if (match && !dims.includes(match)) continue;
    out[dims.includes("date_range_1") ? 1 : 0] += Number(r.metricValues && r.metricValues[0] && r.metricValues[0].value) || 0;
  }
  return out;
}
// The 28 days GA means by "28daysAgo".."yesterday" (in the property's time zone), as YYYYMMDD.
function gaDays() {
  // today's date where the property reports (works whatever date style the runtime's Intl prefers)
  let y, m, d;
  try {
    const parts = {};
    for (const x of new Intl.DateTimeFormat("en-US", { timeZone: GA.tz, year: "numeric", month: "numeric", day: "numeric" }).formatToParts(new Date())) parts[x.type] = Number(x.value);
    y = parts.year; m = parts.month; d = parts.day;
  } catch {}
  if (!(y > 2000 && m >= 1 && m <= 12 && d >= 1 && d <= 31)) { const t = new Date(Date.now() - 6 * 3600e3); y = t.getUTCFullYear(); m = t.getUTCMonth() + 1; d = t.getUTCDate(); }
  const out = [];
  for (let i = GA.days; i >= 1; i--) out.push(new Date(Date.UTC(y, m - 1, d - i)).toISOString().slice(0, 10).replace(/-/g, ""));
  return out;
}
// One number per day (0 where GA has no row): { start: "2026-10-16", visitors: [...], calls: [...], leads: [...] }
function gaDaily(users, events) {
  const days = gaDays(), at = new Map(days.map((d, i) => [d, i])), z = () => days.map(() => 0);
  const out = { start: days[0].replace(/(\d{4})(\d{2})(\d{2})/, "$1-$2-$3"), visitors: z(), calls: z(), leads: z() };
  const val = (r) => Number(r.metricValues && r.metricValues[0] && r.metricValues[0].value) || 0;
  for (const r of users.rows || []) { const i = at.get(r.dimensionValues && r.dimensionValues[0] && r.dimensionValues[0].value); if (i != null) out.visitors[i] += val(r); }
  for (const r of events.rows || []) {
    const dims = (r.dimensionValues || []).map((d) => d.value), i = at.get(dims[0]);
    if (i == null) continue;
    if (dims[1] === GA.events.calls) out.calls[i] += val(r); else if (dims[1] === GA.events.leads) out.leads[i] += val(r);
  }
  return out;
}
// The top 3 pages: [{ path, title, views }], the same path's rows added together.
function gaPages(rep) {
  const by = new Map();
  for (const r of rep.rows || []) {
    const [path, title] = (r.dimensionValues || []).map((d) => d.value);
    if (!path || path === "(not set)") continue;
    const p = by.get(path) || { path: path.slice(0, 200), title: "", views: 0 };
    if (!p.title && title && title !== "(not set)") p.title = title.slice(0, 120);
    p.views += Number(r.metricValues && r.metricValues[0] && r.metricValues[0].value) || 0;
    by.set(path, p);
  }
  return [...by.values()].sort((a, b) => b.views - a.views).slice(0, 3);
}
const gaChange = ([now, before]) => (before ? Math.round(((now - before) / before) * 100) : 0);

// The top source in plain words ("Google", "Facebook", "Typed it in").
function friendlySource(rep) {
  const row = (rep.rows || []).find((r) => r.dimensionValues && r.dimensionValues[0] && r.dimensionValues[0].value !== "(not set)");
  if (!row) return "";
  const raw = row.dimensionValues[0].value, s = raw.toLowerCase();
  if (s.includes("facebook") || s === "fb") return "Facebook";
  if (s.includes("instagram") || s === "ig") return "Instagram";
  if (s.includes("google")) return "Google";
  if (s.includes("bing")) return "Bing";
  if (s.includes("yahoo")) return "Yahoo";
  if (s === "(direct)") return "Typed it in";
  return raw.slice(0, 60);
}

// A signal that stops a call to Google that takes too long.
function giveUpAfter(ms) { const c = new AbortController(); setTimeout(() => c.abort(new Error("Google took longer than " + Math.round(ms / 1000) + " seconds")), ms); return c.signal; }

// One report from Google. Gives up after a while, so the page never waits forever.
async function runReport(property, token, request, ms) {
  const r = await fetch("https://analyticsdata.googleapis.com/v1beta/properties/" + property + ":runReport", {
    method: "POST", headers: { authorization: "Bearer " + token, "content-type": "application/json" },
    body: JSON.stringify(request), signal: giveUpAfter(ms || 15000),
  });
  if (!r.ok) {
    const e = new Error("GA " + r.status); e.status = r.status;
    try { const j = await r.json(); e.detail = (j && j.error && j.error.message) || ""; } catch {}
    throw e;
  }
  return r.json();
}

// Service account -> short-lived Google access token (a signed JWT, RS256, using WebCrypto).
async function googleToken(env) {
  const hit = await env.NOTES.get("gatoken");
  if (hit) return hit;
  const sa = JSON.parse(env.GA_SA_JSON);
  const now = Math.floor(Date.now() / 1000);
  const part = (o) => b64url(enc.encode(JSON.stringify(o)));
  const unsigned = part({ alg: "RS256", typ: "JWT" }) + "." + part({
    iss: sa.client_email, scope: "https://www.googleapis.com/auth/analytics.readonly",
    aud: "https://oauth2.googleapis.com/token", iat: now, exp: now + 3600,
  });
  const pem = String(sa.private_key).replace(/-----[^-]+-----/g, "").replace(/\\n/g, "").replace(/\s+/g, "");
  const key = await crypto.subtle.importKey("pkcs8", Uint8Array.from(atob(pem), (ch) => ch.charCodeAt(0)),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const jwt = unsigned + "." + b64url(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(unsigned)));
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" },
    body: "grant_type=" + encodeURIComponent("urn:ietf:params:oauth:grant-type:jwt-bearer") + "&assertion=" + jwt,
    signal: giveUpAfter(12000),
  });
  const d = await r.json().catch(() => ({}));
  if (!d.access_token) throw new Error("no Google token");
  await env.NOTES.put("gatoken", d.access_token, { expirationTtl: 3000 });
  return d.access_token;
}

// Portal card: the client's own site only (taken from their login, not from what they send).
async function clientStats(req, env) {
  const who = await readSession(env, req, "c");
  if (!who) return fail(401, "Please log in again.");
  const r = await statsFor(who.s, env);
  if (!r.ok) return r;
  const d = await r.json(); delete d.property;
  return json(d);
}

// Admin Analytics tab: any site.
async function adminStats(req, env) {
  const d = await body(req); if (!d) return fail(400, "Bad request.");
  const site = str(d.site, 40).toLowerCase();
  if (!SITE_ID.test(site)) return fail(400, "Bad site.");
  return statsFor(site, env);
}

/* ---------- invoices ---------- */
// Numbers run SW-0002, SW-0003, ... (SW-0001 was made by hand before the admin could make invoices).
const INV = { first: 2, items: 40, bullets: 20, discounts: 10, support: 12 };
const INV_NO = /^SW-\d{4,6}$/;
const invNo = (n) => "SW-" + String(n).padStart(4, "0");
const day = (v) => (/^\d{4}-\d{2}-\d{2}$/.test(String(v || "")) && !isNaN(Date.parse(v)) ? String(v) : "");
const num = (v, lo, hi, dflt) => { const n = Number(v); return v === "" || v == null || !isFinite(n) ? dflt : Math.min(hi, Math.max(lo, Math.round(n * 100) / 100)); };
const lines = (list, max, len) => (Array.isArray(list) ? list : []).slice(0, max).map((x) => str(x, len)).filter(Boolean);

function cleanInvoice(d, number, old) {
  const items = (Array.isArray(d.items) ? d.items : []).slice(0, INV.items).filter((x) => x && typeof x === "object").map((x) => ({
    title: str(x.title, 200), sub: str(x.sub, 300), bullets: lines(x.bullets, INV.bullets, 300),
    qty: num(x.qty, 0, 100000, 1), price: num(x.price, -1000000, 1000000, null),   // price stays empty until it's typed in
  }));
  const discounts = (Array.isArray(d.discounts) ? d.discounts : []).slice(0, INV.discounts).filter((x) => x && typeof x === "object").map((x) => {
    const kind = x.kind === "pct" ? "pct" : "amt";
    return { label: str(x.label, 80), kind, value: num(x.value, 0, kind === "pct" ? 100 : 1000000, 0) };
  });
  const b = d.billTo || {}, p = d.pay || {}, s = d.support || {};
  const status = ["draft", "sent", "paid"].indexOf(d.status) >= 0 ? d.status : "draft";
  const site = str(d.site, 40).toLowerCase();
  const inv = {
    number, status, site: /^[a-z0-9][a-z0-9-]{1,39}$/.test(site) ? site : "",
    issued: day(d.issued) || new Date().toISOString().slice(0, 10), payDays: num(d.payDays, 0, 365, 14),
    billTo: { name: str(b.name, 120), attn: str(b.attn, 120), email: str(b.email, 160) },
    items, discounts,
    pay: { method: str(p.method, 60), sendTo: str(p.sendTo, 80), recipient: str(p.recipient, 80), memo: str(p.memo, 80), qr: p.qr !== false },
    support: { on: s.on !== false, until: day(s.until), included: lines(s.included, INV.support, 160), extra: lines(s.extra, INV.support, 160) },
    sentOn: status === "draft" ? "" : day(d.sentOn) || new Date().toISOString().slice(0, 10),
    paidOn: status === "paid" ? day(d.paidOn) || new Date().toISOString().slice(0, 10) : "",
    created: (old && old.created) || new Date().toISOString(), updated: new Date().toISOString(),
  };
  inv.total = invoiceTotal(inv);
  return inv;
}
// Same math as the admin: discounts come off the subtotal (a % is of the subtotal), never below zero.
function invoiceTotal(inv) {
  const cents = (n) => Math.round(n * 100);
  const sub = inv.items.reduce((t, x) => t + cents((x.price || 0) * x.qty), 0);
  const off = inv.discounts.reduce((t, x) => t + (x.kind === "pct" ? Math.round(sub * x.value / 100) : cents(x.value)), 0);
  return Math.max(0, sub - off) / 100;
}
async function adminInvoice(req, env) {
  const d = await body(req); if (!d || typeof d.invoice !== "object" || !d.invoice) return fail(400, "Bad request.");
  let number = str(d.invoice.number, 12).toUpperCase(), old = null;
  if (number) {
    if (!INV_NO.test(number)) return fail(400, "Invoice numbers look like SW-0002.");
    old = await env.NOTES.get("inv:" + number, "json");
    if (d.isNew && old) return fail(409, "Invoice " + number + " is already used. Pick another number.");
  } else {
    const used = (await listKeys(env, "inv:")).map((k) => Number(k.slice(7))).filter((n) => n > 0);
    number = invNo(Math.max(INV.first - 1, ...used) + 1);
  }
  const inv = cleanInvoice(d.invoice, number, old);
  await env.NOTES.put("inv:" + number, JSON.stringify(inv));
  return json({ ok: true, invoice: inv });
}
async function adminInvoiceDelete(req, env) {
  const d = await body(req); const number = str(d && d.number, 12).toUpperCase();
  if (!INV_NO.test(number)) return fail(400, "Bad invoice number.");
  await env.NOTES.delete("inv:" + number);
  return json({ ok: true });
}

/* ---------- router ---------- */

async function route(req, env, url, path) {
  const post = req.method === "POST";
  if (path === "" || path === "/api") return json({ ok: true, service: "Site Notes is running.", version: VERSION });
  if (path === "/api/check") return setupCheck(url, env);
  if (path === "/api/login" && post) return clientLogin(req, env);
  if (path === "/api/logout" && post) return endSession(env, req);
  if (path === "/api/pic" && post) return savePic(req, env);
  if (path === "/api/notes" && post) return saveNotes(req, env);
  if (path === "/api/stats" && post) return clientStats(req, env);
  if (path === "/api/my-photos" && post) return myPhotos(req, env);
  if (path === "/api/my-photo" && post) return myPhoto(req, env);
  if (path === "/api/admin/login" && post) return adminLogin(req, env);
  if (path === "/api/admin/logout" && post) return endSession(env, req);
  if (path.startsWith("/api/admin/")) {
    if (!(await readSession(env, req, "a"))) return fail(401, "Please log in again.");
    if (path === "/api/admin/data") return adminData(env);
    if (path === "/api/admin/pic") return adminPic(url, env);
    if (path === "/api/admin/client" && post) return adminClient(req, env);
    if (path === "/api/admin/client/delete" && post) return adminClientDelete(req, env);
    if (path === "/api/admin/done" && post) return adminDone(req, env);
    if (path === "/api/admin/pic-used" && post) return adminPicUsed(req, env);
    if (path === "/api/admin/batch/delete" && post) return adminBatchDelete(req, env);
    if (path === "/api/admin/stats" && post) return adminStats(req, env);
    if (path === "/api/admin/invoice" && post) return adminInvoice(req, env);
    if (path === "/api/admin/invoice/delete" && post) return adminInvoiceDelete(req, env);
  }
  return fail(404, "Not found.");
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), path = url.pathname.replace(/\/+$/, "");
    const cors = corsFor(req, env, path);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: { ...SAFE, ...cors } });
    let res;
    if (!env.NOTES || !env.ADMIN_PASSWORD) res = fail(500, "The service isn't set up yet (needs the NOTES storage and ADMIN_PASSWORD).");
    // The admin side only answers its own page (a browser on another site can't read the answer anyway,
    // this also stops it from sending anything).
    else if (path.startsWith("/api/admin/") && !cors["access-control-allow-origin"] && req.headers.get("origin")) res = fail(403, "Not allowed from this address.");
    else {
      try { res = await route(req, env, url, path); }
      catch (e) { res = fail(500, "Something went wrong on the server."); }
    }
    for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
    return res;
  },
};
