#!/usr/bin/env python3
"""Smoke test: console errors, horizontal overflow, tap-target size, broken links.

Requires:  pip install playwright && playwright install chromium
Run from the repo root:  python3 tests/smoke.py
"""
import glob, os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "file://" + ROOT + "/"
pages = sorted(os.path.basename(f) for f in glob.glob(ROOT + "/*.html"))
SIZES = [("320", 320), ("390", 390), ("820", 820), ("1440", 1440)]
problems = []

for f in pages:  # internal links must exist
    for h in re.findall(r'href="([^"#][^"]*)"', open(os.path.join(ROOT, f), encoding="utf-8").read()):
        if not h.startswith(("http", "mailto")) and not os.path.exists(os.path.join(ROOT, h)):
            problems.append(f"{f}: broken link {h}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    for f in pages:
        for label, w in SIZES:
            page = browser.new_page(viewport={"width": w, "height": 800})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "ERR_NAME" not in m.text else None)
            page.goto(BASE + f)
            page.wait_for_timeout(900)
            if page.evaluate("document.documentElement.scrollWidth > innerWidth"):
                problems.append(f"{f} @{label}: horizontal overflow")
            small = page.evaluate("""[...document.querySelectorAll('a,button')].filter(e => e.offsetParent && !e.closest('.menu')
                && e.getBoundingClientRect().height < 43.5 && !e.classList.contains('skip') && !e.classList.contains('sr')).length""")
            if small:
                problems.append(f"{f} @{label}: {small} tap target(s) under 44px")
            for e in errors:
                problems.append(f"{f} @{label}: console error: {e}")
            page.close()
    browser.close()

print("\n".join(problems) if problems else f"OK: {len(pages)} pages x {len(SIZES)} sizes, no problems")
sys.exit(1 if problems else 0)
