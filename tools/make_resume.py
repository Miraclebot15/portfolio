#!/usr/bin/env python3
"""Generate the resume PDFs (the general one and the tailored variants) from content/resume.json, the same data the resume page uses.

Requires reportlab (pip install reportlab). Run from the repo root: python3 tools/make_resume.py
Nothing here is invented: the experience and education sections appear only when entries exist in resume.json.
Fonts (Carlito, Caladea; SIL OFL) are Latin subsets in tools/fonts/.
"""
import json, os, sys
from xml.sax.saxutils import escape as esc
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
site, R = load("content/site.json"), load("content/resume.json")
notes = load("content/notes.json")

FD = os.path.join(ROOT, "tools", "fonts")
for name, f in (("Carlito", "Carlito-Regular"), ("Carlito-Bold", "Carlito-Bold"), ("Carlito-Italic", "Carlito-Italic"), ("Caladea-Bold", "Caladea-Bold")):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FD, f + ".ttf")))
pdfmetrics.registerFontFamily("Carlito", normal="Carlito", bold="Carlito-Bold", italic="Carlito-Italic", boldItalic="Carlito-Bold")

INK, MUTE, ACC, HAIR = (colors.HexColor(x) for x in ("#14110d", "#555048", "#c93810", "#cfc8b8"))
LM, RM, TM, BM = 17 * mm, 17 * mm, 12.5 * mm, 11 * mm
W = A4[0] - LM - RM
FW = W - 12  # the default frame has 6pt of padding on each side


def S(name, **k):
    return ParagraphStyle(name, fontName=k.pop("font", "Carlito"), textColor=k.pop("color", INK), **k)


st = dict(
    name=S("name", font="Caladea-Bold", fontSize=27, leading=29),
    headline=S("headline", fontSize=11.5, leading=15, color=MUTE),
    contact=S("contact", fontSize=9.6, leading=13, color=MUTE),
    h=S("h", font="Carlito-Bold", fontSize=8.8, leading=11, charSpace=1.3, spaceBefore=9.5, spaceAfter=1.5),
    body=S("body", fontSize=10, leading=14),
    pname=S("pname", font="Carlito-Bold", fontSize=10.8, leading=13.5),
    pstat=S("pstat", font="Carlito-Italic", fontSize=9, leading=13, color=MUTE, alignment=TA_RIGHT),
    ptech=S("ptech", font="Carlito-Italic", fontSize=9.2, leading=12, color=MUTE),
    pline=S("pline", fontSize=9.8, leading=13.4, spaceBefore=1, spaceAfter=1.5),
    bullet=S("bullet", fontSize=9.7, leading=13.1, leftIndent=10, bulletIndent=0, spaceAfter=1.2),
    skl=S("skl", font="Carlito-Bold", fontSize=9.7, leading=13.1),
    ski=S("ski", fontSize=9.7, leading=13.1),
)


class AccentRule(Flowable):
    """A hairline across the page with a short accent segment at the left."""
    def wrap(self, aw, ah):
        self.aw = aw
        return aw, 5
    def draw(self):
        c = self.canv
        c.setStrokeColor(HAIR); c.setLineWidth(0.6); c.line(0, 2, self.aw, 2)
        c.setStrokeColor(ACC); c.setLineWidth(2.2); c.line(0, 2, 22 * mm, 2)


def section(title):
    return [Paragraph(title.upper(), st["h"]), HRFlowable(width="100%", thickness=0.5, color=HAIR, spaceBefore=1, spaceAfter=4.5)]


def head_row(left, right):
    t = Table([[Paragraph(left, st["pname"]), Paragraph(right, st["pstat"])]], colWidths=[FW * 0.7, FW * 0.3])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t


def bullets(items):
    return [Paragraph(esc(b), st["bullet"], bulletText="\u2022") for b in items]



def render(D, out):
    """Build one PDF from a resume data dict. Returns the page count."""
    c = D["contact"]
    site_short = site["domain"].replace("https://", "")
    contact = "  \u00b7  ".join([
        f'<a href="mailto:{esc(c["email"])}" color="#14110d">{esc(c["email"])}</a>',
        f'<a href="https://wa.me/{c["whatsapp"].lstrip("+")}" color="#14110d">WhatsApp {esc(c["whatsapp_display"])}</a>',
        f'<a href="{site["domain"]}" color="#14110d">{esc(site_short)}</a>'])

    story = [Paragraph(esc(site["name"]), st["name"]), Spacer(1, 2), Paragraph(esc(D["headline"]), st["headline"]), Spacer(1, 3),
             Paragraph(contact, st["contact"]), Spacer(1, 6), AccentRule()]
    story += section("Summary") + [Paragraph(esc(D["summary"]), st["body"])]

    if D.get("experience"):
        story += section("Experience")
        for e in D["experience"]:
            sub = esc(e["org"]) + (f' \u00b7 {esc(e["location"])}' if e.get("location") else "")
            story.append(KeepTogether([head_row(f'{esc(e["role"])}', esc(e["period"])), Paragraph(sub, st["ptech"]), Spacer(1, 1.5)] + bullets(e.get("bullets", [])) + [Spacer(1, 4)]))

    story += section("Projects")
    for p in D["projects"]:
        story.append(KeepTogether([head_row(esc(p["name"]), esc(p["status"])), Paragraph(esc(p["tech"]), st["ptech"]), Paragraph(esc(p["line"]), st["pline"])] + bullets(p["bullets"]) + [Spacer(1, 4)]))

    story += section("Skills")
    rows = [[Paragraph(esc(g["label"]), st["skl"]), Paragraph(esc(", ".join(g["items"])), st["ski"])] for g in D["skills"]]
    sk = Table(rows, colWidths=[34 * mm, FW - 34 * mm])
    sk.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.6)]))
    story.append(sk)

    if D.get("education"):
        story += section("Education")
        for e in D["education"]:
            story.append(KeepTogether([head_row(esc(e["school"]), esc(e["period"])), Paragraph(esc(e["program"]) + (f' \u00b7 {esc(e["note"])}' if e.get("note") else ""), st["ptech"]), Spacer(1, 3)]))

    story.append(KeepTogether(section("Writing") + [Paragraph(f'{len(notes)} engineering notes on trust boundaries, AI agent pipelines, messaging systems and how the portfolio is built, at <a href="{site["domain"]}/engineering.html" color="#14110d">{esc(site_short)}/engineering</a>.', st["body"])]))


    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                            title=f'{site["name"]}: Resume', author=site["name"], subject="Software engineer resume", keywords="software engineer, AI agents, backend, automation")
    doc.build(story)
    return doc.page


def variant_data(v):
    """The base resume with one variant's headline, summary, project order and bullets, and skill rows."""
    base = {p["slug"]: p for p in R["projects"]}
    projects = [{**base[x["slug"]], "line": x["line"], "bullets": x["bullets"]} for x in v["projects"]]
    return {**R, "headline": v["headline"], "summary": v["summary"], "projects": projects, "skills": v["skills"]}


jobs = [(R, os.path.join(ROOT, "assets", "Miracle-Agbebaku-Resume.pdf"))]
jobs += [(variant_data(v), os.path.join(ROOT, "assets", f"Miracle-Agbebaku-Resume-{v['file']}.pdf")) for v in R.get("variants", [])]
bad = 0
for data, out in jobs:
    pages = render(data, out)
    print("wrote", os.path.relpath(out, ROOT), "| pages:", pages)
    bad += pages > 1
if bad:
    print("note: some resumes run past one page; trim bullets if you want a single page each", file=sys.stderr)
