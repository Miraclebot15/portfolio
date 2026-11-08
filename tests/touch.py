#!/usr/bin/env python3
"""Touch parity checks: effects that need a mouse or a tall screen on desktop must also work on a phone.

Emulates a phone (touch, no hover) and sends touch pointer events. Run from the repo root:
    python3 tests/touch.py
Needs Playwright (pip install playwright && playwright install chromium).
"""
import os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = lambda f: "file://" + os.path.join(ROOT, f)
fails = []


def check(ok, msg):
    if not ok: fails.append(msg)


def fire(page, selector, kind, fx, fy):
    """Dispatch a touch pointer event at a fractional position inside the element."""
    page.evaluate("""([sel, kind, fx, fy]) => {
        const el = document.querySelector(sel), r = el.getBoundingClientRect();
        el.dispatchEvent(new PointerEvent(kind, {bubbles: true, cancelable: true, pointerType: 'touch', isPrimary: true,
            clientX: r.left + r.width * fx, clientY: r.top + r.height * fy}));
    }""", [selector, kind, fx, fy])


with sync_playwright() as p:
    b = p.chromium.launch()
    phone = dict(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2)

    # 1. Buttons lean toward the finger and spring back
    pg = b.new_context(**phone).new_page()
    pg.goto(URL("index.html")); pg.wait_for_timeout(600)
    check(pg.evaluate("matchMedia('(hover:none), (pointer:coarse)').matches"), "emulated phone does not report touch input")
    pg.evaluate("document.querySelector('.mag').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    fire(pg, ".mag", "pointerdown", 0.9, 0.2)
    tr = pg.evaluate("document.querySelector('.mag').style.transform")
    check("scale(0.96)" in tr and "translate(" in tr, f"button does not lean on touch (transform was '{tr}')")
    check(pg.evaluate("document.querySelector('.mag').classList.contains('tpr')"), "button does not show the press pulse")
    fire(pg, ".mag", "pointerup", 0.9, 0.2)
    check(pg.evaluate("document.querySelector('.mag').style.transform") == "", "button does not spring back after release")

    # 2. Hero photo tilts toward a press and sways with scroll
    hero = "[data-hero]"
    if pg.evaluate("!!document.querySelector('[data-hero] .hero2-photo .tilt')"):
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
        fire(pg, hero, "pointerdown", 0.95, 0.1); pg.wait_for_timeout(150)
        ry = pg.evaluate("document.querySelector('[data-hero] .tilt').style.getPropertyValue('--ry')")
        check(ry not in ("", "0deg"), f"hero photo does not tilt toward a touch (--ry was '{ry}')")
        fire(pg, hero, "pointerup", 0.95, 0.1); pg.wait_for_timeout(100)
        check(pg.evaluate("document.querySelector('[data-hero] .tilt').style.getPropertyValue('--ry')") == "0deg", "hero tilt does not reset after release")
        pg.evaluate("window.scrollTo(0,300)"); pg.wait_for_timeout(250)
        sway = pg.evaluate("document.querySelector('[data-hero] .tilt').style.getPropertyValue('--ry')")
        check(sway not in ("", "0deg"), f"hero photo does not sway while scrolling (--ry was '{sway}')")
    else:
        fails.append("hero photo tilt element not found on index.html")

    # 3. Stack cards tilt toward a press
    pg2 = b.new_context(**phone).new_page()
    pg2.goto(URL("stack.html")); pg2.wait_for_timeout(500)
    pg2.evaluate("document.querySelector(\".stkc[data-k='1']\").scrollIntoView({block:'center'})"); pg2.wait_for_timeout(1800)
    sel = ".stkc[data-k='1'] .stkc-i"
    fire(pg2, sel, "pointerdown", 0.9, 0.1); pg2.wait_for_timeout(150)
    ry = pg2.evaluate(f"document.querySelector(\"{sel}\").style.getPropertyValue('--ry')")
    check(ry not in ("", "0deg"), f"stack card does not tilt toward a touch (--ry was '{ry}')")
    fire(pg2, sel, "pointerup", 0.9, 0.1); pg2.wait_for_timeout(100)
    check(pg2.evaluate(f"document.querySelector(\"{sel}\").style.getPropertyValue('--ry')") == "0deg", "stack card tilt does not reset after release")

    # 4. People who ask their device for reduced motion get none of it
    pg3 = b.new_context(reduced_motion="reduce", **phone).new_page()
    pg3.goto(URL("index.html")); pg3.wait_for_timeout(500)
    pg3.evaluate("document.querySelector('.mag').scrollIntoView({block:'center'})")
    fire(pg3, ".mag", "pointerdown", 0.9, 0.2)
    check(pg3.evaluate("document.querySelector('.mag').style.transform") == "", "button still moves when reduced motion is requested")
    # 5. The approach story: sticky diagram on phones and short screens, pinned section on tall desktops
    def story_run(ctx, label, expect_compact):
        pgs = b.new_context(**ctx).new_page()
        pgs.goto(URL("index.html")); pgs.wait_for_timeout(700)
        compact = pgs.evaluate("document.querySelector('[data-story]').classList.contains('mstory')")
        check(compact == expect_compact, f"{label}: compact story mode is {compact}, expected {expect_compact}")
        top = pgs.evaluate("document.querySelector('[data-story]').getBoundingClientRect().top + scrollY")
        height = pgs.evaluate("document.querySelector('[data-story]').offsetHeight")
        vh = pgs.evaluate("innerHeight")
        samples = []
        for k in range(0, 16):
            y = top - vh * 0.1 + (height - vh * 0.3) * k / 15
            pgs.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})"); pgs.wait_for_timeout(160)
            samples.append(pgs.evaluate("""() => { const f = document.querySelector('.flow');
                return [+f.dataset.s, parseFloat(f.style.getPropertyValue('--ty')) || 0, document.querySelectorAll('.step.on').length, Math.round(f.getBoundingClientRect().top)]; }"""))
        s_seq = [s[0] for s in samples]
        check(s_seq == sorted(s_seq) and set(s_seq) == {0, 1, 2}, f"{label}: steps do not advance 0, 1, 2 in order while scrolling ({s_seq})")
        ty = [s[1] for s in samples]
        check(all(a <= b2 + 0.5 for a, b2 in zip(ty, ty[1:])) and ty[-1] > 200, f"{label}: the token does not travel down with the scroll ({ty})")
        if expect_compact:
            check(all(s[2] == 1 for s in samples), f"{label}: more than one step is lit at once")
            sticky = [s[3] for s in samples if s[0] == 1]
            check(bool(sticky) and all(0 <= v <= 120 for v in sticky), f"{label}: the diagram does not stay pinned while the middle step is read ({sticky})")
        return pgs

    story_run(phone, "phone story", True)
    story_run(dict(viewport={"width": 1280, "height": 700}), "short laptop story", True)
    story_run(dict(viewport={"width": 1280, "height": 900}), "tall desktop story", False)
    pr = b.new_context(reduced_motion="reduce", **phone).new_page()
    pr.goto(URL("index.html")); pr.wait_for_timeout(500)
    check(not pr.evaluate("document.querySelector('[data-story]').classList.contains('mstory')"), "reduced motion: story still uses the scroll-linked mode")
    check(pr.evaluate("[...document.querySelectorAll('.step')].every(x => x.classList.contains('on'))"), "reduced motion: story steps are not all shown")
    b.close()

if fails:
    print("touch checks failed:\n  - " + "\n  - ".join(fails)); sys.exit(1)
print("OK: touch parity (button lean, hero tilt and sway, card tilt, story on phones and short screens, reduced motion respected)")
