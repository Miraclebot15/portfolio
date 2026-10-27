#!/usr/bin/env python3
"""Browser smoke test. Serves the site over HTTP, stubs the /api status checks, then verifies:
console errors, horizontal overflow, tap-target size, broken internal links, and that the
live-status chips show Live / Down / Status unavailable correctly.

Requires:  pip install playwright && playwright install chromium
Run from the repo root:  python3 tests/smoke.py
"""
import functools, glob, http.server, json, os, re, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        pass

handler = functools.partial(Quiet, directory=ROOT)
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_address[1]}/"

pages = sorted(os.path.basename(f) for f in glob.glob(ROOT + "/*.html"))
SIZES = [("320", 320), ("390", 390), ("820", 820), ("1440", 1440)]
problems = []

for f in pages:  # internal links must exist
    for h in re.findall(r'href="([^"#][^"]*)"', open(os.path.join(ROOT, f), encoding="utf-8").read()):
        if not h.startswith(("http", "mailto")) and not os.path.exists(os.path.join(ROOT, h)):
            problems.append(f"{f}: broken link {h}")

def stub(status):
    return lambda route: route.fulfill(status=200, content_type="application/json",
                                       body=json.dumps({"status": status, "checkedAt": "2026-10-18T12:00:00Z"}))

with sync_playwright() as p:
    browser = p.chromium.launch()
    for f in pages:
        for label, w in SIZES:
            page = browser.new_page(viewport={"width": w, "height": 800})
            page.route("**/api/*-status", stub("live"))
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "ERR_NAME" not in m.text else None)
            page.goto(BASE + f, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(150)
            if page.evaluate("document.documentElement.scrollWidth > innerWidth"):
                problems.append(f"{f} @{label}: horizontal overflow")
            if page.evaluate("/[\\u2014\\u2013]/.test(document.body.innerText)"):
                problems.append(f"{f} @{label}: em or en dash in visible text")
            small = page.evaluate("""[...document.querySelectorAll('a,button')].filter(e => e.offsetParent && !e.closest('.menu')
                && e.getBoundingClientRect().height < 43.5 && !e.classList.contains('skip') && !e.classList.contains('sr'))
                .map(e => ({tag:e.tagName.toLowerCase(), id:e.id, cls:typeof e.className === 'string' ? e.className : '',
                    text:(e.innerText || e.getAttribute('aria-label') || '').trim().slice(0,48),
                    height:Math.round(e.getBoundingClientRect().height*10)/10}))""")
            if small:
                problems.append(f"{f} @{label}: tap target(s) under 44px: {small}")
            for e in errors:
                problems.append(f"{f} @{label}: console error: {e}")
            page.close()

    # Live status behaviour on the projects page
    for mode, expected in [("live", "Live"), ("down", "Down"), ("unknown", "Status unavailable")]:
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.route("**/api/*-status", stub(mode))
        page.goto(BASE + "projects.html")
        page.wait_for_timeout(800)
        labels = page.evaluate("[...document.querySelectorAll('[data-check] .lbl')].map(e => e.textContent)")
        if not labels or any(l != expected for l in labels):
            problems.append(f"status '{mode}': expected every chip to read {expected!r}, got {labels}")
        page.close()
    page = browser.new_page(viewport={"width": 1440, "height": 900})  # endpoint failing entirely
    page.route("**/api/*-status", lambda route: route.fulfill(status=500, body="error"))
    page.goto(BASE + "projects.html")
    page.wait_for_timeout(800)
    labels = page.evaluate("[...document.querySelectorAll('[data-check] .lbl')].map(e => e.textContent)")
    if not labels or any(l != "Status unavailable" for l in labels):
        problems.append(f"status endpoint error: expected 'Status unavailable', got {labels}")

    # Pause control: pauses every animation, resumes them, and is not defeated by touch hover
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    page = ctx.new_page()
    page.goto(BASE + "index.html")
    page.wait_for_timeout(900)
    states = "[...document.querySelectorAll('.row2,.tape .tk,.mk .orb,.badge svg')].map(e => getComputedStyle(e).animationPlayState)"
    page.evaluate("document.getElementById('pause').scrollIntoView({block:'center',behavior:'instant'})")
    page.tap("#pause"); page.wait_for_timeout(250)
    if set(page.evaluate(states)) != {"paused"}:
        problems.append(f"pause: not every animation paused: {set(page.evaluate(states))}")
    page.reload(); page.wait_for_timeout(700)
    if "Play" not in page.text_content("#pause"):
        problems.append("pause: state was not remembered after reload")
    page.evaluate("document.getElementById('pause').scrollIntoView({block:'center',behavior:'instant'})")
    page.tap("#pause"); page.wait_for_timeout(250)
    if set(page.evaluate(states)) != {"running"}:
        problems.append(f"resume: animations did not resume: {set(page.evaluate(states))}")
    ctx.close()
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(BASE + "index.html"); page.wait_for_timeout(700)
    page.evaluate("document.querySelector('.mq').scrollIntoView({block:'center',behavior:'instant'})")
    page.hover(".mq"); page.wait_for_timeout(200)
    if page.evaluate("getComputedStyle(document.querySelector('.row2')).animationPlayState") != "paused":
        problems.append("hover: marquee should pause under a mouse pointer")
    page.close()
    browser.close()

server.shutdown()
print("\n".join(problems) if problems else f"OK: {len(pages)} pages x {len(SIZES)} sizes + live-status states, no problems")
sys.exit(1 if problems else 0)
