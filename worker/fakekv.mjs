// A stand-in for Cloudflare KV, for local testing only.
export function fakeKV() {
  const m = new Map();
  return {
    _m: m,
    async get(k, type) { const e = m.get(k); if (!e || (e.exp && e.exp < Date.now())) return null;
      if (type === "json") return JSON.parse(typeof e.v === "string" ? e.v : Buffer.from(e.v).toString());
      if (type === "arrayBuffer") return typeof e.v === "string" ? new TextEncoder().encode(e.v).buffer : e.v.buffer.slice(e.v.byteOffset, e.v.byteOffset + e.v.byteLength);
      return typeof e.v === "string" ? e.v : Buffer.from(e.v).toString(); },
    async getWithMetadata(k, type) { const e = m.get(k); return { value: e ? await this.get(k, type) : null, metadata: e ? e.meta || null : null }; },
    async put(k, v, o = {}) { m.set(k, { v: typeof v === "string" ? v : new Uint8Array(v), meta: o.metadata, exp: o.expirationTtl ? Date.now() + o.expirationTtl * 1000 : 0 }); },
    async delete(k) { m.delete(k); },
    async list({ prefix = "" } = {}) { return { keys: [...m.keys()].filter((k) => k.startsWith(prefix)).sort().map((name) => ({ name })), list_complete: true }; },
  };
}
