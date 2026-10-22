// Public website availability check for NEXUS CORE.
// This checks whether the deployed frontend responds, not whether its backend works.
const TARGET = "https://nexus-core-psi-fawn.vercel.app/";
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
    if (response.status >= 200 && response.status < 500) return "live";
    if (response.status >= 500) return "down";
    return "unknown";
  } catch (_) {
    return "unknown";
  } finally {
    clearTimeout(timer);
  }
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  if (req.method !== "GET" && req.method !== "HEAD") {
    res.setHeader("Allow", "GET, HEAD");
    return res.status(405).json({ status: "unknown", checkedAt: new Date().toISOString() });
  }
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
};
