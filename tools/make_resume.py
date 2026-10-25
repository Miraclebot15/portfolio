#!/usr/bin/env python3
"""Generate assets/Miracle-Agbebaku-Resume.pdf from the same content the site uses.

Requires reportlab (pip install reportlab). Run from the repo root: python3 tools/make_resume.py
Nothing here is invented: sections appear only when the content exists.
"""
import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
site = json.load(open(os.path.join(ROOT, "content/site.json"), encoding="utf-8"))
projects = json.load(open(os.path.join(ROOT, "content/projects.json"), encoding="utf-8"))
ACC, INK, MUTE = colors.HexColor("#c93810"), colors.HexColor("#14110d"), colors.HexColor("#5d584f")
SUMMARY = ("Software developer working on AI systems, agent orchestration, backend engineering and complete products. "
           "I care about how a system behaves when real users, messy inputs and failure meet.")
FOCUS = ["AI agents and orchestration", "Backend, APIs and integrations",
         "Frontend with React, Next.js and TypeScript", "Messaging automation and developer tooling"]
LINKS = [("Portfolio", site["domain"]), ("GitHub", "https://github.com/Miraclebot15"), ("X", "https://x.com/MiracleTechX")]

S = lambda n, **k: ParagraphStyle(n, fontName=k.pop("font", "Helvetica"), textColor=k.pop("color", INK), **k)
name = S("name", font="Helvetica-Bold", fontSize=27, leading=30)
role = S("role", fontSize=11.5, leading=15, color=MUTE)
links = S("links", fontSize=9.5, leading=14, color=MUTE)
h = S("h", font="Helvetica-Bold", fontSize=8.5, leading=12, color=ACC, spaceBefore=14, spaceAfter=5, charSpace=1.6)
body = S("body", fontSize=10, leading=14.5)
pname = S("pname", font="Helvetica-Bold", fontSize=10.5, leading=14)
pdesc = S("pdesc", fontSize=9.6, leading=13.5, color=MUTE, spaceAfter=7, leftIndent=0)
bullet = S("bullet", fontSize=10, leading=14.5, leftIndent=11, bulletIndent=0)

story = [Paragraph(site["name"], name), Spacer(1, 3), Paragraph("Software developer · AI systems, backend and automation", role), Spacer(1, 5),
         Paragraph("  ·  ".join(f'{l}: <a href="{u}" color="#c93810">{u.replace("https://", "")}</a>' for l, u in LINKS), links),
         Spacer(1, 8), HRFlowable(width="100%", thickness=1.4, color=ACC, spaceAfter=2)]
story += [Paragraph("SUMMARY", h), Paragraph(SUMMARY, body), Paragraph("FOCUS", h)]
story += [Paragraph(t, bullet, bulletText="•") for t in FOCUS]
story.append(Paragraph("SELECTED PROJECTS", h))
for p in projects:
    story.append(KeepTogether([Paragraph(f'{p["name"]} <font color="#5d584f" size="8.5">· {p["state"]}</font>', pname), Paragraph(p["purpose"], pdesc)]))
story += [Paragraph("TECHNOLOGIES", h), Paragraph(", ".join(n for n, _ in site["stack"]), body)]

out = os.path.join(ROOT, "assets/Miracle-Agbebaku-Resume.pdf")
doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=19*mm, rightMargin=19*mm, topMargin=17*mm, bottomMargin=16*mm,
                        title="Miracle Agbebaku: Resume", author=site["name"], subject="Software developer resume")
doc.build(story)
print("wrote", out)
