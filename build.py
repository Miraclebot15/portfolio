#!/usr/bin/env python3
"""Static site generator. Standard library only.

Edit content/*.json (and content/snippets/*), then run:  python3 build.py
Contact details are NOT in this file or in the HTML: they are assembled in app.js.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
SITE, PROJECTS, ICONS = load("content/site.json"), load("content/projects.json"), load("content/icons.json")
NOTES = load("content/notes.json")
TOOLS = load("content/tools.json")
DOMAIN, NAME = SITE["domain"], SITE["name"]
STACK = SITE["stack"]
STACK_ITEMS = [it for c in STACK for it in c["items"]]
STACK_ICON = {it["name"]: it["i"] for it in STACK_ITEMS if "i" in it}
STACK_LOGOS = [(it["name"], it["i"]) for it in STACK_ITEMS if "i" in it]
STACK_NAMES = [it["name"] for c in STACK if c.get("kind") != "concepts" for it in c["items"]]
BANNED_TECH = ("gemini", "qwen", "groq", "openrouter", "openai", "anthropic", "claude", "gpt", "llama", "mistral", "deepseek")
STATE_CLASS = {"Live": "live", "In development": "dev", "Coming soon": "soon"}

ALIAS = {"wa": "whatsapp", "ig": "instagram", "gh": "github"}
def ic(n, cls="ic"):
    n = ALIAS.get(n, n)
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{ICONS[n]}"/></svg>'
def esc(s): return html.escape(s, quote=True)
def fmt(s): return re.sub(r"\*\*(.+?)\*\*", r'<mark class="kw">\1</mark>', esc(s))
CHECK = "--check" in sys.argv
OUTPUTS = {}
def write(fn, s): OUTPUTS[fn] = s
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
# ---- content validation: fail early, with a clear message -----------------
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED = {"index", "stack", "portfolio", "projects", "about", "resume", "engineering", "contact", "404", "search"}
NOTE_KINDS = {"Design intent", "Implementation note"}
LANG_LABEL = {"python": "Python", "ts": "TypeScript", "js": "JavaScript", "jsx": "JSX", "html": "HTML", "css": "CSS", "bash": "Shell", "sql": "SQL", "yaml": "YAML", "json": "JSON"}
def tool_slug(n): return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")
PROJECT_REQUIRED = ["slug", "name", "state", "motif", "purpose", "summary", "points", "color", "engineering", "eng_intro"]
NOTE_REQUIRED = ["slug", "title", "lede", "read", "kind", "figure", "sections", "topics"]

def validate_content():
    errs = []
    def bad_name(n): return any(b in n.lower() for b in BANNED_TECH)
    seen = set()
    for k, p in enumerate(PROJECTS):
        w = f"projects.json[{k}] ({p.get('slug', '?')})"
        for f in PROJECT_REQUIRED:
            if not p.get(f): errs.append(f"{w}: missing field '{f}'")
        sl = p.get("slug", "")
        if not SLUG_RE.match(sl): errs.append(f"{w}: slug must be lowercase letters, digits and single hyphens")
        if sl in seen or sl in RESERVED: errs.append(f"{w}: slug '{sl}' is duplicated or reserved")
        seen.add(sl)
        if p.get("state") not in STATE_CLASS: errs.append(f"{w}: state '{p.get('state')}' must be one of {', '.join(STATE_CLASS)}")
        if p.get("motif") not in MOTIFS: errs.append(f"{w}: unknown motif '{p.get('motif')}'")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", p.get("color", "")): errs.append(f"{w}: color must look like #ff5a36")
        if p.get("url") and not p["url"].startswith("https://"): errs.append(f"{w}: url must start with https://")
        if p.get("check"):
            ck = p["check"]
            if not (ck.startswith("/api/") and os.path.isfile(os.path.join(ROOT, "api", ck[5:] + ".js"))):
                errs.append(f"{w}: check '{ck}' has no matching file in api/")
        for t in p.get("tech", []):
            if bad_name(t): errs.append(f"{w}: AI model or provider name in tech: {t}")
    seen_n = set()
    for k, n in enumerate(NOTES):
        w = f"notes.json[{k}] ({n.get('slug', '?')})"
        for f in NOTE_REQUIRED:
            if not n.get(f): errs.append(f"{w}: missing field '{f}'")
        sl = n.get("slug", "")
        if not SLUG_RE.match(sl): errs.append(f"{w}: slug must be lowercase letters, digits and single hyphens")
        if sl in seen_n or sl in seen or sl in RESERVED: errs.append(f"{w}: slug '{sl}' is duplicated or reserved")
        seen_n.add(sl)
        if n.get("kind") not in NOTE_KINDS: errs.append(f"{w}: kind must be one of {', '.join(sorted(NOTE_KINDS))}")
        if n.get("project") and n["project"] not in seen: errs.append(f"{w}: project '{n['project']}' does not exist")
        if re.search(r"\b(" + "|".join(BANNED_TECH) + r")\b", " ".join([n.get("title", ""), n.get("lede", "")] + [x for sec in n.get("sections", []) for x in sec.get("p", [])]), re.I):
            errs.append(f"{w}: AI model or provider name in the note text")
        tp = n.get("topics")
        if not (isinstance(tp, list) and 1 <= len(tp) <= 3 and all(isinstance(x, str) and x.strip() for x in tp)): errs.append(f"{w}: 'topics' needs 1 to 3 short labels")
        for m, sec in enumerate(n.get("sections", [])):
            if not sec.get("h") or not sec.get("p"): errs.append(f"{w}: section {m + 1} needs 'h' and a non-empty 'p' list")
    for c in STACK:
        if not c.get("category") or not c.get("items"): errs.append(f"site.json stack: every category needs 'category' and 'items'")
        for it in c.get("items", []):
            if bad_name(it["name"]): errs.append(f"site.json stack: AI model or provider name: {it['name']}")
            if "i" in it and it["i"] not in ICONS: errs.append(f"site.json stack: unknown icon id '{it['i']}' for {it['name']}")
    for k, v in ICONS.items():
        if not isinstance(v, str) or not v: errs.append(f"icons.json: '{k}' must be a path string")
    if not DOMAIN.startswith("https://"): errs.append("site.json: domain must start with https://")
    names = [it["name"] for c in STACK for it in c["items"]]
    slugs = [tool_slug(n) for n in names]
    for sl in {x for x in slugs if slugs.count(x) > 1}: errs.append(f"site.json stack: two items share the page name stack-{sl}.html")
    note_slugs = {n["slug"] for n in NOTES}
    ban = re.compile(r"\b(" + "|".join(BANNED_TECH) + r")\b", re.I)
    for n in names:
        t = TOOLS.get(n)
        if not t: errs.append(f"tools.json: missing entry for '{n}'"); continue
        for f in ("tag", "what", "how", "lang", "et", "code", "en"):
            if not t.get(f): errs.append(f"tools.json['{n}']: missing field '{f}'")
        if not (isinstance(t.get("uses"), list) and len(t["uses"]) == 3 and all(t["uses"])): errs.append(f"tools.json['{n}']: 'uses' needs exactly 3 entries")
        if t.get("lang") not in LANG_LABEL: errs.append(f"tools.json['{n}']: lang must be one of {', '.join(LANG_LABEL)}")
        for q in t.get("pairs", []):
            if q not in names or q == n: errs.append(f"tools.json['{n}']: pairs entry '{q}' is not another item in the stack")
        for q in t.get("notes", []):
            if q not in note_slugs: errs.append(f"tools.json['{n}']: note '{q}' does not exist")
        if ban.search(" ".join([t.get("tag", ""), t.get("what", ""), t.get("how", ""), t.get("en", "")] + list(t.get("uses", [])))):
            errs.append(f"tools.json['{n}']: AI model or provider name in the text")
    for n in TOOLS:
        if n not in names: errs.append(f"tools.json: '{n}' is not in the stack")
    if errs:
        raise SystemExit("build failed, content problems:\n  - " + "\n  - ".join(errs))
validate_content()
def motif(key, cls="motif"):
    ps = "".join(f'<path class="{c}" pathLength="1" style="--k:{i}" d="{d}"/>' for i, (d, c) in enumerate(MOTIFS[key]))
    return f'<svg class="{cls}" viewBox="0 0 200 200" aria-hidden="true" focusable="false">{ps}</svg>'

# ---- shared page chrome ------------------------------------------------
def page(fn, title, key, desc, body, nav=None, prog=False, css=None, js=None):
    nav = nav or key
    css_tag = f'\n<link rel="stylesheet" href="{css}">' if css else ""
    js_tag = f'<script src="{js}" defer></script>\n' if js else ""
    links = "".join(f'<a data-p="{k}" href="{h}"{" aria-current=\"page\"" if k == nav else ""}>{l}</a>' for k, h, l in SITE["nav"])
    big = "".join(f'<a class="big" style="--i:{i}" href="{h}"{" aria-current=\"page\"" if k == nav else ""}>{l}</a>' for i, (k, h, l) in enumerate(SITE["nav"]))
    soc = "".join(f'<a class="soc" data-c="{k}" href="#" aria-label="{l}" title="{l}">{ic(k)}</a>' for k, l in SITE["social"])
    p = '<span class="prog" aria-hidden="true"></span>' if prog else ""
    theme = ("<script>try{var t=localStorage.getItem('t');document.documentElement.dataset.theme=t||"
             "(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark')}catch(e){}</script>")
    _page = f'''<!DOCTYPE html>
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
<link rel="stylesheet" href="styles.css">{css_tag}
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
{js_tag}</body>
</html>
'''
    write(fn, add_markers(_page))

# ---- animated section markers (replace the old dash before labels) -------
MARKERS = [
 '<svg viewBox="0 0 32 32" class="v0"><g class="mrot"><circle class="ln" cx="16" cy="16" r="12.5" stroke-dasharray="2 3.2"/><g class="idle orb"><circle class="pt" cx="16" cy="3.5" r="2.5"/></g></g><g class="st"><rect class="ln idle brt" x="11" y="11" width="10" height="10" rx="2"/></g></svg>',
 '<svg viewBox="0 0 32 32" class="v1"><g class="mrot"><path class="ln tri" d="M16 5 27 24H5Z"/><circle class="pt n1" cx="16" cy="5" r="2.4"/><circle class="pt n2" cx="27" cy="24" r="2.4"/><circle class="pt n3" cx="5" cy="24" r="2.4"/></g></svg>',
 '<svg viewBox="0 0 32 32" class="v2"><g class="mrot"><path class="ln" d="M3 16H29M9 11v10M16 11v10M23 11v10"/></g><g class="st"><rect class="pt tok" x="5" y="12.5" width="7" height="7" rx="1.6"/></g></svg>',
 '<svg viewBox="0 0 32 32" class="v3"><g class="mrot"><path class="ln hexp" d="M16 3 27 9.5V22.5L16 29 5 22.5V9.5Z"/></g><g class="st"><circle class="pt hb" cx="16" cy="16" r="3.2"/></g></svg>']
def add_markers(h):
    h = h.replace('<span class="dot"></span>', "")
    n = [0]
    def rep(m):
        s = MARKERS[n[0] % len(MARKERS)]; n[0] += 1
        return m.group(1) + f'<span class="mk" aria-hidden="true">{s}</span>'
    return re.sub(r'(<p class="(?:eyebrow|kicker)"[^>]*>)', rep, h)

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
    g = "".join(f'<span class="tc">{ic(i)}{esc(n)}</span>' for n, i in (STACK_LOGOS[::-1] if rev else STACK_LOGOS))
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
<div class="wrap" style="display:flex;flex-wrap:wrap;gap:12px"><button class="btn pz" id="pause" aria-pressed="false">{ic("pause","ic pa")}{ic("play","ic pl")}<span class="lbl">Pause motion</span></button><a class="btn" style="margin-top:16px" href="stack.html">Explore the full stack{ic("right")}</a></div></section>'''
stack_band = f'''<section class="sec tech" style="padding-top:0"><div class="wrap"><p class="eyebrow rv">Technologies</p><h2 class="rv">The tools behind the work.</h2><p class="lede rv">Every tool I build with, grouped by category, with the project pages that list each one.</p><a class="btn pri rv" href="stack.html">Explore the full stack{ic("right")}</a></div></section>'''
cta = f'''<section class="wrap sec" style="padding-top:0"><h2 class="ctaBig rv">Let’s build something.</h2><div class="cta"><a class="btn pri mag up" data-c="wa" href="#">{ic("wa")}Message on WhatsApp</a><a class="btn mag up" data-c="mail" href="#">{ic("mail")}Send an email</a></div></section>'''
page("portfolio.html", f"Portfolio | {NAME}", "portfolio", "Selected software projects and engineering work by Miracle Agbebaku.", hero + band + build + code + work + stack_band + cta)


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
WORDS = ["AI agents", "Backend systems", "Messaging automation", "Developer tooling", "Product engineering", "Orchestration"]
def tape_words(rev=False):
    ws = WORDS[::-1] if rev else WORDS
    return "".join(f"<span>{esc(w)}</span>" for w in ws * 2)
TAPE = (f'<div class="tapes" aria-hidden="true"><div class="tape a"><div class="tk"><div>{tape_words()}</div><div>{tape_words()}</div></div></div>'
        f'<div class="tape b"><div class="tk"><div>{tape_words(True)}</div><div>{tape_words(True)}</div></div></div></div>')
RAIL = "".join(f'''<article class="rcard" style="--pc:{p["color"]}"><div class="rtop"><span class="rnum">{pnum(i)}</span>{motif(p["motif"])}</div><div><h3><a href="{p["slug"]}.html" translate="no">{esc(p["name"])}</a></h3><p>{esc(p["purpose"])}</p></div><div class="rfoot">{chip(p["state"], p.get("check"))}{(f'<a class="live-link" href="{p["url"]}" target="_blank" rel="noopener noreferrer">Open {ic("ext")}<span class="sr">(opens in a new tab)</span></a>') if p.get("url") else ""}</div></article>''' for i, p in enumerate(PROJECTS))
landing = (open(os.path.join(ROOT, "content/landing.html"), encoding="utf-8").read()
           .replace("{PHOTO_HERO}", HERO_PHOTO).replace("{TAPE}", TAPE).replace("{RAIL_CARDS}", RAIL).replace("{TECH}", tech)
           .replace("{ARROW}", ARROW).replace("{WA}", ic("wa")).replace("{MAIL}", ic("mail")))
page("index.html", f"{NAME} | Software & AI Systems", "home", "Miracle Agbebaku builds AI systems, software products, automation and the engineering behind them.", landing)

# ---- projects list -----------------------------------------------------
rows = "".join(f'''<li data-d="{STATE_CLASS[p["state"]]}"><a class="prow" href="{p["slug"]}.html" style="--pc:{p["color"]}"><span class="pn">{pnum(i)}</span><h3 style="view-transition-name:p-{p["slug"]}">{esc(p["name"])}</h3><p class="pp">{esc(p["purpose"])}</p><span class="side"><span class="pm" aria-hidden="true">{motif(p["motif"])}</span>{chip(p["state"], p.get("check"))}<span class="ar">{ic("right")}</span></span></a></li>''' for i, p in enumerate(PROJECTS))
page("projects.html", f"Projects | {NAME}", "projects", "Projects by Miracle Agbebaku: AI orchestration, messaging assistants, customer care, UI tooling and more.",
 f'''<div class="wrap phead"><p class="eyebrow">Work</p><h1><span class="ml"><span class="mw">Projects</span></span></h1><p class="lede">What each project is for. Open one for the full picture.</p>
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
    summ = "".join(f'<p class="lede" style="font-size:18px">{fmt(x)}</p>' for x in p["summary"].split("\n\n"))
    built = ("<h2 class=\"h3s\">Built with</h2>" + tech_tags(p["tech"])) if p.get("tech") else ""
    eng = ""
    if p.get("engineering"):
        items = "".join(f'<li class="st" style="--i:{k}"><button class="hb" aria-expanded="{"true" if k == 0 else "false"}" aria-controls="e{k}"><span class="en">{k+1:02d}</span><span class="et">{esc(e["t"])}</span>{ic("right")}</button><div class="dt" id="e{k}"><div><p>{fmt(e["d"])}</p></div></div></li>' for k, e in enumerate(p["engineering"]))
        eng = f'<h2 class="h3s">Engineering concerns</h2><p class="lede" style="font-size:16px">{esc(p["eng_intro"])}</p><ol class="eng">{items}</ol>'
    body = f'''<div class="wrap phead"><a class="back" href="projects.html">{ic("right")}Projects</a><p class="eyebrow" style="display:flex">{pnum(i)}</p><h1 style="view-transition-name:p-{p["slug"]}"><span class="ml"><span class="mw">{esc(p["name"])}</span></span></h1><div class="chips" style="margin-bottom:{"6px" if p.get("check") else "18px"}">{chip(p["state"], p.get("check"))}</div>{"<p class=\"cap\" style=\"margin:0 0 18px\">" + esc(p.get("check_note", "Live status checks whether the deployed website responds.")) + "</p>" if p.get("check") else ""}<p class="lede">{esc(p["purpose"])}</p><div class="cta" style="margin-top:6px">{live}</div></div>
<div class="wrap pgrid"><div><h2 class="h3s" style="margin-top:20px">About</h2>{summ}<h2 class="h3s">What it’s for</h2><ul class="plain">{pts}</ul>{flow(p["flow"]) if p.get("flow") else ""}{eng}{built}</div>
<div class="side"><div class="motifbox" style="--pc:{p["color"]}">{motif(p["motif"])}</div></div></div>
<div class="wrap" style="padding-bottom:50px"><a class="nextp" href="{nxt["slug"]}.html"><small>Next project</small><span>{esc(nxt["name"])}{ic("right")}</span></a></div>'''
    page(f'{p["slug"]}.html', f'{p["name"]} | {NAME}', "case", p["purpose"], body, nav="projects", prog=True)

# ---- other pages -------------------------------------------------------
def ph(eyebrow, h, lede=""): return f'<div class="wrap phead"><p class="eyebrow">{eyebrow}</p><h1><span class="ml"><span class="mw">{h}</span></span></h1>{f"<p class=\"lede\">{lede}</p>" if lede else ""}</div>'

# ---- Stack pages: the map (stack.html) and one deep-dive page per item ----
ORDER = [it["name"] for c in STACK for it in c["items"]]
CAT_OF = {it["name"]: c["category"] for c in STACK for it in c["items"]}
KIND_OF = {it["name"]: c.get("kind") for c in STACK for it in c["items"]}
TOOL_FILE = {n: f"stack-{tool_slug(n)}.html" for n in ORDER}
NOTE_BY = {n["slug"]: n for n in NOTES}
PROJ_OF = {}
for _p in PROJECTS:
    for _t in _p.get("tech", []):
        PROJ_OF.setdefault(_t.lower(), []).append({"n": _p["name"], "h": _p["slug"] + ".html"})

def tool_icon(n):
    return ic(STACK_ICON[n]) if n in STACK_ICON else f'<span class="tmono" aria-hidden="true">{esc(n[0])}</span>'

def stack_card(k, c):
    concepts = c.get("kind") == "concepts"
    items = ""
    for j, it in enumerate(c["items"]):
        n = esc(it["name"])
        cls = "sb" + (" cn" if concepts else "") + ("" if "i" in it or concepts else " nlg")
        inner = f'<a class="{cls}" href="{TOOL_FILE[it["name"]]}" data-n="{n}" data-c="{esc(c["category"])}">{ic(it["i"]) if "i" in it else ""}<span>{n}</span></a>'
        items += f'<li style="--j:{j};--bd:{5 + (j * 7) % 4}s">{inner}</li>'
    orb = '<svg class="sorb" viewBox="0 0 200 200" aria-hidden="true"><circle cx="100" cy="100" r="86" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="3 7"/><circle cx="100" cy="100" r="56" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="2 9"/><circle cx="186" cy="100" r="5" fill="var(--acc)"/><circle cx="44" cy="148" r="4" fill="currentColor"/><circle cx="120" cy="44" r="3" fill="currentColor"/></svg>' if concepts else ""
    blurb = f'<p>{esc(c["blurb"])}</p>' if c.get("blurb") else ""
    return (f'<section class="stkc rv{" wide" if concepts else ""}" style="--i:{k % 4}" data-k="{k}" aria-labelledby="stk{k}">'
            f'<div class="stkc-i">{orb}<h3 id="stk{k}">{esc(c["category"])}</h3>{blurb}<ul>{items}</ul></div></section>')

_tools = sum(1 for c in STACK if c.get("kind") != "concepts" for _ in c["items"])
_linked = sum(1 for n in STACK_NAMES if PROJ_OF.get(n.lower()))
_stats = "".join(f'<div><b data-count="{n}">{n}</b><span>{l}</span></div>' for n, l in ((len(STACK), "categories"), (_tools, "tools"), (_linked, "listed on project pages")))
_rail = '<div class="frail" role="group" aria-label="Filter by category"><button class="fp" type="button" data-f="all" aria-pressed="true">All</button>' + "".join(f'<button class="fp" type="button" data-f="{k}" aria-pressed="false">{esc(c["category"])}</button>' for k, c in enumerate(STACK)) + '</div>'
_head = ph("Stack", "The full stack.", "Every tool and design idea behind my work, grouped by what it does. Tap one for a quick look, then open the deep dive for how it works and an example.")
assert _head.startswith('<div class="wrap phead">') and _head.endswith("</div>")
_head = _head.replace('<div class="wrap phead">', f'<div class="wrap phead"><a class="back" href="portfolio.html">{ic("right")}Portfolio</a>', 1)[:-6] + f'<div class="stats rv">{_stats}</div></div>'
_sheet = (f'<div class="sheet" id="sheet" role="dialog" aria-labelledby="sh-name" aria-modal="false"><button class="sh-x" id="sh-x" type="button" aria-label="Close details">{ic("close")}</button>'
          '<div class="sh-ic" id="sh-ic" aria-hidden="true"></div><p class="sh-cat" id="sh-cat"></p><h2 id="sh-name"></h2><p class="sh-tag" id="sh-tag"></p>'
          f'<a class="btn pri sh-go" id="sh-go" href="stack.html">Open the deep dive{ic("right")}</a>'
          '<p class="sh-lbl" id="sh-lbl"></p><ul class="sh-list" id="sh-list"></ul></div>')
_usage = json.dumps({n.lower(): {"p": PROJ_OF.get(n.lower(), []), "t": TOOLS[n]["tag"], "h": TOOL_FILE[n]} for n in ORDER}, ensure_ascii=False).replace("</", "<\\/")
page("stack.html", f"The full stack | {NAME}", "stack", "Every tool and design idea behind my work, grouped by category, with a deep dive for each: what it is, how it works, an example and where it appears.",
     _head + '<div class="wrap">' + _rail + '<div class="stkg">' + "".join(stack_card(k, c) for k, c in enumerate(STACK)) + '</div>'
     f'<button class="btn pz" id="pause" aria-pressed="false">{ic("pause", "ic pa")}{ic("play", "ic pl")}<span class="lbl">Pause motion</span></button></div>'
     + _sheet + f'<script type="application/json" id="stack-usage">{_usage}</script>',
     nav="portfolio", css="stack.css", js="stack.js")

LAYERS = [("overview", "Overview"), ("how", "How it works"), ("example", "Example"), ("work", "In my work")]

def chip_link(n):
    return f'<li><a class="tchip" href="{TOOL_FILE[n]}">{ic(STACK_ICON[n]) if n in STACK_ICON else ""}{esc(n)}</a></li>'

def nx(k):
    return f'<button class="nx" type="button" data-go="{LAYERS[k + 1][0]}">Next layer: {LAYERS[k + 1][1]}</button>' if k < len(LAYERS) - 1 else ""

def tool_page(i, n):
    t, cat = TOOLS[n], CAT_OF[n]
    concept = KIND_OF[n] == "concepts"
    uses = "".join(f'<li style="--j:{j}">{esc(u)}</li>' for j, u in enumerate(t["uses"]))
    lines = "".join(f'<span class="cl" style="--l:{j}">{esc(l) if l else chr(8203)}</span>' for j, l in enumerate(t["code"].split("\n")))
    pairs = "".join(chip_link(q) for q in t["pairs"])
    projects = PROJ_OF.get(n.lower(), [])
    if projects:
        work = '<h2 class="lh">Listed on these project pages</h2><ul class="tchips">' + "".join(f'<li><a class="tchip" href="{x["h"]}">{esc(x["n"])}</a></li>' for x in projects) + '</ul>'
    elif concept:
        work = '<p class="tbig">This is a design idea rather than a product, so it is not tied to a project\u2019s tech list.' + (' The engineering notes below show it applied.' if t["notes"] else '') + '</p>'
    else:
        work = '<p class="tbig">No project page lists this yet.</p>'
    if t["notes"]:
        work += '<h2 class="lh">Related engineering notes</h2><ul class="tchips">' + "".join(f'<li><a class="tchip" href="{q}.html">{esc(NOTE_BY[q]["title"])}</a></li>' for q in t["notes"]) + '</ul>'
    sibs = [q for q in ORDER if CAT_OF[q] == cat and q != n]
    if sibs: work += f'<h2 class="lh">More in {esc(cat)}</h2><ul class="tchips">' + "".join(chip_link(q) for q in sibs) + '</ul>'
    tabs = "".join(f'<button class="ltab" type="button" role="tab" id="t-{k}" aria-controls="{k}" aria-selected="{"true" if j == 0 else "false"}" tabindex="{0 if j == 0 else -1}" data-l="{k}"><b>{j + 1}</b><span>{v}</span></button>' for j, (k, v) in enumerate(LAYERS))
    panels = (
        f'<section class="lp shown" id="overview" role="tabpanel" aria-labelledby="t-overview"><p class="tbig">{esc(t["what"])}</p><h2 class="lh">What you use it for</h2><ul class="uses">{uses}</ul>{nx(0)}</section>'
        f'<section class="lp" id="how" role="tabpanel" aria-labelledby="t-how"><p class="tbig">{esc(t["how"])}</p><h2 class="lh">Pairs well with</h2><ul class="tchips">{pairs}</ul>{nx(1)}</section>'
        f'<section class="lp" id="example" role="tabpanel" aria-labelledby="t-example"><h2 class="lh">{esc(t["et"])}</h2>'
        f'<div class="cb" data-code="{esc(t["code"])}"><div class="ch"><span>{LANG_LABEL[t["lang"]]}</span><button class="cp" type="button" aria-label="Copy the example">Copy</button></div><pre tabindex="0"><code>{lines}</code></pre></div><p class="cnote">{esc(t["en"])}</p>{nx(2)}</section>'
        f'<section class="lp" id="work" role="tabpanel" aria-labelledby="t-work">{work}</section>')
    prev_n, next_n = ORDER[i - 1], ORDER[(i + 1) % len(ORDER)]
    nav_ = (f'<nav class="tnav" aria-label="More from the stack"><a class="tn" href="{TOOL_FILE[prev_n]}"><span>Previous</span><b>{esc(prev_n)}</b></a>'
            f'<a class="tn nxt" href="{TOOL_FILE[next_n]}"><span>Next</span><b>{esc(next_n)}</b></a></nav>')
    head = (f'<div class="wrap phead tp"><a class="back" href="stack.html">{ic("right")}The full stack</a><p class="eyebrow">{esc(cat)}</p>'
            f'<div class="thd"><span class="tic">{tool_icon(n)}</span><h1><span class="ml"><span class="mw">{esc(n)}</span></span></h1></div><p class="lede">{esc(t["tag"])}</p></div>')
    page(TOOL_FILE[n], f"{n} | The full stack | {NAME}", "stack", f'{t["tag"]} Overview, how it works, a worked example and where it appears in my projects.',
         head + f'<div class="wrap tool"><div class="lay" role="tablist" aria-label="Layers of detail">{tabs}</div>{panels}{nav_}</div>',
         nav="portfolio", css="stack.css", js="tool.js")

for _i, _n in enumerate(ORDER):
    tool_page(_i, _n)
about_markup = """
<div class="wrap about2-head">
<div><p class="kicker"><span class="dot"></span>About the developer</p>
<h1 class="h1d"><span class="ml"><span class="mw">Built with intent. <span class="it">Engineered to work.</span></span></span></h1>
<p class="lead">I’m Miracle Agbebaku, a developer focused on AI systems, agent orchestration, backend engineering and complete products. I care about how a system behaves when real users, messy inputs and failure meet.</p>
<div class="tags2"><span>AI systems</span><span>Product engineering</span><span>Automation</span></div></div>
<div class="pwrap">{ABOUT_PHOTO}</div>
</div>
<div class="wrap a2rows">
<div class="a2row rv"><b>01</b><div><p class="kicker">What I build</p><h2>From model output to useful software.</h2></div><p>I work across AI and agentic systems, backend APIs, full-stack applications, conversational automation and developer tooling. The interface matters, but so do architecture, observability, security boundaries and recovery when something breaks.</p></div>
<div class="a2row rv"><b>02</b><div><p class="kicker">How I think</p><h2>Understand the failure path.</h2></div><div><p>I prefer to trace how a system actually behaves before changing it. I test assumptions, look for edge cases, and value reliable behavior over flashy demos. I’m building my foundations in computer science while exploring the deeper engineering behind intelligent systems.</p><a class="btn mag" href="projects.html">Explore the projects {ARROW}</a></div></div>
<div class="a2row rv"><b>03</b><div><p class="kicker">Principles</p><h2>Make failure legible.</h2></div><ul class="plain"><li>Prefer invariants that code enforces over rules people remember.</li><li>Keep state explicit and observable, so behavior can be explained after the fact.</li><li>Draw boundaries where trust changes, and validate everything that crosses them.</li><li>Make changes small and reversible, and treat a passing demo as weak evidence.</li><li>Have systems state only what they can verify about themselves.</li></ul></div>
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
RESUME_PDF = "assets/Miracle-Agbebaku-Resume.pdf"
SUMMARY = "Software developer working on AI systems, agent orchestration, backend engineering and complete products. I care about how a system behaves when real users, messy inputs and failure meet."
FOCUS = ["AI agents and orchestration", "Backend, APIs and integrations", "Frontend with React, Next.js and TypeScript", "Messaging automation and developer tooling"]
paper_projects = "".join(f'<div class="rp"><dt><a href="{p["slug"]}.html" translate="no">{esc(p["name"])}</a><span>{p["state"]}</span></dt><dd>{esc(p["purpose"])}</dd></div>' for p in PROJECTS)
paper = f'''<article class="paper rv" aria-label="Resume of {NAME}"><header><h2 class="pname" translate="no">{NAME}</h2><p class="prole">Software developer · AI systems, backend and automation</p>
<p class="plinks"><a href="{DOMAIN}">{DOMAIN.replace("https://", "")}</a> · <a data-c="gh" href="#">GitHub</a> · <a data-c="x" href="#">X</a></p></header>
<section><h3>Summary</h3><p>{SUMMARY}</p></section>
<section><h3>Focus</h3><ul>{"".join(f"<li>{x}</li>" for x in FOCUS)}</ul></section>
<section><h3>Selected projects</h3><dl>{paper_projects}</dl></section>
<section><h3>Technologies</h3><p>{", ".join(STACK_NAMES)}</p></section></article>'''
page("resume.html", f"Resume | {NAME}", "resume", "Resume of Miracle Agbebaku: summary, focus, projects and technologies. View it here or download the PDF.",
 ph("Resume", "Resume", "Read it here, or take it with you.") +
 f'''<div class="wrap" style="padding-bottom:80px"><div class="cta rv" style="margin:0 0 34px"><a class="btn pri mag" href="{RESUME_PDF}" download>Download PDF {ic("download")}</a><a class="btn mag" href="{RESUME_PDF}" target="_blank" rel="noopener noreferrer">Open PDF {ic("ext")}<span class="sr">(opens in a new tab)</span></a><button class="btn mag" id="print" type="button">Print</button></div>{paper}</div>''')
def figure(f):
    lis, k = "", 0
    for idx, l in enumerate(f["labels"]):
        if l.startswith("BOUNDARY:"):
            lis += f'<li class="fb" style="--i:{idx}"><span>{esc(l[9:])}</span></li>'
        else:
            k += 1
            lis += f'<li class="fs" style="--i:{idx}"><b>{k:02d}</b><span>{esc(l)}</span></li>'
    return f'<figure class="fig rv"><ol class="fig-st">{lis}</ol><figcaption>{esc(f["caption"])}</figcaption></figure>'
NOTE_TOOLS = {n["slug"]: [t for t in ORDER if n["slug"] in TOOLS[t]["notes"]] for n in NOTES}
TOPICS = []
for _n in NOTES:
    for _t in _n["topics"]:
        if _t not in TOPICS: TOPICS.append(_t)
def note_proj(n): return next((p for p in PROJECTS if p["slug"] == n["project"]), None)
note_cards = "".join(
    f'''<a class="note-card" href="{n["slug"]}.html" data-topics="{esc("|".join(n["topics"]))}"><span class="mono">{n["kind"]} \u00b7 {n["read"]}{(" \u00b7 " + esc(note_proj(n)["name"])) if note_proj(n) else ""}</span><h3>{esc(n["title"])}</h3><p>{esc(n["lede"])}</p><span class="etags">{"".join(f'<i class="etag">{esc(t)}</i>' for t in n["topics"])}</span><span class="note-go">Read {ic("right")}</span></a>''' for n in NOTES)
rpath = ('<section class="erp rv" aria-labelledby="erp-h"><h2 class="erp-h" id="erp-h">Reading path</h2><p class="erp-s">Start with the principle, follow one system end to end, see where it goes next, then the smaller notes.</p><ol class="erp-l">'
         + "".join(f'<li style="--i:{k}"><a href="{n["slug"]}.html"><b>{k + 1:02d}</b><span>{esc(n["title"])}</span><small>{n["kind"]} \u00b7 {n["read"]}</small></a></li>' for k, n in enumerate(NOTES)) + '</ol></section>')
efil = ('<div class="efil" role="group" aria-label="Filter notes by topic"><button class="ef" type="button" data-t="all" aria-pressed="true">All</button>'
        + "".join(f'<button class="ef" type="button" data-t="{esc(t)}" aria-pressed="false">{esc(t)}</button>' for t in TOPICS) + f'</div><p class="ecount" aria-live="polite">{len(NOTES)} notes</p>')
page("engineering.html", f"Engineering | {NAME}", "engineering", "Design and implementation notes on the systems behind the projects, with a reading path and topic filters.",
 ph("Journal", "Engineering", "Design intent and implementation notes: trust boundaries, an agent pipeline end to end, routing, availability checks and how this site is built.") +
 f'<div class="wrap" style="padding-bottom:90px">{rpath}{efil}<div class="notes enotes">{note_cards}</div></div>', css="eng.css", js="eng.js")
for k, n in enumerate(NOTES):
    nxt = NOTES[(k + 1) % len(NOTES)]
    proj = note_proj(n)
    toc = "".join(f'<li><a href="#s{m+1}">{esc(s["h"])}</a></li>' for m, s in enumerate(n["sections"]))
    secs = "".join(f'<h2 id="s{m+1}"><span class="sn">{m+1:02d}</span>{esc(s["h"])}</h2>' + "".join(f"<p>{fmt(t)}</p>" for t in s["p"]) for m, s in enumerate(n["sections"]))
    cta = (f'<a class="btn mag" href="{proj["slug"]}.html">About {esc(proj["name"])} {ic("right")}</a>' if proj else f'<a class="btn mag" href="projects.html">See the projects {ic("right")}</a>')
    used = NOTE_TOOLS[n["slug"]]
    nstk = (f'<aside class="nstk" aria-labelledby="nstk-h"><h2 class="nstk-h" id="nstk-h">Stack behind this note</h2><ul class="nstk-l">' + "".join(f'<li><a href="{TOOL_FILE[t]}">{ic(STACK_ICON[t]) if t in STACK_ICON else ""}{esc(t)}</a></li>' for t in used) + '</ul></aside>') if used else ""
    page(f'{n["slug"]}.html', f'{n["title"]} | {NAME}', "engineering", n["lede"],
     ph(f'{n["kind"]} \u00b7 {n["read"]}', esc(n["title"]), esc(n["lede"])) +
     f'''<div class="wrap note-wrap"><aside class="toc" aria-label="On this page"><p class="mono">On this page</p><ol>{toc}</ol></aside><div><article class="prose">{figure(n["figure"])}{secs}<p>{cta}</p>{nstk}</article>
<a class="nextp" href="{nxt["slug"]}.html"><small>Next note</small><span>{esc(nxt["title"])}</span></a></div></div>''', nav="engineering", prog=True, css="eng.css")
page("contact.html", f"Contact | {NAME}", "contact", "Ways to contact Miracle Agbebaku.",
 ph("Contact", "Say hello", "The fastest way to reach me is WhatsApp. The other channels work too.") +
 '<div class="wrap" style="padding-bottom:80px">' + "".join(f'<a class="crow" data-c="{k}" href="#">{ic(k)}<b>{l}</b>{ic("ext")}</a>' for k, l in [("wa", "WhatsApp"), ("mail", "Email"), ("x", "X"), ("ig", "Instagram"), ("gh", "GitHub")]) + '</div>')
page("404.html", f"Not found | {NAME}", "none", "Page not found.", ph("404", "Not found", "That page doesn’t exist.") + f'<div class="wrap" style="padding-bottom:80px"><a class="btn pri" href="index.html">Back home {ic("right")}</a></div>')

# ---- static files ------------------------------------------------------
write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0b0b0d"/><path d="M14 48V16h6l12 20 12-20h6v32h-6V28L32 48 20 28v20z" fill="#ff5a36"/></svg>')
NOINDEX = {"404.html", "search.html"}
pages = [f for f in sorted(OUTPUTS) if f.endswith(".html") and f not in NOINDEX]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{DOMAIN}/{'' if f == 'index.html' else f}</loc></url>\n" for f in pages) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
write("vercel.json", json.dumps({"headers": [{"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}, {"key": "X-Frame-Options", "value": "DENY"}]}]}, indent=2) + "\n")

# ---- output validation: runs on everything before anything is written -----
def validate_output():
    errs = []
    ids = {}
    html_files = {f: t for f, t in OUTPUTS.items() if f.endswith(".html")}
    for f, t in html_files.items():
        ids[f] = re.findall(r'\sid="([^"]+)"', t)
    def exists(path):
        return path in OUTPUTS or os.path.isfile(os.path.join(ROOT, path))
    for f, t in OUTPUTS.items():
        if "\u2014" in t or "\u2013" in t: errs.append(f"{f}: em or en dash found")
    for f, t in html_files.items():
        if len(re.findall(r"<h1[\s>]", t)) != 1: errs.append(f"{f}: needs exactly one h1")
        m = re.search(r"<title>([^<]*)</title>", t)
        if not m or not m.group(1).strip(): errs.append(f"{f}: missing title")
        d = re.search(r'<meta name="description" content="([^"]*)"', t)
        if not d or not d.group(1).strip(): errs.append(f"{f}: missing meta description")
        elif len(html.unescape(d.group(1))) > 200: errs.append(f"{f}: meta description is longer than 200 characters")
        for ph in re.findall(r"\{[A-Z][A-Z_]{2,}\}", t): errs.append(f"{f}: unreplaced placeholder {ph}")
        dup = {i for i in ids[f] if ids[f].count(i) > 1}
        if dup: errs.append(f"{f}: duplicate ids: {', '.join(sorted(dup))}")
        for u in re.findall(r'\b(?:href|src)="([^"]*)"', t):
            if not u or re.match(r"(https?:|mailto:|tel:|data:|javascript:|//)", u): continue
            path, _, frag = u.partition("#")
            path = path.split("?")[0]
            if not path:
                if frag and frag not in ids[f]: errs.append(f"{f}: anchor #{frag} not found on this page")
                continue
            if not exists(path): errs.append(f"{f}: broken link or asset '{u}'"); continue
            if frag and path.endswith(".html") and frag not in ids.get(path, []): errs.append(f"{f}: anchor '{u}' not found")
    if errs:
        raise SystemExit("build failed, output problems:\n  - " + "\n  - ".join(errs[:40]) + (f"\n  ... and {len(errs) - 40} more" if len(errs) > 40 else ""))

GENERATED_ROOT = re.compile(r".*\.html$")
def read_disk(fn):
    path = os.path.join(ROOT, fn)
    return open(path, encoding="utf-8", newline="").read() if os.path.isfile(path) else None

validate_output()
if CHECK:
    stale = [f for f, t in sorted(OUTPUTS.items()) if read_disk(f) != t]
    orphans = [f for f in sorted(os.listdir(ROOT)) if GENERATED_ROOT.match(f) and f not in OUTPUTS]
    if stale or orphans:
        print("build --check failed")
        for f in stale: print("  stale or missing:", f)
        for f in orphans: print("  orphan (not generated any more):", f)
        print("Run python3 build.py and commit the result.")
        raise SystemExit(1)
    print(f"OK: {len(OUTPUTS)} generated files are up to date")
else:
    for fn, t in OUTPUTS.items():
        open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(t)
    print("built", len([f for f in OUTPUTS if f.endswith(".html")]), "pages")
