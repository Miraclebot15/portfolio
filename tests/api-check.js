// Unit checks for the /api status functions, with fetch mocked. Run: node tests/api-check.js
const assert = require("assert");
const handlers = ["ella-status", "nexus-status", "carecore-status", "lagoon-status"].map((n) => [n, require("../api/" + n + ".js")]);

function run(handler, method = "GET") {
  return new Promise((resolve) => {
    const res = { headers: {}, setHeader(k, v) { this.headers[k] = v; }, status(c) { this.code = c; return this; }, json(b) { resolve({ code: this.code, body: b, headers: this.headers }); } };
    handler({ method }, res);
  });
}
const respond = (status) => async () => ({ status });
const fail = async () => { throw new Error("network"); };
const cases = [
  ["200 on both probes -> live", [respond(200), respond(200)], "live"],
  ["redirect/404 still means the site responds -> live", [respond(404), respond(404)], "live"],
  ["5xx on both probes -> down", [respond(503), respond(503)], "down"],
  ["timeout/network error alone is inconclusive -> unknown", [fail, fail], "unknown"],
  ["5xx plus network error -> unknown", [respond(503), fail], "unknown"],
  ["one probe live is enough -> live", [respond(503), respond(200)], "live"],
];
(async () => {
  for (const [name, handler] of handlers) {
    for (const [label, seq, expected] of cases) {
      let i = 0; global.fetch = (...a) => seq[i++ % seq.length](...a);
      const out = await run(handler);
      assert.strictEqual(out.body.status, expected, `${name}: ${label}`);
      assert.strictEqual(out.headers["Cache-Control"], "no-store, max-age=0");
    }
    assert.strictEqual((await run(handler, "POST")).code, 405, `${name}: POST rejected`);
  }
  console.log(`OK: ${handlers.length} status functions x ${cases.length + 1} checks`);
})().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
