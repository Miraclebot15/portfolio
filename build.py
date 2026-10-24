#!/usr/bin/env python3
"""Static site generator. Standard library only.

Edit content/*.json (and content/snippets/*), then run:  python3 build.py
Contact details are NOT in this file or in the HTML: they are assembled in app.js.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
SITE, PROJECTS, ICONS = load("content/site.json"), load("content/projects.json"), load("content/icons.json")
DOMAIN, NAME = SITE["domain"], SITE["name"]
STACK_ICON = {n: i for n, i in SITE["stack"]}
STATE_CLASS = {"Live": "live", "In development": "dev", "Coming soon": "soon"}

ALIAS = {"wa": "whatsapp", "ig": "instagram", "gh": "github"}
def ic(n, cls="ic"):
    n = ALIAS.get(n, n)
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{ICONS[n]}"/></svg>'
def esc(s): return html.escape(s, quote=True)
def write(fn, s): open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(s)
def chip(state, check=None):
    c = f' data-check="{check}" aria-live="polite"' if check else ""
    return f'<span class="chip {STATE_CLASS[state]}"{c}><i></i><b class="lbl">{state}</b></span>'

# ---- code highlighting -------------------------------------------------
def highlight(code, lang):
    kw = {"py": r"from|import|class|def|return|not|or|and|if|else|for|in|True|False|None",
          "cpp": r"struct|return|const|auto|for|int|bool|char|std"}[lang]
    com = r"#[^\n]*" if lang == "py" else r"//[^\n]*"
    pre = r"^\#include[^\n]*" if lang == "cpp" else r"(?!x)x"
    rx = re.compile(rf"(?P<c>{com})|(?P<p>{pre})|(?P<s>\"(?:\\.|[^\"\\])*\")|(?P<d>@\w+)|(?P<k>\b(?:{kw})\b)|(?P<n>\b\d+\b)", re.M)
    out, i = [], 0
    for m in rx.finditer(code):
        out.append(esc(code[i:m.start()]))
        cls = {"c": "c", "p": "k", "s": "s", "d": "k", "k": "k", "n": "n"}[m.lastgroup]
        out.append(f'<span class="{cls}">{esc(m.group())}</span>')
        i = m.end()
    out.append(esc(code[i:]))
    return "".join(out)

# ---- motifs (animated SVG line art that hints at each project's purpose)
def circ(cx, cy, r): return f"M{cx-r} {cy}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0"
MOTIFS = {
 "nexus": [("M40 24h120a8 8 0 0 1 8 8v26a8 8 0 0 1-8 8H40a8 8 0 0 1-8-8V32a8 8 0 0 1 8-8z",""),("M12 104h74M114 104h74","a"),("M100 70v68m-9-9l9 9 9-9","a"),("M36 138h56v42H36zM108 138h56v42h-56z","")],
 "ella": [("M26 38h96a10 10 0 0 1 10 10v34a10 10 0 0 1-10 10H70l-20 18V92H26a10 10 0 0 1-10-10V48a10 10 0 0 1 10-10z",""),("M140 64h22l18-26M162 64h30M162 64l18 26","a"),("M150 128h30a8 8 0 0 1 8 8v16a8 8 0 0 1-8 8h-8l-10 10v-10h-12a8 8 0 0 1-8-8v-16a8 8 0 0 1 8-8z","")],
 "carecore": [("M44 22h112v156H44z",""),("M66 62h68M66 88h68M66 114h40",""),("M146 136a16 16 0 1 0 .01 0","a"),("M138 136l6 6 12-12","a")],
 "atelier": [("M30 30h140v140H30z",""),("M30 76h140M84 76v94",""),("M118 118l26 26m-4-34l14-14","a")],
 "engine": [("M100 26l62 36v72l-62 36-62-36V62z",""),("M38 62l62 36 62-36M100 98v72","a")],
 "agent": [(circ(42,152,12),""),(circ(100,100,12),""),(circ(158,48,12),"a"),("M50 142l42-32M108 90l42-32",""),("M136 150l10 10 20-20","a")],
 "lagoon": [(circ(82,88,44),""),(circ(122,88,44),"a"),(circ(102,122,44),"")],
 "aurora": [("M24 56h92M24 86h138M24 116h64M24 146h112",""),("M112 32v140","a"),("M104 40l8-8 8 8","a")]}
def motif(key, cls="motif"):
    ps = "".join(f'<path class="{c}" pathLength="1" style="--k:{i}" d="{d}"/>' for i, (d, c) in enumerate(MOTIFS[key]))
    return f'<svg class="{cls}" viewBox="0 0 200 200" aria-hidden="true" focusable="false">{ps}</svg>'

# ---- shared page chrome ------------------------------------------------
def page(fn, title, key, desc, body, nav=None, prog=False):
    nav = nav or key
    links = "".join(f'<a data-p="{k}" href="{h}"{" aria-current=\"page\"" if k == nav else ""}>{l}</a>' for k, h, l in SITE["nav"])
    big = "".join(f'<a class="big" style="--i:{i}" href="{h}"{" aria-current=\"page\"" if k == nav else ""}>{l}</a>' for i, (k, h, l) in enumerate(SITE["nav"]))
    soc = "".join(f'<a class="soc" data-c="{k}" href="#" aria-label="{l}" title="{l}">{ic(k)}</a>' for k, l in SITE["social"])
    p = '<span class="prog" aria-hidden="true"></span>' if prog else ""
    theme = ("<script>try{var t=localStorage.getItem('t');document.documentElement.dataset.theme=t||"
             "(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark')}catch(e){}</script>")
    write(fn, f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{DOMAIN}/{fn}">
<meta property="og:url" content="{DOMAIN}/{fn}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0b0b0d">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
{theme}
<link rel="stylesheet" href="styles.css">
</head>
<body data-page="{key}">
<a class="skip" href="#main">Skip to content</a>{p}
<header class="top"><div class="bar"><a class="brand" href="index.html" translate="no">{NAME}</a>
<nav class="links" aria-label="Main">{links}</nav>
<div class="tools"><div class="site-language" id="site-language"><button class="site-language-trigger" id="site-language-trigger" type="button" aria-haspopup="dialog" aria-expanded="false" aria-controls="site-language-panel" aria-label="Change website language"><span aria-hidden="true">文</span><span id="site-language-current">EN</span><span aria-hidden="true">⌄</span></button><div class="site-language-panel" id="site-language-panel" role="dialog" aria-label="Choose website language" hidden><label for="site-language-search">WEBSITE LANGUAGE</label><input id="site-language-search" type="search" placeholder="Search languages…" autocomplete="off"><div id="site-language-options" class="site-language-options" role="listbox" aria-label="Languages"></div><p>Translation provided by Google Translate.</p></div></div><button class="ib" id="theme" aria-label="Toggle light and dark theme" aria-pressed="false">{ic("sun","ic i-sun")}{ic("moon","ic i-moon")}</button><button class="ib mb" id="mb" aria-label="Open menu" aria-expanded="false" aria-controls="menu">{ic("menu")}</button></div></div></header>
<div class="menu" id="menu" role="dialog" aria-label="Menu"><button class="ib x" id="mx" aria-label="Close menu">{ic("close")}</button>{big}<div class="socs">{soc}</div></div>
<main id="main">
{body}
</main>
<div class="wrap"><footer class="ft"><span>© {SITE["year"]} {NAME}</span><div class="socs" role="group" aria-label="Contact links">{soc}</div></footer></div>
<noscript><p style="text-align:center;color:var(--mute)">Contact links need JavaScript enabled.</p></noscript>
<div id="google_translate_element" hidden></div><script>function googleTranslateElementInit(){{if(window.google&&google.translate){{new google.translate.TranslateElement({{pageLanguage:"en",includedLanguages:"af,sq,am,ar,hy,az,eu,be,bn,bs,bg,ca,ceb,zh-CN,zh-TW,hr,cs,da,nl,eo,et,fi,fr,gl,ka,de,el,gu,ht,ha,he,hi,hu,is,id,ga,it,ja,jv,kn,kk,km,ko,ku,ky,lo,la,lv,lt,mk,ms,ml,mt,mi,mr,mn,my,ne,no,ps,fa,pl,pt,pa,ro,ru,sr,si,sk,sl,so,es,su,sw,sv,tg,ta,te,th,tr,uk,ur,uz,vi,cy,yi,yo,zu",autoDisplay:false}},"google_translate_element");}}}}</script><script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit" defer></script><script src="app.js"></script>
</body>
</html>
''')

def letters(name):
    out, n = "", 0
    for w in name.split():
        s = ""
        for c in w:
            s += f'<span class="l" style="--i:{n}">{c}</span>'; n += 1
        out += f'<span class="ln" aria-hidden="true">{s}</span>'
    return out

def tech_tags(names):
    return '<div class="tags">' + "".join(f'<span class="tag">{ic(STACK_ICON[n]) if n in STACK_ICON else ""}{esc(n)}</span>' for n in names) + '</div>'

def pnum(i): return f"{i+1:02d}"

def pcard(i, p):
    live = f'<a class="btn up" href="{p["url"]}" target="_blank" rel="noopener noreferrer">{esc(p.get("link_label","Open live"))} {ic("ext")}<span class="sr">(opens in a new tab)</span></a>' if p.get("url") else ""
    return f'''<article class="pcard" style="--i:{i}"><div><span class="pn">{pnum(i)}</span><h3>{esc(p["name"])}</h3><p class="pp">{esc(p["purpose"])}</p><div class="chips">{chip(p["state"], p.get("check"))}</div><div class="go"><a class="btn pri" href="{p["slug"]}.html">View project {ic("right")}</a>{live}</div></div><div class="mo">{motif(p["motif"])}</div></article>'''

# ---- home --------------------------------------------------------------
snip = {k: open(os.path.join(ROOT, f"content/snippets/authorize.{k}"), encoding="utf-8").read().rstrip("\n") for k in ("py", "cpp")}
gate_items = [(44, "pass", "0s"), (128, "block", "1.3s"), (212, "pass", "2.6s"), (296, "block", "3.9s")]
gate = "".join(f'<rect class="it" x="{x}" y="38" width="58" height="36" rx="9" style="--k:{k};--d:{d}"/>' for x, k, d in gate_items)
ticks = "".join(f'<path d="M{x} 224v16" stroke="var(--mute)" stroke-width="1.5"/>' for x in range(40, 400, 40))
slots = ''.join(f'<rect class="slot" x="{x}" y="306" width="58" height="36" rx="9"/>' for x in (44, 212))
gate_svg = f'''<figure class="gate" aria-label="Illustration: a model proposes actions, and a boundary decides which may run"><svg viewBox="0 0 420 470" role="img" aria-hidden="true"><text x="22" y="22">Propose</text>{slots}{gate}<path class="ln2" d="M20 232H400"/>{ticks}<text x="398" y="216" text-anchor="end">Authorize</text><text x="22" y="452">Run</text></svg></figure>'''
names2 = "".join(f"<span>{esc(p['name'])}</span>" for p in PROJECTS)
band = f'<div class="band" aria-hidden="true"><div class="track"><div>{names2}</div><div class="dup">{names2}</div></div></div>'
def tech_row(rev):
    g = "".join(f'<span class="tc">{ic(i)}{esc(n)}</span>' for n, i in (SITE["stack"][::-1] if rev else SITE["stack"]))
    return f'<div class="row2{" rev" if rev else ""}"><div>{g}</div><div aria-hidden="true">{g}</div></div>'
hero = f'''<section class="wrap hero heroWrap"><div><p class="eyebrow">Software engineer</p>
<h1 class="name" aria-label="{NAME}">{letters(NAME)}</h1>
<p class="sub"><span class="sr">{esc(SITE["tagline"])}</span><span aria-hidden="true">I build <b class="rot" data-w="AI agents|backend systems|messaging assistants|developer tools">AI agents</b><i class="caret"></i></span></p>
<div class="cta"><a class="btn pri mag" href="projects.html">See projects {ic("right")}</a><a class="btn mag" href="contact.html">Get in touch</a></div></div>
{gate_svg}<a class="cue" href="#build" aria-label="Scroll to the next section">{ic("down")}</a></section>'''
build = f'''<section class="wrap sec" id="build"><div class="stm"><div class="rv"><p class="eyebrow">What I build</p><h2>Systems that act, with limits.</h2><p class="lede">I work on AI agents, the backends behind them, and the interfaces and tools around them.</p></div>
<div class="row3"><div class="rv" style="--i:1"><b>01</b><h3>AI agents and orchestration</h3><p>Systems where a model proposes and separate controls decide what runs.</p></div>
<div class="rv" style="--i:2"><b>02</b><h3>Backends and integrations</h3><p>APIs, databases and messaging integrations designed around failure handling.</p></div>
<div class="rv" style="--i:3"><b>03</b><h3>Interfaces and tooling</h3><p>React, Next.js and TypeScript front ends, and tools that speed up development.</p></div></div></div></section>'''
code = f'''<section class="wrap sec" style="padding-top:0"><div class="stm"><div class="rv"><p class="eyebrow">The idea</p><h2>A model proposes. Something else decides.</h2><p class="lede">This is the principle behind NEXUS CORE, written as a few lines in two languages.</p></div>
<div class="rv" style="--i:1"><div class="code" id="code"><div class="ctop"><div class="tabs" role="tablist" aria-label="Language"><button role="tab" aria-selected="true" data-file="authorize.py">Python</button><button role="tab" aria-selected="false" data-file="authorize.cpp">C++</button></div><div class="cact"><span id="cfile" class="sr">authorize.py</span><button id="skip" hidden>Skip</button><button id="replay">Replay</button></div></div>
<div aria-hidden="true"><pre class="cb">{highlight(snip["py"], "py")}</pre><pre class="cb" hidden>{highlight(snip["cpp"], "cpp")}</pre></div>
<pre class="sr">Python version:
{esc(snip["py"])}

C++ version:
{esc(snip["cpp"])}</pre></div><p class="cap">An illustration of the idea, not NEXUS CORE’s source code.</p></div></div></section>'''
work = f'''<section class="wrap sec" style="padding-top:0"><p class="eyebrow rv">Selected work</p><h2 class="rv">Projects.</h2><div class="cards">{"".join(pcard(i, p) for i, p in enumerate(PROJECTS[:4]))}</div><p class="cta"><a class="btn mag" href="projects.html">All projects {ic("right")}</a></p></section>'''
tech = f'''<section class="sec tech" style="padding-top:0"><div class="wrap"><p class="eyebrow rv">Technologies</p><h2 class="rv">The tools behind the work.</h2></div>
<div class="mq" role="group" aria-label="Technologies used across my projects">{tech_row(False)}{tech_row(True)}</div>
<div class="wrap"><button class="btn pz" id="pause" aria-pressed="false">{ic("pause","ic pa")}{ic("play","ic pl")}<span class="lbl">Pause motion</span></button></div></section>'''
cta = f'''<section class="wrap sec" style="padding-top:0"><h2 class="ctaBig rv">Let’s build something.</h2><div class="cta"><a class="btn pri mag up" data-c="wa" href="#">{ic("wa")}Message on WhatsApp</a><a class="btn mag up" data-c="mail" href="#">{ic("mail")}Send an email</a></div></section>'''
page("portfolio.html", f"Portfolio | {NAME}", "portfolio", "Selected software projects and engineering work by Miracle Agbebaku.", hero + band + build + code + work + tech + cta)


# ---- photos (responsive WebP with JPEG fallback) -------------------------
def photo(name, alt, ratio, sizes, eager=False, caption=""):
    w, h = ratio
    cap = f"<figcaption>{esc(caption)}</figcaption>" if caption else ""
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="ph" style="--ar:{w}/{h}"><picture>'
            f'<source type="image/webp" srcset="assets/images/{name}-640.webp 640w, assets/images/{name}-960.webp 960w" sizes="{sizes}">'
            f'<img src="assets/images/{name}-960.jpg" width="960" height="{round(960*h/w)}" alt="{esc(alt)}" {load} decoding="async"></picture>{cap}</figure>')
HERO_PHOTO = photo("miracle-hero", "Miracle Agbebaku", (4, 5), "(max-width: 900px) 70vw, 420px", eager=True)
ABOUT_PHOTO = photo("miracle-about", "Miracle Agbebaku", (1, 1), "(max-width: 900px) 90vw, 430px")
ARROW = ic("right")
TICKER = "".join(f"<span>{esc(w)}</span>" for w in ["AI agents", "Backend systems", "Messaging automation", "Developer tooling", "Product engineering", "Orchestration"])
RAIL = "".join(f'''<article class="rcard"><div class="rtop"><span class="rnum">{pnum(i)}</span>{motif(p["motif"])}</div><div><h3><a href="{p["slug"]}.html" translate="no">{esc(p["name"])}</a></h3><p>{esc(p["purpose"])}</p></div><div class="rfoot">{chip(p["state"], p.get("check"))}{(f'<a class="live-link" href="{p["url"]}" target="_blank" rel="noopener noreferrer">Open {ic("ext")}<span class="sr">(opens in a new tab)</span></a>') if p.get("url") else ""}</div></article>''' for i, p in enumerate(PROJECTS))
landing = (open(os.path.join(ROOT, "content/landing.html"), encoding="utf-8").read()
           .replace("{PHOTO_HERO}", HERO_PHOTO).replace("{TICKER}", TICKER).replace("{RAIL_CARDS}", RAIL).replace("{TECH}", tech)
           .replace("{ARROW}", ARROW).replace("{WA}", ic("wa")).replace("{MAIL}", ic("mail")))
page("index.html", f"{NAME} | Software & AI Systems", "home", "Miracle Agbebaku builds AI systems, software products, automation and the engineering behind them.", landing)

# ---- projects list -----------------------------------------------------
rows = "".join(f'''<li data-d="{STATE_CLASS[p["state"]]}"><a class="prow" href="{p["slug"]}.html"><span class="pn">{pnum(i)}</span><h3 style="view-transition-name:p-{p["slug"]}">{esc(p["name"])}</h3><p class="pp">{esc(p["purpose"])}</p><span class="side">{chip(p["state"], p.get("check"))}<span class="ar">{ic("right")}</span></span></a></li>''' for i, p in enumerate(PROJECTS))
page("projects.html", f"Projects | {NAME}", "projects", "Projects by Miracle Agbebaku: AI orchestration, messaging assistants, customer care, UI tooling and more.",
 f'''<div class="wrap phead"><p class="eyebrow">Work</p><h1>Projects</h1><p class="lede">What each project is for. Open one for the full picture.</p>
<div class="filters" role="group" aria-label="Filter by status"><button data-f="all" aria-pressed="true">All</button><button data-f="live" aria-pressed="false">Live</button><button data-f="dev" aria-pressed="false">In development</button><button data-f="soon" aria-pressed="false">Coming soon</button></div><p class="count" id="cnt" aria-live="polite">{len(PROJECTS)} projects</p></div>
<div class="wrap" style="padding-bottom:60px"><ul class="plist">{rows}</ul></div>''')

# ---- project pages -----------------------------------------------------
def flow(f):
    out = ""
    for i, (n, t) in enumerate(f["steps"]):
        out += (f'<li class="bd" style="--i:{i}">{esc(t)}</li>' if n == "BOUNDARY" else
                f'<li class="st" style="--i:{i}"><button class="hb" aria-expanded="false" aria-controls="s{i}">{esc(n)}{ic("right")}</button><div class="dt" id="s{i}"><div><p>{esc(t)}</p></div></div></li>')
    return f'<h2 class="h3s">{esc(f["title"])}</h2><p class="lede" style="font-size:16px">{esc(f["note"])}</p><ol class="pipe">{out}</ol>'
for i, p in enumerate(PROJECTS):
    nxt = PROJECTS[(i + 1) % len(PROJECTS)]
    live = f'<a class="btn pri up" href="{p["url"]}" target="_blank" rel="noopener noreferrer">{esc(p.get("link_label","Open live"))} {ic("ext")}<span class="sr">(opens in a new tab)</span></a>' if p.get("url") else ""
    pts = "".join(f"<li>{esc(x)}</li>" for x in p["points"])
    body = f'''<div class="wrap phead"><a class="back" href="projects.html">{ic("right")}Projects</a><p class="eyebrow" style="display:flex">{pnum(i)}</p><h1 style="view-transition-name:p-{p["slug"]}">{esc(p["name"])}</h1><div class="chips" style="margin-bottom:{"6px" if p.get("check") else "18px"}">{chip(p["state"], p.get("check"))}</div>{"<p class=\"cap\" style=\"margin:0 0 18px\">" + esc(p.get("check_note", "Live status checks whether the deployed website responds.")) + "</p>" if p.get("check") else ""}<p class="lede">{esc(p["purpose"])}</p><div class="cta" style="margin-top:6px">{live}</div></div>
<div class="wrap pgrid"><div><h2 class="h3s" style="margin-top:20px">About</h2><p class="lede" style="font-size:18px">{esc(p["summary"])}</p><h2 class="h3s">What it’s for</h2><ul class="plain">{pts}</ul>{("<h2 class=\"h3s\">Built with</h2>" + tech_tags(p["tech"])) if p.get("tech") else ""}{flow(p["flow"]) if p.get("flow") else ""}</div>
<div class="side"><div class="motifbox">{motif(p["motif"])}</div></div></div>
<div class="wrap" style="padding-bottom:50px"><a class="nextp" href="{nxt["slug"]}.html"><small>Next project</small><span>{esc(nxt["name"])}{ic("right")}</span></a></div>'''
    page(f'{p["slug"]}.html', f'{p["name"]} | {NAME}', "case", p["purpose"], body, nav="projects", prog=True)

# ---- other pages -------------------------------------------------------
def ph(eyebrow, h, lede=""): return f'<div class="wrap phead"><p class="eyebrow">{eyebrow}</p><h1>{h}</h1>{f"<p class=\"lede\">{lede}</p>" if lede else ""}</div>'
about_markup = """
<div class="wrap about2-head">
<div><p class="kicker"><span class="dot"></span>About the developer</p>
<h1 class="h1d">Built with intent. <span class="it">Engineered to work.</span></h1>
<p class="lead">I’m Miracle Agbebaku, a developer focused on AI systems, agent orchestration, backend engineering and complete products. I care about how a system behaves when real users, messy inputs and failure meet.</p>
<div class="tags2"><span>AI systems</span><span>Product engineering</span><span>Automation</span></div></div>
<div class="pwrap">{ABOUT_PHOTO}</div>
</div>
<div class="wrap a2rows">
<div class="a2row rv"><b>01</b><div><p class="kicker">What I build</p><h2>From model output to useful software.</h2></div><p>I work across AI and agentic systems, backend APIs, full-stack applications, conversational automation and developer tooling. The interface matters, but so do architecture, observability, security boundaries and recovery when something breaks.</p></div>
<div class="a2row rv"><b>02</b><div><p class="kicker">How I think</p><h2>Understand the failure path.</h2></div><div><p>I prefer to trace how a system actually behaves before changing it. I test assumptions, look for edge cases, and value reliable behavior over flashy demos. I’m building my foundations in computer science while exploring the deeper engineering behind intelligent systems.</p><a class="btn mag" href="projects.html">Explore the projects {ARROW}</a></div></div>
</div>
<div class="wrap">
<p class="kicker">Try it</p>
<section class="tw" id="terminal" aria-labelledby="tw-t">
<div class="tw-head"><div class="tw-title"><span class="tw-mark" aria-hidden="true" translate="no">M/</span><div><strong id="tw-t">Interactive profile</strong><small>Runs in your browser, read-only</small></div></div><span class="tw-status"><i></i><span id="tw-state">Ready</span></span></div>
<div class="tw-body">
<div class="tw-code">
<div class="tw-langs" id="tw-pills" role="group" aria-label="Choose a language"><span class="tw-select"><label class="sr" for="tw-all">All languages</label><select id="tw-all" translate="no"></select><span aria-hidden="true">▾</span></span></div>
<div class="tw-filebar"><span id="tw-file" translate="no">profile.py</span><button class="tw-copy" id="tw-copy" type="button">Copy</button></div>
<div class="tw-editor" translate="no"><div class="tw-gut" id="tw-gut" aria-hidden="true">1</div><pre class="tw-pre" id="tw-pre" tabindex="0" aria-label="Code sample"><code></code></pre></div>
</div>
<div class="tw-session">
<div class="tw-chips" role="group" aria-label="Run a command"><button class="tw-chip" type="button" data-cmd="help">help</button><button class="tw-chip" type="button" data-cmd="about">about</button><button class="tw-chip" type="button" data-cmd="projects">projects</button><button class="tw-chip" type="button" data-cmd="principles">principles</button><button class="tw-chip" type="button" data-cmd="now">now</button><button class="tw-chip" type="button" data-cmd="links">links</button><button class="tw-chip" type="button" data-cmd="clear">clear</button></div>
<div class="tw-out" id="tw-out" role="log" aria-live="polite" tabindex="0" aria-label="Terminal output"></div>
<form class="tw-form" id="tw-form" autocomplete="off"><label for="tw-in" aria-hidden="true">&rsaquo;</label><input id="tw-in" type="text" autocapitalize="none" spellcheck="false" placeholder="Type a command" aria-label="Command"><button type="submit">Run</button></form>
<p class="tw-foot">A small interactive profile. No shell access, and nothing you type is sent to a server.</p>
</div>
</div>
</section>
</div>
<script type="application/json" id="project-data">{PROJECT_JSON}</script>
"""
PROJECT_JSON = json.dumps([{"name": p["name"], "slug": p["slug"], "state": p["state"]} for p in PROJECTS]).replace("</", "<\\/")
page("about.html", f"About | {NAME}", "about", "About Miracle Agbebaku: AI systems, product engineering, automation and future robotics.", about_markup.replace("{ABOUT_PHOTO}", ABOUT_PHOTO).replace("{ARROW}", ic("right")).replace("{PROJECT_JSON}", PROJECT_JSON))
stack_chips = "".join(f'<span class="tag">{ic(i)}{esc(n)}</span>' for n, i in SITE["stack"])
prow_links = "".join(f'<li><a href="{p["slug"]}.html">{esc(p["name"])}</a>: {esc(p["purpose"])}</li>' for p in PROJECTS)
page("resume.html", f"Resume | {NAME}", "resume", "Summary, focus areas and projects.",
 ph("Resume", "Resume", "Software developer working on AI agents, backend systems and developer tooling.") +
 f'''<div class="wrap" style="padding-bottom:70px"><h2 class="h3s">Focus</h2><ul class="plain"><li>AI agents and orchestration</li><li>Backend, APIs and integrations</li><li>Frontend with React, Next.js and TypeScript</li><li>Messaging automation and developer tooling</li></ul>
<h2 class="h3s">Technologies</h2><div class="stk">{stack_chips}</div><h2 class="h3s">Projects</h2><ul class="plain">{prow_links}</ul>
<h2 class="h3s">Links</h2><a class="crow" data-c="gh" href="#">{ic("gh")}<b>GitHub</b>{ic("ext")}</a><a class="crow" data-c="mail" href="#">{ic("mail")}<b>Email</b>{ic("ext")}</a></div>''')
page("engineering.html", f"Engineering | {NAME}", "engineering", "Technical write-ups and notes.",
 ph("Journal", "Engineering", "Technical write-ups, architecture notes and debugging stories.") +
 '<div class="wrap" style="padding-bottom:80px"><div class="soon"><p><strong>Coming soon.</strong></p><p>The first write-ups are planned on how NEXUS CORE separates planning from execution, and how ELLA decides where a message should go.</p></div></div>')
page("contact.html", f"Contact | {NAME}", "contact", "Ways to contact Miracle Agbebaku.",
 ph("Contact", "Say hello", "The fastest way to reach me is WhatsApp. The other channels work too.") +
 '<div class="wrap" style="padding-bottom:80px">' + "".join(f'<a class="crow" data-c="{k}" href="#">{ic(k)}<b>{l}</b>{ic("ext")}</a>' for k, l in [("wa", "WhatsApp"), ("mail", "Email"), ("x", "X"), ("ig", "Instagram"), ("gh", "GitHub")]) + '</div>')
page("404.html", f"Not found | {NAME}", "none", "Page not found.", ph("404", "Not found", "That page doesn’t exist.") + f'<div class="wrap" style="padding-bottom:80px"><a class="btn pri" href="index.html">Back home {ic("right")}</a></div>')

# ---- static files ------------------------------------------------------
write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0e1114"/><path d="M14 48V16h6l12 20 12-20h6v32h-6V28L32 48 20 28v20z" fill="#6fe0c0"/></svg>')
pages = [f for f in sorted(os.listdir(ROOT)) if f.endswith(".html") and f != "404.html"]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{DOMAIN}/{'' if f == 'index.html' else f}</loc></url>\n" for f in pages) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
write("vercel.json", json.dumps({"headers": [{"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}, {"key": "X-Frame-Options", "value": "DENY"}]}]}, indent=2) + "\n")
print("built", len(pages) + 1, "pages")
