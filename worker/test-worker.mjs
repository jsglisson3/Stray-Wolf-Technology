import worker from "./worker.js";
import { fakeKV } from "./fakekv.mjs";
const env = { NOTES: fakeKV(), ADMIN_PASSWORD: "howl-at-the-moon" };
let pass = 0, failN = 0;
const ok = (name, cond) => { cond ? pass++ : (failN++, console.log("FAIL", name)); };
const call = async (path, { body, token, method, raw, type: sendType, ip, origin } = {}) => {
  const r = await worker.fetch(new Request("https://x.test" + path, { method: method || (body || raw ? "POST" : "GET"),
    headers: { ...(token ? { authorization: "Bearer " + token } : {}), ...(sendType ? { "content-type": sendType } : {}), "cf-connecting-ip": ip || "1.2.3.4", ...(origin !== null ? { origin: origin || (path.startsWith("/api/admin/") ? "https://straywolftech.com" : "https://cedar.test") } : {}) }, body: raw || (body ? JSON.stringify(body) : undefined) }), env);
  const type = r.headers.get("content-type") || "";
  return { status: r.status, cors: r.headers.get("access-control-allow-origin"), headers: r.headers, type, data: type.includes("json") ? await r.json() : new Uint8Array(await r.arrayBuffer()) };
};
const png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

let r = await call("/api"); ok("health", r.data.ok && r.cors === "*");
r = await call("/api/x", { method: "OPTIONS" }); ok("preflight", r.status === 204);
r = await call("/api/admin/data"); ok("admin needs token", r.status === 401);
r = await call("/api/admin/login", { body: { password: "nope" } }); ok("admin wrong pw", r.status === 401);
r = await call("/api/admin/login", { body: { password: "howl-at-the-moon" } }); ok("admin login", r.data.ok); const admin = r.data.token;
r = await call("/api/admin/client", { token: admin, body: { site: "Bad Name!", name: "x", password: "abcdef" } }); ok("bad site id", r.status === 400);
r = await call("/api/admin/client", { token: admin, body: { site: "cedar-street", name: "Cedar Street Barbers", url: "cedar.test", password: "abc" } }); ok("short pw", r.status === 400);
r = await call("/api/admin/client", { token: admin, body: { site: "cedar-street", name: "Cedar Street Barbers", url: "cedar.test", password: "maple-4821" } }); ok("add client", r.data.ok);
r = await call("/api/login", { body: { site: "cedar-street", password: "wrong" } }); ok("client wrong pw", r.status === 401);
r = await call("/api/login", { body: { site: "nobody", password: "maple-4821" } }); ok("unknown site", r.status === 401);
r = await call("/api/login", { body: { site: "Cedar-Street", password: "maple-4821" } }); ok("client login", r.data.ok && r.data.name === "Cedar Street Barbers"); const client = r.data.token;
r = await call("/api/admin/data", { token: client }); ok("client token can't open admin", r.status === 401);
r = await call("/api/notes", { token: admin, body: { notes: [{ text: "x" }] } }); ok("admin token can't send notes", r.status === 401);
r = await call("/api/notes", { token: client + "x", body: { notes: [{ text: "x" }] } }); ok("tampered token", r.status === 401);
r = await call("/api/notes", { token: client, body: { notes: [] } }); ok("empty send", r.status === 400);
const pngBytes = Buffer.from(png, "base64");
r = await call("/api/pic", { raw: pngBytes, type: "image/png" }); ok("pic upload needs login", r.status === 401);
r = await call("/api/pic", { token: admin, raw: pngBytes, type: "image/png" }); ok("admin token can't upload", r.status === 401);
r = await call("/api/pic", { token: client, raw: pngBytes, type: "image/gif" }); ok("bad pic type", r.status === 400);
r = await call("/api/pic", { token: client, raw: new Uint8Array(3 * 1024 * 1024 + 1), type: "image/jpeg" }); ok("pic too big", r.status === 413);
r = await call("/api/pic", { token: client, raw: pngBytes, type: "image/png" }); ok("pic upload", r.data.ok && r.data.key.startsWith("pic:cedar-street:")); const upKey = r.data.key;
r = await call("/api/notes", { token: client, body: { notes: [{ text: "x", pics: ["pic:other-client:123-abc"] }] } }); ok("can't attach someone else's picture", r.status === 400);
r = await call("/api/notes", { token: client, body: { notes: [{ text: "x", pics: ["client:cedar-street"] }] } }); ok("can't attach a non-picture key", r.status === 400);
r = await call("/api/notes", { token: client, body: { notes: [{ text: "x", pics: Array(21).fill(upKey) }] } }); ok("too many pictures", r.status === 400);
r = await call("/api/notes", { token: client, body: { notes: [
  { page: "/", title: "Home", on: "Services: Haircut · $30", text: "Change to $32 <b>please</b>", pics: [] },
  { page: "/", title: "Home", on: "Photos: Fresh fade", text: "", pics: [upKey] },
  { page: "/", title: "Home", on: "nothing", text: "   ", pics: [] } ] } });
ok("send", r.data.ok && r.data.notes === 2 && r.data.pictures === 1); const batchId = r.data.id;
r = await call("/api/admin/data", { token: admin });
ok("admin sees it", r.data.clients.length === 1 && r.data.batches.length === 1 && r.data.batches[0].notes.length === 2 && r.data.batches[0].site === "cedar-street");
ok("password visible to admin", r.data.clients[0].password === "maple-4821");
const picKey = r.data.batches[0].notes[1].pics[0];
r = await call("/api/admin/pic?key=" + encodeURIComponent(picKey), { token: admin }); ok("pic", r.type === "image/png" && Buffer.from(r.data).equals(pngBytes));
r = await call("/api/admin/pic?key=" + encodeURIComponent(picKey), { token: client }); ok("pic needs admin", r.status === 401);
r = await call("/api/admin/pic?key=client:cedar-street", { token: admin }); ok("pic key guarded", r.status === 400);
r = await call("/api/admin/done", { token: admin, body: { batch: batchId, n: 1, done: true } }); ok("done", r.data.ok);
r = await call("/api/admin/data", { token: admin }); ok("done saved", r.data.batches[0].notes[0].done === true && r.data.batches[0].notes[1].done === false);
r = await call("/api/admin/client", { token: admin, body: { site: "cedar-street", password: "birch-9001" } }); ok("change pw keeps name", r.data.client.name === "Cedar Street Barbers");
r = await call("/api/login", { body: { site: "cedar-street", password: "maple-4821" } }); ok("old pw dead", r.status === 401);
r = await call("/api/notes", { token: client, body: { notes: [{ text: "x" }] } }); ok("new password logged the client out", r.status === 401);
let client2 = (await call("/api/login", { body: { site: "cedar-street", password: "birch-9001" } })).data.token;
r = await call("/api/admin/batch/delete", { token: admin, body: { batch: batchId } }); ok("delete batch", r.data.ok && ![...env.NOTES._m.keys()].some((k) => k.startsWith("pic:") || k.startsWith("batch:")));
// ---- photo captions (picNotes) ----
r = await call("/api/pic", { token: client2, raw: pngBytes, type: "image/png" }); const k1 = r.data.key;
r = await call("/api/pic", { token: client2, raw: pngBytes, type: "image/png" }); const k2 = r.data.key;
r = await call("/api/notes", { token: client2, body: { notes: [
  { page: "/", title: "Home", on: "Photos", text: "New pictures\n\nPhoto 2: the new shed pad", pics: [k1, k2], picNotes: ["", "the new shed pad" + "x".repeat(200), "extra one"] },
  { page: "/", title: "Home", on: "Photos", text: "no words", pics: [k1], picNotes: [""] },
  { page: "/", title: "Home", on: "Old portal", text: "older site-notes.js", pics: [k2] } ] } });
ok("send with captions", r.data.ok && r.data.pictures === 4); const capBatch = r.data.id;
r = await call("/api/admin/data", { token: admin });
{ const b = r.data.batches.find((x) => x.id === capBatch), [a, bl, c] = b.notes;
  ok("captions kept, same order as pictures", Array.isArray(a.picNotes) && a.picNotes.length === 2 && a.picNotes[0] === "" && a.picNotes[1].startsWith("the new shed pad") && a.picNotes[1].length === 140);
  ok("all-empty captions left off", !("picNotes" in bl));
  ok("older portal (no captions) still works", !("picNotes" in c) && c.pics.length === 1); }
await call("/api/admin/batch/delete", { token: admin, body: { batch: capBatch } });
// ---- where each note was left ----
r = await call("/api/notes", { token: client2, body: { notes: [
  { page: "/", title: "Home", on: "Top of the page: Groundwork Done Right.", text: "Change this", url: "https://cedar.test/", sel: "#hero > h1", path: [0, 2, 1], fx: 0.25, fy: 1.7, py: 0.0412345, snip: "Groundwork Done Right" + "x".repeat(300), vw: 390 },
  { page: "/", title: "Home", on: "x", text: "junk where", url: "javascript:alert(1)", path: [0, -1], fx: "a", py: NaN, vw: 3.5 },
  { page: "/", title: "Home", on: "older", text: "no where at all" } ] } });
ok("send with where", r.data.ok); const whereBatch = r.data.id;
r = await call("/api/admin/data", { token: admin });
{ const [a, j, o] = r.data.batches.find((x) => x.id === whereBatch).notes;
  ok("where kept", a.url === "https://cedar.test/" && a.sel === "#hero > h1" && a.path.join() === "0,2,1" && a.fx === 0.25 && a.fy === 1 && a.py === 0.041 && a.snip.length === 160 && a.vw === 390);
  ok("bad where dropped", !("url" in j) && !("path" in j) && !("fx" in j) && !("py" in j) && !("vw" in j));
  ok("older notes untouched", !["url", "sel", "path", "fx", "fy", "py", "snip", "vw"].some((k) => k in o)); }
await call("/api/admin/batch/delete", { token: admin, body: { batch: whereBatch } });

// ---- contacts ----
r = await call("/api/admin/client", { token: admin, body: { site: "cedar-street", contacts: [
  { name: "Marcus Lee", role: "Owner", phone: "555-201-3344", email: "marcus@cedar.test", note: "Text first", junk: "dropped" },
  { name: "", email: "nobody@x.test" }, "not a person" ] } });
ok("save contacts", r.data.ok && r.data.client.contacts.length === 1 && r.data.client.contacts[0].email === "marcus@cedar.test" && !("junk" in r.data.client.contacts[0]));
ok("contacts keep name and password", r.data.client.name === "Cedar Street Barbers" && r.data.client.password === "birch-9001");
r = await call("/api/admin/client", { token: admin, body: { site: "cedar-street", password: "birch-9002" } }); ok("new password keeps contacts", r.data.client.contacts.length === 1);
r = await call("/api/admin/data", { token: admin }); ok("admin data has contacts", r.data.clients[0].contacts[0].name === "Marcus Lee");
r = await call("/api/admin/client", { token: admin, body: { site: "cedar-street", contacts: [] } }); ok("clear contacts", r.data.client.contacts.length === 0);
r = await call("/api/admin/client", { token: admin, body: { site: "cedar-street", password: "birch-9001" } });
client2 = (await call("/api/login", { body: { site: "cedar-street", password: "birch-9001" } })).data.token;

// ---- Google Analytics numbers (Google is a local stand-in) ----
const { subtle } = globalThis.crypto;
const kp = await subtle.generateKey({ name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" }, true, ["sign", "verify"]);
const pkcs8 = Buffer.from(await subtle.exportKey("pkcs8", kp.privateKey)).toString("base64").replace(/(.{64})/g, "$1\n");
const SA = { client_email: "notes@stray-wolf.iam.gserviceaccount.com", private_key: "-----BEGIN PRIVATE KEY-----\n" + pkcs8 + "\n-----END PRIVATE KEY-----\n" };
let gHits = { token: 0, report: 0 }, gMode = "ok", lastJwtOk = false, lastProp = "";
const realFetch = globalThis.fetch;
const gFetch = async (u, o) => {
  const J = (b, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json" } });
  if (u === "https://oauth2.googleapis.com/token") {
    gHits.token++;
    const jwt = new URLSearchParams(o.body).get("assertion"), [h, p, s] = jwt.split(".");
    const sig = Buffer.from(s.replace(/-/g, "+").replace(/_/g, "/"), "base64");
    lastJwtOk = await subtle.verify("RSASSA-PKCS1-v1_5", kp.publicKey, sig, new TextEncoder().encode(h + "." + p))
      && JSON.parse(Buffer.from(p, "base64").toString()).iss === SA.client_email;
    return lastJwtOk ? J({ access_token: "ya29.test", expires_in: 3600 }) : J({ error: "invalid_grant" }, 400);
  }
  const mb = String(u).match(/properties\/(\d+):batchRunReports$/);
  if (mb) { const reports = []; for (const q of JSON.parse(o.body).requests) { const rr = await gFetch(String(u).replace(":batchRunReports", ":runReport"), { ...o, body: JSON.stringify(q) }); if (!rr.ok) return rr; reports.push(await rr.json()); } return J({ reports }); }
  const m = String(u).match(/properties\/(\d+):runReport$/);
  if (m) {
    gHits.report++; lastProp = m[1];
    if (gMode === "403") return J({ error: { code: 403 } }, 403);
    const q = JSON.parse(o.body), row = (dims, n) => ({ dimensionValues: dims.map((value) => ({ value })), metricValues: [{ value: String(n) }] });
    const dimNames = (q.dimensions || []).map((d) => d.name);
    if (dimNames[0] === "date") { // each day: yesterday and a day outside the window (dropped)
      const [ty, tm, td] = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Chicago", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date()).split("-").map(Number);
      const y = new Date(Date.UTC(ty, tm - 1, td - 1)).toISOString().slice(0, 10).replace(/-/g, ""); // yesterday where the property is
      return J({ rows: q.metrics[0].name === "activeUsers" ? [row([y], 9), row(["19990101"], 5)] : [row([y, "phone_call_click"], 2), row([y, "generate_lead"], 1)] });
    }
    if (q.metrics[0].name === "screenPageViews") return J({ rows: [row(["/", "Home | Cedar"], 50), row(["/prices/", "Prices"], 20), row(["/", "Home"], 5), row(["/book/", "(not set)"], 9), row(["/about/", "About"], 3)] });
    if (q.metrics[0].name === "activeUsers") return J({ rows: [row(["date_range_0"], 412), row(["date_range_1"], 349)] });
    if (q.metrics[0].name === "eventCount") return J({ rows: [row(["phone_call_click", "date_range_0"], 23), row(["phone_call_click", "date_range_1"], 21), row(["generate_lead", "date_range_0"], 7)] });
    return J({ rows: [row(["(not set)"], 90), row(["m.facebook.com"], 80), row(["google"], 60)] });
  }
  return realFetch(u, o);
};
globalThis.fetch = gFetch;
r = await call("/api/stats", { body: { site: "cedar-street" } }); ok("stats needs login", r.status === 401);
r = await call("/api/stats", { token: admin, body: {} }); ok("admin token isn't a client login", r.status === 401);
r = await call("/api/stats", { token: client2, body: { site: "cedar-street" } }); ok("no property yet = 404 (card stays hidden)", r.status === 404 && !r.data.ok);
r = await call("/api/admin/stats", { token: admin, body: { site: "cedar-street" } }); ok("admin: not connected yet", r.status === 404 && /No Google/.test(r.data.error));
await env.NOTES.put("ga:cedar-street", "512345678");
r = await call("/api/stats", { token: client2, body: {} }); ok("property but no secret = clear message", r.status === 503 && !r.data.ok);
env.GA_SA_JSON = JSON.stringify(SA);
r = await call("/api/stats", { token: client2, body: { site: "someone-else" } });
ok("portal numbers", r.data.ok && r.data.visitors === 412 && r.data.visitorsChange === 18 && r.data.calls === 23 && r.data.callsChange === 10 && r.data.leads === 7 && r.data.leadsChange === 0 && r.data.source === "Facebook" && r.data.days === 28);
ok("signed with the service account", lastJwtOk && lastProp === "512345678" && gHits.token === 1 && gHits.report === 6);
ok("counts before, for exact change", r.data.visitorsPrev === 349 && r.data.callsPrev === 21 && r.data.leadsPrev === 0);
ok("each day: 28 numbers, yesterday last", r.data.daily && r.data.daily.visitors.length === 28 && r.data.daily.visitors[27] === 9 && r.data.daily.calls[27] === 2 && r.data.daily.leads[27] === 1 && r.data.daily.visitors.reduce((a, b) => a + b) === 9 && /^\d{4}-\d{2}-\d{2}$/.test(r.data.daily.start));
ok("top 3 pages, same path added up", r.data.pages.length === 3 && r.data.pages[0].path === "/" && r.data.pages[0].views === 55 && r.data.pages[0].title === "Home | Cedar" && r.data.pages[2].path === "/book/" && r.data.pages[2].title === "");
ok("portal gets own site only, no property ID", !("property" in r.data));
r = await call("/api/admin/stats", { token: admin, body: { site: "cedar-street" } });
ok("admin shares the 6-hour cache", r.data.ok && r.data.property === "512345678" && r.data.visitors === 412 && gHits.report === 6);
r = await call("/api/admin/stats", { body: { site: "cedar-street" } }); ok("admin stats needs admin", r.status === 401);
r = await call("/api/admin/stats", { token: client2, body: { site: "cedar-street" } }); ok("client can't use admin stats", r.status === 401);
await env.NOTES.put("ga:juniper", "properties/600000001"); gMode = "403";
r = await call("/api/admin/stats", { token: admin, body: { site: "juniper" } }); ok("no Viewer access = plain message", r.status === 502 && /Viewer/.test(r.data.error) && gHits.token === 1);
ok("errors aren't cached", (await env.NOTES.get("stats:juniper")) === null);
gMode = "ok"; r = await call("/api/admin/stats", { token: admin, body: { site: "juniper" } }); ok("'properties/' prefix accepted", r.data.ok && lastProp === "600000001");
env.GA_SA_JSON = "not json"; await env.NOTES.delete("gatoken"); await env.NOTES.delete("stats:juniper");
r = await call("/api/admin/stats", { token: admin, body: { site: "juniper" } }); ok("bad secret = clear message", r.status === 502 && /GA_SA_JSON/.test(r.data.error));
r = await call("/api/admin/stats", { token: admin, body: { site: "Bad Site!" } }); ok("bad site name", r.status === 400);
globalThis.fetch = realFetch; delete env.GA_SA_JSON;

// ---- setup check page + forgiving property IDs ----
r = await call("/api"); ok("health shows version", /^2026-11-13k/.test(r.data.version));
await env.NOTES.put("ga:quoted", '"562482788" '); env.GA_SA_JSON = JSON.stringify(SA); globalThis.fetch = gFetch;
r = await call("/api/admin/stats", { token: admin, body: { site: "quoted" } }); ok("quotes around the ID forgiven", r.data.ok && lastProp === "562482788");
await env.NOTES.put("ga:measure", "G-ABC123XYZ");
r = await call("/api/admin/stats", { token: admin, body: { site: "measure" } }); ok("measurement ID explained", r.status === 400 && /Measurement ID/.test(r.data.error));
r = await call("/api/check?site=quoted"); ok("check page", r.data.googleKeySaved && r.data.googleKeyLooksRight && r.data.propertyIdSaved && r.data.propertyIdLooksRight && r.data.numbersCached && !JSON.stringify(r.data).includes("562482788"));
r = await call("/api/check?site=nobody"); ok("check page, no ID", r.data.propertyIdSaved === false);
globalThis.fetch = realFetch; delete env.GA_SA_JSON;
r = await call("/api/check"); ok("check page, no key", r.data.googleKeySaved === false);

// ---- 13j: Google that hangs. Reports go one at a time, each with its own time limit and one retry ----
{
  let inFlight = 0, most = 0, hang = 0, hangBody = 0, hangAll = false, reports = 0;
  const never = (signal) => new Promise((_, no) => signal && signal.addEventListener("abort", () => no(signal.reason || new Error("aborted"))));
  globalThis.fetch = async (u, o) => {
    if (/tokeninfo|discovery|metadata|checkCompatibility|analyticsadmin/.test(String(u))) return new Response("{}", { status: 200 });   // probe calls, never the real Google
    if (!/:runReport(\?|$)/.test(String(u))) return gFetch(u, o);
    u = String(u).replace(/\?.*$/, "");
    reports++; inFlight++; most = Math.max(most, inFlight);
    try {
      if (hangAll || hang > 0) { hang--; return await never(o.signal); }   // never answers
      const real = await gFetch(u, o);
      if (hangBody > 0) { hangBody--;                                       // answers, then the body never ends
        return new Response(new ReadableStream({ start() {} }), { status: 200, headers: { "content-type": "application/json" } }); }
      return real;
    } finally { inFlight--; }
  };
  env.GA_SA_JSON = JSON.stringify(SA); await env.NOTES.put("ga:hangs", "577777777");
  let t = Date.now(); hang = 1;
  r = await call("/api/admin/stats", { token: admin, body: { site: "hangs" } });
  ok("hung report is dropped and asked again", r.data.ok && !r.data.stale && r.data.visitors === 412 && r.data.source === "Facebook" && r.data.pages.length === 3 && reports === 7);
  ok("reports never run at the same time", most === 1);
  ok("a retry finishes inside the admin's 20 s wait", Date.now() - t < 9000);
  ok("a fully good fetch leaves no problem", (await env.NOTES.get("gaerr:hangs", "json")) === null);
  await env.NOTES.delete("stats:hangs"); hangBody = 1; reports = 0; t = Date.now();
  r = await call("/api/admin/stats", { token: admin, body: { site: "hangs" } });
  ok("answer whose body never ends is dropped and asked again", r.data.ok && !r.data.stale && r.data.visitors === 412 && reports === 7 && Date.now() - t < 9000);
  // Google hangs on everything: the last saved numbers come back, marked stale, before the admin gives up
  await env.NOTES.delete("stats:hangs"); hangAll = true; reports = 0; t = Date.now();
  r = await call("/api/admin/stats", { token: admin, body: { site: "hangs" } });
  const took = Date.now() - t;
  ok("Google hangs: last numbers shown, marked stale", r.data.ok && r.data.stale === true && r.data.visitors === 412);
  ok("Google hangs: answer in under 17 s", took < 17000);
  const p2 = await env.NOTES.get("gaerr:hangs", "json");
  ok("check page problem says which step and lists timings", p2 && /headline numbers \(visitors\)/.test(p2.what) && /longer than/.test(p2.said) && p2.steps.length >= 2 && p2.steps[0].step === "sign-in");
  hangAll = false;
  // &test=1 times each step, one after another; &test=2 asks all 3 at once
  most = 0; r = await call("/api/check?site=hangs&test=1");
  ok("test=1: sign-in and 3 reports, each timed", r.data.test.signIn === "ok" && r.data.test.report === "ok" && r.data.test.steps.length === 3 && /^visitors: ok in [\d.]+ s$/.test(r.data.test.steps[0]) && most === 1);
  ok("test=1: no numbers or IDs shown", !JSON.stringify(r.data).includes("577777777") && !JSON.stringify(r.data).includes("412"));
  r = await call("/api/check?site=hangs&test=1"); ok("test=1 once a minute", /minute/.test(r.data.test.skipped));
  await env.NOTES.delete("gatest:hangs"); most = 0;
  r = await call("/api/check?site=hangs&test=2"); ok("test=2: 3 at once", r.data.test.report === "ok" && most === 3 && /at once/.test(r.data.test.mode));
  // &test=3 probes 8 small Google calls; one that hangs shows NO ANSWER, nothing secret shown
  await env.NOTES.delete("gatest:hangs"); hang = 1; t = Date.now();
  r = await call("/api/check?site=hangs&test=3");
  const ps = r.data.test.steps || [];
  ok("test=3: 8 probes listed", ps.length === 8 && r.data.test.signIn === "ok");
  ok("test=3: the hung report shows NO ANSWER, the other report answers", /^7 .*NO ANSWER in 5 s/.test(ps[6]) && /^8 .*: 200 in/.test(ps[7]));
  ok("test=3: no IDs or token shown", !JSON.stringify(r.data).includes("577777777") && !JSON.stringify(r.data).includes("ya29"));
  // 403 (no Viewer access) is not asked again
  await env.NOTES.put("ga:noaccess", "588888888"); gMode = "403"; reports = 0;
  r = await call("/api/admin/stats", { token: admin, body: { site: "noaccess" } }); ok("403 asked once, plain message", r.status === 502 && /Viewer/.test(r.data.error) && reports === 1);
  gMode = "ok"; globalThis.fetch = realFetch; delete env.GA_SA_JSON;
}

// ---- the right password clears earlier wrong tries ----
for (let i = 0; i < 6; i++) await call("/api/login", { body: { site: "cedar-street", password: "oops" + i } });
r = await call("/api/login", { body: { site: "cedar-street", password: "birch-9001" } }); ok("right password after several misses (1 earlier + 6)", r.data.ok);
ok("wrong tries cleared", (await env.NOTES.get("fail:1.2.3.4")) === null);

for (let i = 0; i < 8; i++) await call("/api/login", { body: { site: "cedar-street", password: "guess" + i } });
r = await call("/api/login", { body: { site: "cedar-street", password: "birch-9001" } }); ok("throttled after many fails", r.status === 429);
const env2 = { NOTES: env.NOTES, ADMIN_PASSWORD: "new-password" };
const r2 = await worker.fetch(new Request("https://x.test/api/admin/data", { headers: { authorization: "Bearer " + admin } }), env2); ok("changing admin pw logs out", r2.status === 401);


// ======== V-g: sessions, logout, limits, lockout, pictures, CORS, headers ========
const realNow = Date.now; let shift = 0; Date.now = () => realNow() + shift;
const ip2 = "5.6.7.8";
const freshClient = async () => (await call("/api/login", { ip: ip2, body: { site: "cedar-street", password: "birch-9001" } })).data.token;
r = await call("/api/admin/login", { ip: ip2, body: { password: "howl-at-the-moon" } }); const adm = r.data.token;
ok("admin login gives a random key + limits", /^[\w-]{43}$/.test(adm) && r.data.idleMinutes === 30 && r.data.maxMinutes === 480);
ok("only the fingerprint is stored", ![...env.NOTES._m.keys()].some((k) => k.includes(adm)) && [...env.NOTES._m.keys()].some((k) => k.startsWith("sess:")));
r = await call("/api/admin/data", { token: adm }); ok("new admin login works", r.data.ok);
// logout
r = await call("/api/admin/logout", { token: adm, body: {} }); ok("admin logout ok", r.data.ok);
r = await call("/api/admin/data", { token: adm }); ok("admin key dead after logout", r.status === 401);
// idle
let a2 = (await call("/api/admin/login", { ip: ip2, body: { password: "howl-at-the-moon" } })).data.token;
shift = 29 * 6e4; r = await call("/api/admin/data", { token: a2 }); ok("admin 29 min idle still in", r.data.ok);
shift += 29 * 6e4; r = await call("/api/admin/data", { token: a2 }); ok("activity pushed the idle limit back", r.data.ok);
shift += 31 * 6e4; r = await call("/api/admin/data", { token: a2 }); ok("admin 31 min idle = out", r.status === 401);
// absolute
shift = 0; a2 = (await call("/api/admin/login", { ip: ip2, body: { password: "howl-at-the-moon" } })).data.token;
for (let m = 20; m <= 470; m += 20) { shift = m * 6e4; await call("/api/admin/data", { token: a2 }); }
shift = 475 * 6e4; r = await call("/api/admin/data", { token: a2 }); ok("admin active 7h55 still in", r.data.ok);
shift = 481 * 6e4; r = await call("/api/admin/data", { token: a2 }); ok("admin 8h max = out even if active", r.status === 401);
shift = 0;
// client sessions
let c2 = await freshClient();
r = await call("/api/my-photos", { token: c2, body: {} }); ok("client login works", r.data.ok);
r = await call("/api/logout", { token: c2, body: {} }); ok("client logout ok", r.data.ok);
r = await call("/api/my-photos", { token: c2, body: {} }); ok("client key dead after logout", r.status === 401);
c2 = await freshClient();
shift = 119 * 6e4; r = await call("/api/my-photos", { token: c2, body: {} }); ok("client 1h59 idle still in", r.data.ok);
shift += 121 * 6e4; r = await call("/api/my-photos", { token: c2, body: {} }); ok("client 2h idle = out", r.status === 401);
shift = 0; c2 = await freshClient();
for (let m = 100; m <= 1400; m += 100) { shift = m * 6e4; await call("/api/my-photos", { token: c2, body: {} }); }
shift = 1441 * 6e4; r = await call("/api/my-photos", { token: c2, body: {} }); ok("client 24h max = out", r.status === 401);
shift = 0;
// password change / delete revokes
const adm3 = (await call("/api/admin/login", { ip: ip2, body: { password: "howl-at-the-moon" } })).data.token;
c2 = await freshClient();
await call("/api/admin/client", { token: adm3, body: { site: "cedar-street", name: "Cedar Street Barbers" } });
r = await call("/api/my-photos", { token: c2, body: {} }); ok("editing name/contacts keeps client logged in", r.data.ok);
await call("/api/admin/client", { token: adm3, body: { site: "cedar-street", password: "birch-9001" } });
r = await call("/api/my-photos", { token: c2, body: {} }); ok("same password saved again keeps client logged in", r.data.ok);
await call("/api/admin/client", { token: adm3, body: { site: "cedar-street", password: "cedar-7777" } });
r = await call("/api/my-photos", { token: c2, body: {} }); ok("new client password logs them out", r.status === 401);
r = await call("/api/login", { ip: ip2, body: { site: "cedar-street", password: "cedar-7777" } }); c2 = r.data.token; ok("new password logs in", r.data.ok);
await call("/api/admin/client", { token: adm3, body: { site: "temp-co", name: "Temp", password: "temp-12345" } });
let ct = (await call("/api/login", { ip: ip2, body: { site: "temp-co", password: "temp-12345" } })).data.token;
await call("/api/admin/client/delete", { token: adm3, body: { site: "temp-co" } });
r = await call("/api/my-photos", { token: ct, body: {} }); ok("deleted client is logged out", r.status === 401);
r = await call("/api/admin/data", { token: c2 }); ok("client key isn't an admin key", r.status === 401);
r = await call("/api/notes", { token: adm3, body: { notes: [{ text: "x" }] } }); ok("admin key isn't a client key", r.status === 401);
// old HMAC-style keys are refused
r = await call("/api/admin/data", { token: "eyJrIjoiYSJ9.abc" }); ok("old-style key refused", r.status === 401);
// per-login lockout from many places
for (let i = 0; i < 20; i++) await call("/api/login", { ip: "9.9.9." + i, body: { site: "cedar-street", password: "nope" + i } });
r = await call("/api/login", { ip: "8.8.8.8", body: { site: "cedar-street", password: "cedar-7777" } }); ok("20 misses from many places lock that login", r.status === 429);
r = await call("/api/admin/login", { ip: "8.8.8.8", body: { password: "howl-at-the-moon" } }); ok("other logins unaffected", r.data.ok);
for (const k of [...env.NOTES._m.keys()]) if (k.startsWith("fail:")) await env.NOTES.delete(k);
// pictures must really be pictures
r = await call("/api/pic", { token: c2, raw: new TextEncoder().encode("<html><script>alert(1)</script>"), type: "image/png" }); ok("HTML dressed as PNG refused", r.status === 400);
r = await call("/api/pic", { token: c2, raw: new Uint8Array([0xff, 0xd8, 0xff, 0xe0, 0, 16]), type: "image/jpeg" }); ok("real JPEG start accepted", r.data.ok);
r = await call("/api/pic", { token: c2, raw: pngBytes, type: "image/png" }); const pk = r.data.key;
r = await call("/api/admin/pic?key=" + encodeURIComponent(pk), { token: adm3 });
ok("pictures sent with nosniff + sandbox CSP", r.headers.get("x-content-type-options") === "nosniff" && /sandbox/.test(r.headers.get("content-security-policy")));
// headers + CORS
r = await call("/api"); ok("JSON has safety headers", r.headers.get("x-frame-options") === "DENY" && r.headers.get("cache-control") === "no-store" && r.cors === "*");
r = await call("/api/admin/data", { token: adm3, origin: "https://evil.test" }); ok("admin refuses other web addresses", r.status === 403 && !r.cors);
r = await call("/api/admin/data", { token: adm3 }); ok("admin answers its own page", r.data.ok && r.cors === "https://straywolftech.com");
r = await call("/api/admin/data", { token: adm3, origin: null }); ok("no Origin (not a browser) still needs the key", r.data.ok);
r = await call("/api/admin/login", { method: "OPTIONS", origin: "https://evil.test" }); ok("admin preflight from elsewhere gets no CORS", r.status === 204 && !r.cors);
r = await call("/api/login", { method: "OPTIONS" }); ok("client preflight open", r.cors === "*");
env.ADMIN_ORIGINS = "http://localhost:8080";
r = await call("/api/admin/data", { token: adm3, origin: "http://localhost:8080" }); ok("ADMIN_ORIGINS setting", r.data.ok && r.cors === "http://localhost:8080");
delete env.ADMIN_ORIGINS;
// input limits
r = await call("/api/admin/client", { token: adm3, body: { site: "x-co", name: "X", password: "abcdefg", url: "javascript:alert(1)" } }); ok("bad website address refused", r.status === 400);
r = await call("/api/admin/client", { token: adm3, body: { site: "x-co", name: "X", password: "abcdefg", url: "https://jsglisson3.github.io/GLP-Home-Options/" } }); ok("GitHub Pages address accepted", r.data.ok);
r = await call("/api/notes", { token: c2, raw: JSON.stringify({ notes: [{ text: "x".repeat(300 * 1024) }] }), type: "application/json" }); ok("huge body refused", r.status === 400);
r = await call("/api/notes", { token: c2, body: { notes: [null, 5, { text: "fine" }] } }); ok("junk notes skipped, no crash", r.data.ok && r.data.notes === 1);
// KV copy expires by itself
const sk = [...env.NOTES._m.entries()].filter(([k]) => k.startsWith("sess:")).map(([, e]) => e.exp);
ok("stored logins expire on their own", sk.length && sk.every((e) => e > 0));
Date.now = realNow;
console.log(pass + " passed, " + failN + " failed");
// ---- invoices sit behind the admin login ----
{ const adm = (await call("/api/admin/login", { ip: "7.7.7.7", body: { password: "howl-at-the-moon" } })).data.token;
  let q = await call("/api/admin/invoice", { body: { invoice: {} } }); console.log(q.status === 401 ? "ok invoice needs admin" : "FAIL invoice open " + q.status);
  q = await call("/api/admin/invoice", { token: (await call("/api/login", { ip: "7.7.7.7", body: { site: "cedar-street", password: "cedar-7777" } })).data.token, body: { invoice: {} } }); console.log(q.status === 401 ? "ok client can't make invoices" : "FAIL " + q.status);
  q = await call("/api/admin/invoice", { token: adm, origin: "https://evil.test", body: { invoice: {} } }); console.log(q.status === 403 ? "ok invoice refuses other sites" : "FAIL " + q.status);
  q = await call("/api/admin/data", { token: adm }); console.log(Array.isArray(q.data.invoices) ? "ok data has invoices" : "FAIL no invoices"); }
