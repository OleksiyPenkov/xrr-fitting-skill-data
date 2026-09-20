"""Regenerate the six manuscript figures of the XRR-Fitting-Skill preprint (v3) with
de-identified rendered text.

Regenerates, into D:\\MultilayerLab\\Papers\\XRR-Fitting-Skill\\figures\\ only:

    fig3-baseline-CoC5.png             a rejected baseline fit of CoC5 vs the measured curve
    fig4a-CoC4-session-vs-expert.png   round-1 test session vs the expert's withheld fit, CoC4
    fig4b-CoC5-session-vs-expert.png   round-1 test session vs the expert's withheld fit, CoC5
    fig5-budgets.png                   turns and context tokens per judged two-fit session
    fig6-two-sigma-minima.png          CoC4, the two roughness minima of the periodic fit
    fig7-surface-layer.png             CoC4, the surface-layer test on the swapped-roughness fit

Why this script exists
----------------------
The images previously sitting under those names were renamed copies of laboratory-record
figures. Their rendered pixels still carried record specimen names (P2-0x, 2609xxA), job ids,
session labels, segment numbers, tool names and Angstrom values, none of which may appear in
the manuscript. The printed captions in build_pdf_v3.py are already correct, so this script
changes TEXT ONLY: every plotted value, data source, colour, line style, panel layout, axis
scale and axis limit is identical to the record scripts it was adapted from.

Source it was adapted from (READ ONLY; this script never writes there)
---------------------------------------------------------------------
    ...\\LLM-XRay-Optics-Lab\\experiments\\skill-dev-2026-09-18\\overlay_vs_author.py  -> fig 4a, 4b
    ...\\LLM-XRay-Optics-Lab\\experiments\\skill-dev-2026-09-18\\p204_sigma_minima.py  -> fig 6
    ...\\LLM-XRay-Optics-Lab\\experiments\\skill-dev-2026-09-18\\p204_cap_figure.py    -> fig 7
    ...\\XRR-Fitting-Skill\\figure4_budgets.py                                         -> fig 5

Figure 3 has no surviving generating script. It was rebuilt here from the record data of the
rejected baseline fit (measured.dat, calc.dat, residual.dat of that job, plus the raw counts
curve from the inbox, scaled by the scale factor recorded in that job's request.json). The
reconstruction was validated pixel-by-pixel against the record image: the zoom panel and the
residual panel reproduce it exactly, and the full-range panel differs only in antialiasing on
the single-pixel noise spikes of the raw curve. The axis limits of figure 3 were recovered by
measuring the record image's spines and tick positions, since no script states them.

Run:  python make_figures_v3.py        (from anywhere; all paths are absolute)
"""

import os
import zipfile

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- absolute paths
PAPER = r"D:\MultilayerLab\Papers\XRR-Fitting-Skill"
OUT = os.path.join(PAPER, "figures")
E = r"D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments"          # READ ONLY
AUTHREF = os.path.join(E, "runs", "exp-03", "author-reference")

RESULTS = []


def announce(path, written, why=""):
    RESULTS.append((path, written, why))
    state = "WRITTEN" if written else "SKIPPED"
    print(f"{state:8s} {path}" + (f"   ({why})" if why else ""))


def require(paths):
    """Return the list of the given paths that do not exist."""
    return [p for p in paths if not os.path.exists(p)]


def load_xrcx_curve(z, name):
    """Identical to overlay_vs_author.py: read a curve out of an .xrcx archive."""
    t = z.read(name).decode("utf-8", "replace").replace(",", ".")
    rows = []
    for line in t.splitlines():
        p = line.split()
        try:
            rows.append((float(p[0]), float(p[1])))
        except (ValueError, IndexError):
            pass
    a = np.array(rows)
    if a[-1, 0] > 5:  # 2theta file
        a[:, 0] /= 2
    return a


# ---------------------------------------------------------------- figure 3
def figure3():
    out = os.path.join(OUT, "fig3-baseline-CoC5.png")
    jd = os.path.join(E, "runs", "exp-03", "workdir", "jobs", "fit-20260918-144637-1bcc")
    raw_path = os.path.join(E, "runs", "exp-03", "workdir", "inbox", "P2-05", "xrr.dat")
    need = [os.path.join(jd, "measured.dat"), os.path.join(jd, "calc.dat"),
            os.path.join(jd, "residual.dat"), raw_path]
    miss = require(need)
    if miss:
        announce(out, False, "missing input: " + "; ".join(miss))
        return

    m = np.loadtxt(os.path.join(jd, "measured.dat"), skiprows=1)
    c = np.loadtxt(os.path.join(jd, "calc.dat"), skiprows=1)
    r = np.loadtxt(os.path.join(jd, "residual.dat"), skiprows=1)
    raw = np.loadtxt(raw_path)              # column 0 is 2theta, column 1 is counts
    SCALE = 9.3e-7                          # the scale recorded in that job's request.json

    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(10, 11))
    a1.semilogy(raw[:, 0] / 2, raw[:, 1] * SCALE, color="0.6", lw=0.7, label="raw × 9.3e-7")
    a1.semilogy(m[:, 0], m[:, 1], color="black", lw=0.9, label="measured as fitted")
    a1.semilogy(c[:, 0], c[:, 1], color="red", lw=0.9, label="rejected baseline fit")
    a1.set_xlim(0.15, 3.70)
    a1.set_ylim(1e-7, 1.25)
    a1.legend(loc="upper right")

    a2.semilogy(m[:, 0], m[:, 1], color="black", lw=0.9)
    a2.semilogy(c[:, 0], c[:, 1], color="red", lw=0.9)
    a2.set_xlim(0.28, 1.3)
    a2.set_ylim(3e-5, 0.5)
    a2.set_title("zoom 0.28-1.3 deg")       # a region, not a specimen: kept

    a3.plot(r[:, 0], r[:, 1], color="blue", lw=0.8)
    a3.axhline(0, color="k", lw=0.5)
    a3.set_ylim(-1, 1)
    a3.set_xlabel("theta (deg)")
    a3.set_ylabel("log10 meas - calc")

    fig.tight_layout()
    fig.savefig(out, dpi=100)
    plt.close(fig)
    announce(out, True)


# ---------------------------------------------------------------- figures 4a, 4b
def overlay(workdir, job, ref, out):
    """Adapted from overlay_vs_author.py. Same data, same styling, de-identified labels
    and no in-image title."""
    jd = os.path.join(workdir, "jobs", job)
    need = [os.path.join(jd, "measured.dat"), os.path.join(jd, "calc.dat"), ref]
    miss = require(need)
    if miss:
        announce(out, False, "missing input: " + "; ".join(miss))
        return

    m = np.loadtxt(os.path.join(jd, "measured.dat"), skiprows=1)
    c = np.loadtxt(os.path.join(jd, "calc.dat"), skiprows=1)
    z = zipfile.ZipFile(ref)
    rc = load_xrcx_curve(z, "calc.dat")
    rd = load_xrcx_curve(z, [n for n in z.namelist() if n.startswith("data")][0])

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9, 8), sharex=True,
                                  gridspec_kw={"height_ratios": [3, 1]})
    ax.semilogy(m[:, 0], m[:, 1], color="0.3", lw=0.8,
                label="measured (session's normalization)")
    ax.semilogy(c[:, 0], c[:, 1], color="tab:red", lw=1.0, label="test session fit")
    ax.semilogy(rc[:, 0], rc[:, 1], color="tab:blue", lw=1.0, ls="--",
                label="expert's withheld fit (his normalization)")
    ax.set_ylabel("reflectivity")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)

    ok = (m[:, 1] > 0) & (c[:, 1] > 0)
    ax2.plot(m[ok, 0], np.log10(c[ok, 1] / m[ok, 1]), color="tab:red", lw=0.7,
             label="log10(calc/meas), test session")
    rci = np.interp(rd[:, 0], rc[:, 0], rc[:, 1])
    okr = (rd[:, 1] > 0) & (rci > 0)
    ax2.plot(rd[okr, 0], np.log10(rci[okr] / rd[okr, 1]), color="tab:blue", lw=0.7, ls="--",
             label="log10(calc/meas), the expert")
    ax2.axhline(0, color="k", lw=0.5)
    ax2.set_ylim(-1, 1)
    ax2.set_xlabel("theta (deg)")
    ax2.set_ylabel("log residual")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    announce(out, True)


def figure4():
    overlay(os.path.join(E, "skill-dev-2026-09-18", "workdir-T04"),
            "fit-20260918-201131-4c37",
            os.path.join(AUTHREF, "author-fit-P2-04-full-fit.xrcx"),
            os.path.join(OUT, "fig4a-CoC4-session-vs-expert.png"))
    overlay(os.path.join(E, "skill-dev-2026-09-18", "workdir-T05"),
            "fit-20260918-201038-0878",
            os.path.join(AUTHREF, "author-fit-P2-05-Manual-2026-09-18.xrcx"),
            os.path.join(OUT, "fig4b-CoC5-session-vs-expert.png"))


# ---------------------------------------------------------------- figure 5
def figure5():
    """Adapted from figure4_budgets.py. Same numbers, same bars, same order.
    Session labels become round labels in the paper's specimen names; the mapping is
    Table 3 of sections/05-qualification.md (round, curve, session) read through
    specimen-concordance.md (P2-04 -> CoC4, P2-05 -> CoC5)."""
    out = os.path.join(OUT, "fig5-budgets.png")
    # (label, turns, context tokens in millions = cache_read + cache_creation + input)
    before = [("CoC5, round 1", 672, 146.4), ("CoC4, round 1", 632, 116.7),
              ("CoC5, round 2", 573, 103.7), ("CoC4, round 2", 667, 128.8)]
    after = [("CoC5, round 3", 32, 2.05), ("CoC4, round 3", 32, 1.60),
             ("the agent", 13, 3.91)]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    labels = [b[0] for b in before] + [a[0] for a in after]
    turns = [b[1] for b in before] + [a[1] for a in after]
    toks = [b[2] for b in before] + [a[2] for a in after]
    colors = ["0.55"] * len(before) + ["tab:blue"] * len(after)
    for ax, vals, ylab in ((a1, turns, "turns per session"),
                           (a2, toks, "context tokens per session (millions)")):
        bars = ax.bar(range(len(labels)), vals, color=colors)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
        ax.set_ylabel(ylab, fontsize=9)
        ax.set_yscale("log")
        ax.grid(axis="y", alpha=0.3)
        ax.set_ylim(min(vals) * 0.5, max(vals) * 3)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v * 1.15, f"{v:g}", ha="center", fontsize=7)
        ax.axvline(len(before) - 0.5, color="k", lw=0.6, ls="--")
    # both panels carry both group labels: with the labels on the left panel only, the
    # two titles read as "left panel = before, right panel = after", which is wrong.
    for _ax in (a1, a2):
        _ax.set_title("before the changes", fontsize=9, loc="left")
        _ax.set_title("after the changes", fontsize=9, loc="right")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    announce(out, True)


# ---------------------------------------------------------------- figure 6
def figure6():
    """Adapted from p204_sigma_minima.py."""
    out = os.path.join(OUT, "fig6-two-sigma-minima.png")
    agent = os.path.join(E, "runs", "exp-03", "workdir", "jobs", "fit-20260918-233743-691e")
    sonnet = os.path.join(E, "skill-dev-2026-09-18", "workdir-T04c", "jobs",
                          "fit-20260918-222358-b830")
    ref = os.path.join(AUTHREF, "author-fit-P2-04-full-fit.xrcx")
    need = [os.path.join(agent, "measured.dat"), os.path.join(agent, "calc.dat"),
            os.path.join(sonnet, "calc.dat"), ref]
    miss = require(need)
    if miss:
        announce(out, False, "missing input: " + "; ".join(miss))
        return

    m = np.loadtxt(os.path.join(agent, "measured.dat"), skiprows=1)
    ca = np.loadtxt(os.path.join(agent, "calc.dat"), skiprows=1)
    cs = np.loadtxt(os.path.join(sonnet, "calc.dat"), skiprows=1)
    z = zipfile.ZipFile(ref)
    rows = []
    for line in z.read("calc.dat").decode("utf-8", "replace").splitlines():
        p = line.split()
        try:
            rows.append((float(p[0]), float(p[1])))
        except (ValueError, IndexError):
            pass
    cr = np.array(rows)

    fig = plt.figure(figsize=(11, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.6, 1])
    ax = fig.add_subplot(gs[0, :])
    z1 = fig.add_subplot(gs[1, 0])
    z2 = fig.add_subplot(gs[1, 1])
    for a in (ax, z1, z2):
        a.semilogy(m[:, 0], m[:, 1], color="0.25", lw=0.8, label="measured × agent's scale")
        a.semilogy(ca[:, 0], ca[:, 1], color="tab:red", lw=1.0,
                   label="the agent (σ_C 0.264 / σ_Co 0.433 nm, χ² 7.94)")
        a.semilogy(cs[:, 0], cs[:, 1], color="tab:green", lw=1.0,
                   label="test session, round 3 (σ_C 0.570 / σ_Co 0.275 nm, χ² 7.28)")
        a.semilogy(cr[:, 0], cr[:, 1], color="tab:blue", lw=1.0, ls="--",
                   label="the expert (σ_C 0.558 / σ_Co 0.246 nm, his normalization)")
        a.grid(alpha=0.3)
    ax.set_xlim(0.2, 5.6)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylabel("reflectivity")
    z1.set_xlim(0.95, 1.65)
    z1.set_ylim(3e-5, 3e-2)
    z1.set_title("fringes between orders 1 and 2", fontsize=10)
    z2.set_xlim(3.05, 5.0)
    z2.set_ylim(1e-6, 2e-3)
    z2.set_title("orders 4, 5, 6", fontsize=10)
    for a in (z1, z2):
        a.set_xlabel("theta (deg)")
    z1.set_ylabel("reflectivity")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    announce(out, True)


# ---------------------------------------------------------------- figure 7
def figure7():
    """Adapted from p204_cap_figure.py. Only the suptitle is removed; the three legend
    entries and every number in them are unchanged."""
    out = os.path.join(OUT, "fig7-surface-layer.png")
    nocap = os.path.join(E, "skill-dev-2026-09-18", "workdir-CAP", "A-S", "jobs",
                         "fit-20260919-061017-879e")
    cap = os.path.join(E, "skill-dev-2026-09-18", "workdir-CAP", "B-S", "jobs",
                       "fit-20260919-061017-4587")
    other = os.path.join(E, "skill-dev-2026-09-18", "workdir-T04c", "jobs",
                         "fit-20260918-222358-b830")
    need = [os.path.join(nocap, "measured.dat"), os.path.join(nocap, "calc.dat"),
            os.path.join(cap, "calc.dat"), os.path.join(other, "calc.dat")]
    miss = require(need)
    if miss:
        announce(out, False, "missing input: " + "; ".join(miss))
        return

    m = np.loadtxt(os.path.join(nocap, "measured.dat"), skiprows=1)
    c0 = np.loadtxt(os.path.join(nocap, "calc.dat"), skiprows=1)
    c1 = np.loadtxt(os.path.join(cap, "calc.dat"), skiprows=1)
    c2 = np.loadtxt(os.path.join(other, "calc.dat"), skiprows=1)

    fig, axs = plt.subplots(1, 3, figsize=(14, 4.6))
    wins = [(0.95, 1.65, 3e-5, 3e-2, "between orders 1 and 2"),
            (1.75, 2.4, 1e-6, 3e-3, "between orders 2 and 3"),
            (0.2, 0.9, 1e-3, 1.2, "edge and first fringes")]
    for a, (x0, x1, y0, y1, t) in zip(axs, wins):
        a.semilogy(m[:, 0], m[:, 1], color="0.25", lw=0.8, label="measured × scale")
        a.semilogy(c0[:, 0], c0[:, 1], color="tab:red", lw=1.0,
                   label="no surface layer, σ 0.264 / 0.433 nm, χ² 7.94")
        a.semilogy(c1[:, 0], c1[:, 1], color="tab:orange", lw=1.0,
                   label="+ C 1.26 nm ρ 0.68 on top, σ 0.263 / 0.446 nm, χ² 6.09")
        a.semilogy(c2[:, 0], c2[:, 1], color="tab:green", lw=1.0, ls="--",
                   label="other minimum, σ 0.570 / 0.275 nm, no layer, χ² 7.28")
        a.set_xlim(x0, x1)
        a.set_ylim(y0, y1)
        a.set_title(t, fontsize=10)
        a.grid(alpha=0.3)
        a.set_xlabel("theta (deg)")
    axs[0].set_ylabel("reflectivity")
    axs[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    announce(out, True)


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    print(f"output directory: {OUT}")
    figure3()
    figure4()
    figure5()
    figure6()
    figure7()
    n = sum(1 for _, w, _ in RESULTS if w)
    print(f"\n{n} written, {len(RESULTS) - n} skipped, of {len(RESULTS)} figures")


if __name__ == "__main__":
    main()
