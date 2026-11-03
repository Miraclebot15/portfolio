#!/usr/bin/env python3
"""Performance budgets: gzip size of every page, the stylesheet and script, and image weights.

Run from the repo root:  python3 tests/budgets.py
Raise a budget on purpose, in this file, when a feature really needs the room.
"""
import glob, gzip, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = 1024
PAGE_GZ = {"index.html": 45 * KB, "portfolio.html": 45 * KB}
DEFAULT_PAGE_GZ = 16 * KB
CSS_GZ, JS_GZ = 22 * KB, 20 * KB
IMAGE_MAX = {".webp": 120 * KB, ".jpg": 200 * KB, ".png": 40 * KB}
IMAGES_TOTAL = 700 * KB


def gz(path):
    return len(gzip.compress(open(path, "rb").read(), 9))


def main():
    rows, bad = [], []
    def check(name, size, limit):
        rows.append((name, size, limit))
        if size > limit: bad.append(f"{name}: {size / KB:.1f} KB is over the {limit / KB:.0f} KB budget")
    for f in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        n = os.path.basename(f)
        check(n + " (gzip)", gz(f), PAGE_GZ.get(n, DEFAULT_PAGE_GZ))
    check("styles.css (gzip)", gz(os.path.join(ROOT, "styles.css")), CSS_GZ)
    check("app.js (gzip)", gz(os.path.join(ROOT, "app.js")), JS_GZ)
    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "assets", "images", "*"))):
        size = os.path.getsize(f); total += size
        limit = IMAGE_MAX.get(os.path.splitext(f)[1].lower())
        if limit: check("images/" + os.path.basename(f), size, limit)
    check("all images", total, IMAGES_TOTAL)
    width = max(len(r[0]) for r in rows)
    for name, size, limit in rows:
        print(f"{name:<{width}}  {size / KB:7.1f} KB  / {limit / KB:5.0f} KB  {'OVER' if size > limit else 'ok'}")
    if bad:
        print("\nBudget problems:\n  - " + "\n  - ".join(bad)); sys.exit(1)
    print(f"OK: {len(rows)} budgets met")


if __name__ == "__main__":
    main()
