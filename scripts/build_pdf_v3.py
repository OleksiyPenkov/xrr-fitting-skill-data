"""Build the v3 preprint PDF: preprint-v3.md -> HTML (tables) with each figure placed after the section that first
cites it -> Edge headless print-to-pdf.

Differences from build_pdf.py (v2):
  - reads preprint-v3.md;
  - seven figures, renumbered (v2's 2 to 6 are v3's 3 to 7) and captioned in the paper's specimen names
    (specimen-concordance.md), with no job id, segment number, or laboratory record name;
  - a missing figure file is reported and skipped instead of raising, so the PDF builds while Figure 2 is drawn;
  - styles the third heading level, which v3 uses for numbered subsections.

usage: python build_pdf_v3.py
"""
import os, re, base64, subprocess
import markdown

D = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(D, "preprint-v3.md")
md = open(src, encoding="utf-8").read()
FIG = os.path.join(D, "figures")

# figure number -> (file or files separated by |, caption)
# Captions rewritten for v3: paper specimen names, no job ids, no segment numbers, nm throughout.
captions = {
    1: ("fig1-parties.svg",
        "Figure 1. The three parties and what crosses each boundary. The test sessions never see the expert's "
        "reference fits or the tolerances, the expert never edits the written procedure, and the fitting server is "
        "shared by all three."),
    2: ("fig2-session-flow.svg",
        "Figure 2. Flow of sessions through both campaigns. Campaign 1 qualified the written procedure on CoC4 and "
        "CoC5 in three rounds of two fresh sessions, and then gave it unchanged to the agent. Campaign 2 applied "
        "the same artifact to six Ru/C curves in two rounds of six sessions. Dashed boxes give the reference each "
        "session was judged against."),
    3: ("fig3-baseline-CoC5.png",
        "Figure 3. A rejected baseline fit of CoC5 against the measured curve, before the written procedure existed. "
        "The fourth Bragg order is about 7 times too low and the model sits on its floor above 2.7 degrees."),
    4: ("fig4a-CoC4-session-vs-expert.png|fig4b-CoC5-session-vs-expert.png",
        "Figure 4. Stage 1, round 1. The fit each test session accepted (red) against the expert's withheld fit "
        "(blue dashed), for CoC4 (top) and CoC5 (bottom). The measured curve is shown on the session's own "
        "normalization and the expert's fit on his. Lower panels give the log residual of each fit."),
    5: ("fig5-budgets.png",
        "Figure 5. Cost of a judged two-fit session before and after the five interface changes: turns (left) and "
        "context tokens (right), log scale. Grey, the rounds run by polling; blue, the round run with a blocking "
        "wait and the per-fit report, and the agent's own session."),
    6: ("fig6-two-sigma-minima.png",
        "Figure 6. CoC4, the two roughness minima of the periodic fit. The agent's fit (red), a test session's fit "
        "carrying the expert's assignment (green), and the expert's own fit (blue dashed). Lower panels give the "
        "fringe field between orders 1 and 2 and the orders 4 to 6."),
    7: ("fig7-surface-layer.png",
        "Figure 7. CoC4, the surface-layer test on the swapped-roughness fit: without a layer (red), with a 1.26 nm "
        "carbon layer of density 0.68 g/cm³ on top (orange), and the other roughness minimum without a layer "
        "(green dashed), shown in the fringe field between orders 1 and 2, between orders 2 and 3, and at the edge."),
}

missing = [n for n, (f, _) in captions.items()
           if not all(os.path.exists(os.path.join(FIG, x)) for x in f.split("|"))]

first = {}
for n in captions:
    m = re.search(rf"Figure {n}\b", md)
    first[n] = m.start() if m else len(md)
heads = [m.start() for m in re.finditer(r"^## ", md, flags=re.M)] + [len(md)]


def section_end(pos):
    for a, b in zip(heads[:-1], heads[1:]):
        if a <= pos < b:
            return b
    return len(md)


inserts = {}
for n, pos in first.items():
    if n in missing:
        continue
    inserts.setdefault(section_end(pos), []).append(n)


def img_tag(fname):
    p = os.path.join(FIG, fname)
    data = open(p, "rb").read()
    kind = "svg+xml" if fname.endswith(".svg") else "png"
    return f'<img src="data:image/{kind};base64,{base64.b64encode(data).decode()}" style="width:100%">'


def fig_block(n):
    files, cap = captions[n]
    imgs = "".join(img_tag(f) for f in files.split("|"))
    return f'\n\n<div class="figure">{imgs}<p class="caption">{cap}</p></div>\n\n'


out, last = [], 0
for end in sorted(inserts):
    out.append(md[last:end])
    out.append("".join(fig_block(n) for n in sorted(inserts[end])))
    last = end
out.append(md[last:])
body = markdown.markdown("".join(out), extensions=["tables", "smarty"])

css = """
@page { size: A4; margin: 22mm 20mm 22mm 20mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.42; color: #111; max-width: 170mm; margin: 0 auto; }
h1 { font-size: 16pt; line-height: 1.25; margin: 0 0 6pt 0; }
h2 { font-size: 12pt; margin: 16pt 0 6pt 0; }
h3 { font-size: 10.8pt; font-style: italic; margin: 11pt 0 4pt 0; }
p { margin: 0 0 7pt 0; text-align: justify; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 9pt; }
table { border-collapse: collapse; font-size: 8.3pt; margin: 6pt 0 10pt 0; width: 100%; page-break-inside: avoid; }
th, td { border: 0.5pt solid #777; padding: 2pt 4pt; vertical-align: top; text-align: left; }
th { background: #eee; }
.figure { margin: 10pt 0 12pt 0; page-break-inside: avoid; }
.caption { font-size: 9pt; text-align: left; margin-top: 3pt; }
em { font-style: italic; }
"""
html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>preprint v3</title>"
        f"<style>{css}</style></head><body>{body}</body></html>")
hp = os.path.join(D, "preprint-v3.html")
open(hp, "w", encoding="utf-8").write(html)
pdf = os.path.join(D, "preprint-v3.pdf")
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
       f"--print-to-pdf={pdf}", "file:///" + hp.replace("\\", "/")]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
print("html", hp)
print("pdf", pdf, "exists" if os.path.exists(pdf) else "MISSING", r.returncode)
if missing:
    print("MISSING FIGURE FILES, skipped:", ", ".join(
        f"Figure {n} ({captions[n][0]})" for n in sorted(missing)))
