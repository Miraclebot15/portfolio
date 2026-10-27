// Vercel serverless endpoint: checks the public ELLA deployment from the server,
// avoiding browser CORS restrictions. Two probes reduce transient false-down results.
const TARGET = "https://ella-bot-er0d.onrender.com/";
const TIMEOUT_MS = 9000;

async function probe() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(TARGET, {
      method: "GET",
      redirect: "follow",
      signal: controller.signal,
      headers: { "user-agent": "MiraclePortfolio-AvailabilityCheck/1.0" }
    });
    // A non-5xx response confirms the web service is responding, including redirects
    // and ordinary client errors. A 5xx response is treated as unavailable.
    if (response.status >= 200 && response.status < 500) return "live";
    if (response.status >= 500) return "down";
    return "unknown";
  } catch (_) {
    // A timeout or network error is inconclusive, not proof of downtime.
    return "unknown";
  } finally {
    clearTimeout(timer);
  }
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET" && req.method !== "HEAD") {
    res.setHeader("Allow", "GET, HEAD");
    return res.status(405).json({ status: "unknown", checkedAt: new Date().toISOString() });
  }

  try {
    const results = await Promise.all([probe(), probe()]);
    const status = results.includes("live")
      ? "live"
      : results.every((result) => result === "down")
        ? "down"
        : "unknown";
    return res.status(200).json({
      status,
      checkedAt: new Date().toISOString(),
      target: TARGET
    });
  } catch (_) {
    return res.status(200).json({
      status: "unknown",
      checkedAt: new Date().toISOString()
    });
  }
};
