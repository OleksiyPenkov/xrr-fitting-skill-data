"""Stage the data-and-code part of the Zenodo deposit for the XRR fitting skill paper.

Run:  python D:/MultilayerLab/Papers/XRR-Fitting-Skill/submission/zenodo/scripts/build_deposit.py

Adapted from the companion paper's deposit builder
(Agentic-Deposition-Control/drafts/build_deposit_v11.py). That file is the precedent
and is not modified. The layout, the CSV format, the per-directory .zip and the
redaction discipline are taken from it unchanged.

In:   LLM-XRay-Optics-Lab/          the laboratory record (READ ONLY)
      XRR-Fitting-Skill/            the manuscript's own analysis and figure scripts
Out:  XRR-Fitting-Skill/submission/zenodo/
        curves/    + curves.zip     the measured curves of the Co/C campaign, as recorded
        fits/      + fits.zip       the expert's reference projects
        jobs/      + jobs.zip       the request, job and report files of every fit job
        procedure/ + procedure.zip  the written procedure and the prompts as sent
        scripts/   + scripts.zip    the qualification, scoring and figure scripts
        server/    + server.zip     what the record holds about the tool-server revisions

NOT written here: README.md (hand-written), SHA256SUMS.txt (generated last, over the
finished tree), and transcripts/ + transcripts.zip (build_transcript_deposit.py).

WHAT IS NOT RE-DEPOSITED
The six Ru/C curves and the expert's Ru/C fits belong to the companion paper's deposit
(reference [42] of the manuscript) and are cited, not copied. Only the fit jobs the
transfer sessions produced on those curves are here, because those are this study's.

REDACTION
The same exact literals as build_transcript_deposit.py, applied to every deposited text
file. Binary and numeric files are scanned for the same literals and refused if one
occurs, then copied byte for byte.

NOTHING IS RECOMPUTED. No measured curve is refitted, smoothed, interpolated or
resampled. The curve CSVs carry the numbers of the record's data files as strings,
token for token.
"""
import csv
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
PAPER = OUT.parent.parent
LAB = Path("D:/MultilayerLab/Papers/LLM-XRay-Optics-Lab")
E = LAB / "experiments"
EXP03 = E / "runs" / "exp-03"
SKILLDEV = E / "skill-dev-2026-09-18"
INBOX = EXP03 / "workdir" / "inbox"
RAW = EXP03 / "raw"
AUTHREF = EXP03 / "author-reference"
RESCORE = PAPER / "analysis" / "baseline-rescoring-2026-09-19"

sys.dont_write_bytecode = True   # no __pycache__ in the deposit tree
sys.path.insert(0, str(HERE))
from build_transcript_deposit import REDACTIONS  # noqa: E402

counts = {p: 0 for p, _, _, _ in REDACTIONS}


# ---------------------------------------------------------------- the tables

# paper name -> (record name, .xrdml in raw/, what it is)
# The concordance is specimen-concordance.md; CoC6 (record P2-07) has no measured
# curve in the record and therefore no entry here.
CURVES = [
    ("CoC1", "P2-01", "XRR 1_Co(260914A).xrdml",
     "Co/C, baseline round 1"),
    ("CoC2", "P2-02", "XRR 1_Co-C(260914B).xrdml",
     "Co/C, baseline round 1"),
    ("CoC3", "P2-03", "XRR-1_Co-C(260916A)-XRR.xrdml",
     "Co/C, baseline round 2"),
    ("CoC4", "P2-04", "XRR-1_Co-C(260916B).xrdml",
     "Co/C, qualification reference curve 1; baseline round 2"),
    ("CoC5", "P2-05", "XRR 1_Co-C(260917A).xrdml",
     "Co/C, qualification reference curve 2; baseline round 3"),
    ("C1", "P2-06", "XRR 1_C(260917B)-XRR.xrdml",
     "single carbon film on glass; baseline round 3"),
]

# deposited stem -> (source .xrcx, what it is)
FITS = [
    ("CoC4-expert-full-fit", "author-fit-P2-04-full-fit.xrcx",
     "the expert's withheld reference fit of CoC4; the fit the manuscript's numbers use"),
    ("CoC4-expert-from-agent-project", "author-fit-P2-04-from-agent-project.xrcx",
     "a second reference fit of CoC4, made in the agent's own project file; NOT the one "
     "the manuscript's numbers use"),
    ("CoC5-expert", "author-fit-P2-05-Manual-2026-09-18.xrcx",
     "the expert's withheld reference fit of CoC5"),
]

# deposit group -> [(deposit session directory, source workdir)]
# Session directory names are the manuscript's. The record's own labels are in the
# top-level README's mapping table.
JOB_GROUPS = [
    ("campaign1-stage1", [
        ("CoC4-round-1", SKILLDEV / "workdir-T04"),
        ("CoC4-round-2", SKILLDEV / "workdir-T04b"),
        ("CoC4-round-3", SKILLDEV / "workdir-T04c"),
        ("CoC5-round-1", SKILLDEV / "workdir-T05"),
        ("CoC5-round-2", SKILLDEV / "workdir-T05b"),
        ("CoC5-round-3", SKILLDEV / "workdir-T05c"),
        ("aborted-launch-max-turns", SKILLDEV / "workdir-run1-maxturns"),
    ]),
    ("campaign2-transfer", [
        ("RuC1-round-a", SKILLDEV / "workdir-RuC-260511B-a"),
        ("RuC1-round-b", SKILLDEV / "workdir-RuC-260511B-b"),
        ("RuC2-round-a", SKILLDEV / "workdir-RuC-260908A-a"),
        ("RuC2-round-b", SKILLDEV / "workdir-RuC-260908A-b"),
        ("RuC3-round-a", SKILLDEV / "workdir-RuC-260908B-a"),
        ("RuC3-round-b", SKILLDEV / "workdir-RuC-260908B-b"),
        ("RuC4-round-a", SKILLDEV / "workdir-RuC-260909A-a"),
        ("RuC4-round-b", SKILLDEV / "workdir-RuC-260909A-b"),
        ("RuC5-round-a", SKILLDEV / "workdir-RuC-260910A-a"),
        ("RuC5-round-b", SKILLDEV / "workdir-RuC-260910A-b"),
        ("Ru1-round-a", SKILLDEV / "workdir-RuC-260910B-a"),
        ("Ru1-round-b", SKILLDEV / "workdir-RuC-260910B-b"),
    ]),
    ("seed-and-surface-study", [
        ("CoC4-seed-A-periodic", SKILLDEV / "workdir-CAP" / "A-R"),
        ("CoC4-seed-A-surface", SKILLDEV / "workdir-CAP" / "A-S"),
        ("CoC4-seed-B-periodic", SKILLDEV / "workdir-CAP" / "B-R"),
        ("CoC4-seed-B-surface", SKILLDEV / "workdir-CAP" / "B-S"),
        ("CoC4-seed-A1", SKILLDEV / "workdir-CAP2" / "A1"),
        ("CoC4-seed-A2", SKILLDEV / "workdir-CAP2" / "A2"),
        ("CoC4-seed-B1", SKILLDEV / "workdir-CAP2" / "B1"),
        ("CoC4-seed-B2", SKILLDEV / "workdir-CAP2" / "B2"),
    ]),
    # One workdir served the loop agent through the whole Co/C campaign: the three
    # rejected baseline rounds of Section 6, the stage-2 qualification fits of
    # Section 7.2, and the refits under the amended procedure of Section 7.5. Its jobs
    # are deposited whole rather than partitioned, because the record does not
    # partition them and the manuscript names individual job ids.
    ("agent-loop", [("all-fits", EXP03 / "workdir")]),
]

# Per-job JSON files as the server writes them. There is no result.json: the server
# writes the result of a fit as report.json beside job.json.
JOB_JSON = ("request.json", "job.json", "report.json",
            "author-grid-score.json", "author-model-score.json")

# The jobs whose curve files the figure scripts read. Deposited so that
# make_figures_v3.py can run against this archive.
FIGURE_JOBS = [
    ("fig3-CoC5-baseline", EXP03 / "workdir", "fit-20260918-144637-1bcc"),
    ("fig4a-CoC4-session", SKILLDEV / "workdir-T04", "fit-20260918-201131-4c37"),
    ("fig4b-CoC5-session", SKILLDEV / "workdir-T05", "fit-20260918-201038-0878"),
    ("fig6-CoC4-agent", EXP03 / "workdir", "fit-20260918-233743-691e"),
    ("fig6-CoC4-session", SKILLDEV / "workdir-T04c", "fit-20260918-222358-b830"),
    ("fig7-CoC4-no-surface", SKILLDEV / "workdir-CAP" / "A-S", "fit-20260919-061017-879e"),
    ("fig7-CoC4-surface", SKILLDEV / "workdir-CAP" / "B-S", "fit-20260919-061017-4587"),
]
FIGURE_DAT = ("measured.dat", "calc.dat", "residual.dat")

PROCEDURE = E / "brief" / "manual" / "xrr-fitting-skill.md"

# deposited name -> source, for the prompts exactly as the sessions received them
AS_SENT = [
    ("stage1-CoC4-round-1.md", SKILLDEV / "prompt-T04-as-sent.md"),
    ("stage1-CoC4-round-2.md", SKILLDEV / "prompt-T04b-as-sent.md"),
    ("stage1-CoC4-round-3.md", SKILLDEV / "prompt-T04c-as-sent.md"),
    ("stage1-CoC5-round-1.md", SKILLDEV / "prompt-T05-as-sent.md"),
    ("stage1-CoC5-round-2.md", SKILLDEV / "prompt-T05b-as-sent.md"),
    ("stage1-CoC5-round-3.md", SKILLDEV / "prompt-T05c-as-sent.md"),
    ("transfer-RuC1-round-a.md", SKILLDEV / "prompt-RuC-260511B-a-as-sent.md"),
    ("transfer-RuC1-round-b.md", SKILLDEV / "prompt-RuC-260511B-b-as-sent.md"),
    ("transfer-RuC2-round-a.md", SKILLDEV / "prompt-RuC-260908A-a-as-sent.md"),
    ("transfer-RuC2-round-b.md", SKILLDEV / "prompt-RuC-260908A-b-as-sent.md"),
    ("transfer-RuC3-round-a.md", SKILLDEV / "prompt-RuC-260908B-a-as-sent.md"),
    ("transfer-RuC3-round-b.md", SKILLDEV / "prompt-RuC-260908B-b-as-sent.md"),
    ("transfer-RuC4-round-a.md", SKILLDEV / "prompt-RuC-260909A-a-as-sent.md"),
    ("transfer-RuC4-round-b.md", SKILLDEV / "prompt-RuC-260909A-b-as-sent.md"),
    ("transfer-RuC5-round-a.md", SKILLDEV / "prompt-RuC-260910A-a-as-sent.md"),
    ("transfer-RuC5-round-b.md", SKILLDEV / "prompt-RuC-260910A-b-as-sent.md"),
    ("transfer-Ru1-round-a.md", SKILLDEV / "prompt-RuC-260910B-a-as-sent.md"),
    ("transfer-Ru1-round-b.md", SKILLDEV / "prompt-RuC-260910B-b-as-sent.md"),
]

# deposited name -> source, the qualification, scoring and harness scripts
QUAL_SCRIPTS = [
    ("run-skilltest.ps1", SKILLDEV / "run-skilltest.ps1"),
    ("make_ruc_skilltest.py", SKILLDEV / "make_ruc_skilltest.py"),
    ("skilltest_compare.py", SKILLDEV / "skilltest_compare.py"),
    ("skilltest_compare_ruc.py", SKILLDEV / "skilltest_compare_ruc.py"),
    ("score_author_model.py", SKILLDEV / "score_author_model.py"),
    ("score_on_author_grid.py", SKILLDEV / "score_on_author_grid.py"),
    ("chi2_offline.py", SKILLDEV / "chi2_offline.py"),
    ("overlay_vs_author.py", SKILLDEV / "overlay_vs_author.py"),
    ("p204_sigma_minima.py", SKILLDEV / "p204_sigma_minima.py"),
    ("p204_cap_figure.py", SKILLDEV / "p204_cap_figure.py"),
    ("p204_cap_hypothesis.py", SKILLDEV / "p204_cap_hypothesis.py"),
    ("p204_cap_seeds.py", SKILLDEV / "p204_cap_seeds.py"),
]

# deposited name -> source, what the record holds about the tool server
SERVER_FILES = [
    ("xrc-mcp-server-requirements.md",
     LAB / "docs" / "specs" / "2026-09-08-xrc-mcp-server-requirements.md"),
    ("verify-02e7b63.ps1", E / "fom-defect-2026-09-12" / "verify-02e7b63.ps1"),
    ("verify-06035de.txt", E / "fit-bounds-defect-2026-09-16" / "verify-06035de.txt"),
    ("verify-2643c4c.txt", E / "fit-bounds-defect-2026-09-16" / "verify-2643c4c.txt"),
    ("verify-f0168e0.txt", E / "fit-smoothing-2026-09-17" / "verify-f0168e0.txt"),
    ("verify-7f5b397.txt", E / "fit-smoothing-2026-09-17" / "verify-7f5b397.txt"),
    ("verify-2accc0c-and-dbee34c.txt", SKILLDEV / "verify-2accc0c.txt"),
    ("mcp-config-example.json", SKILLDEV / "mcp.skilltest-RuC-260511B-a.json"),
]


# ---------------------------------------------------------------- helpers

def redact_text(text):
    for pat, rep, _, _ in REDACTIONS:
        if pat in text:
            counts[pat] += text.count(pat)
            text = text.replace(pat, rep)
    return text


def scan_binary(path):
    data = path.read_bytes()
    if path.suffix == ".xrcx":
        with zipfile.ZipFile(path) as z:
            data = b"".join(z.read(n) for n in z.namelist())
    for pat, _, _, _ in REDACTIONS:
        if pat.encode("utf-8") in data:
            sys.exit("redaction literal found in %s; refusing to copy it unchanged" % path)


def copy_text(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(redact_text(src.read_text(encoding="utf-8")),
                   encoding="utf-8", newline="")


def copy_binary(src, dst):
    scan_binary(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_xrcx_curve(path):
    """((2Theta, measured, fitted) rows, MinLimit) from one .xrcx.

    The method of the companion deposit's extract_xrr_curves.py, unchanged: params.dsc
    names the dataset the fit is linked to as LinkedData=N and the member holding it is
    data_<N>.dat; calc.dat is the curve calculated from the fitted structure. Both are
    released over their full range, exactly as stored.
    """
    with zipfile.ZipFile(path) as z:
        params = z.read("params.dsc").decode("latin-1")
        limit = re.search(r"^MinLimit=([0-9.eE+-]+)\s*$", params, re.M)
        linked = re.search(r"^LinkedData=(\d+)\s*$", params, re.M)
        if not linked:
            sys.exit("%s: params.dsc carries no LinkedData" % path.name)
        member = "data_%s.dat" % linked.group(1)
        if member not in z.namelist():
            sys.exit("%s: LinkedData points at %s, which is not in the file"
                     % (path.name, member))
        cols = {}
        for name, key in ((member, "measured"), ("calc.dat", "fitted")):
            pts = []
            for line in z.read(name).decode("utf-8", "replace").splitlines()[2:]:
                line = line.strip()
                if not line:
                    continue
                x, y = line.split("\t")[:2]
                pts.append((float(x), float(y)))
            cols[key] = pts
    m, f = cols["measured"], cols["fitted"]
    if len(m) != len(f):
        sys.exit("%s: %d measured points against %d fitted" % (path.name, len(m), len(f)))
    for (xm, _), (xf, _) in zip(m, f):
        if abs(xm - xf) > 1e-9:
            sys.exit("%s: measured and fitted are not on one grid" % path.name)
    return ([(x, ym, yf) for (x, ym), (_, yf) in zip(m, f)],
            float(limit.group(1)) if limit else None)


# ---------------------------------------------------------------- the parts

def build_curves():
    d = OUT / "curves"
    d.mkdir(parents=True, exist_ok=True)
    rows = []
    for paper, record, xrdml, what in CURVES:
        meta = json.loads((INBOX / record / "meta.json").read_text(encoding="utf-8"))
        # the curve, token for token out of the record's data file
        lines = (INBOX / record / "xrr.dat").read_text(encoding="utf-8").splitlines()
        pts = [ln.split() for ln in lines if ln.strip()]
        out = d / ("%s.csv" % paper)
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["# specimen", paper, "record_name", record,
                        "instrument_id", meta["specimen_id_on_instrument"],
                        "raw_file", meta["raw_file"], "role", what,
                        "points", len(pts)])
            w.writerow(["two_theta_deg", "intensity_counts"])
            for a, b in pts:
                w.writerow([a, b])
        copy_text(INBOX / record / "meta.json", d / ("%s.meta.json" % paper))
        copy_binary(RAW / xrdml, d / ("%s.xrdml" % paper))
        if meta["raw_file"] != xrdml:
            sys.exit("%s: meta.json names %s, table names %s"
                     % (record, meta["raw_file"], xrdml))
        rows.append((paper, record, meta["specimen_id_on_instrument"], xrdml,
                     len(pts), pts[0][0], pts[-1][0], meta["scan"]["step_deg"], what))
        print("curve %-5s %-5s %5d pts  %s to %s deg" % (paper, record, len(pts),
                                                         pts[0][0], pts[-1][0]))
    return rows


def build_fits():
    d = OUT / "fits"
    d.mkdir(parents=True, exist_ok=True)
    rows = []
    for stem, src, what in FITS:
        copy_binary(AUTHREF / src, d / (stem + ".xrcx"))
        curve, limit = read_xrcx_curve(AUTHREF / src)
        out = d / (stem + ".csv")
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["# fit", stem, "stored_as", src, "min_limit",
                        "" if limit is None else "%.3E" % limit])
            w.writerow(["two_theta_deg", "measured_reflectivity", "fitted_reflectivity"])
            for x, ym, yf in curve:
                w.writerow(["%.3f" % x, "%.6E" % ym, "%.6E" % yf])
        rows.append((stem, src, len(curve), curve[0][0], curve[-1][0], limit, what))
        print("fit   %-32s %4d pts  %.3f to %.3f deg" % (stem, len(curve),
                                                         curve[0][0], curve[-1][0]))
    return rows


def build_jobs():
    d = OUT / "jobs"
    d.mkdir(parents=True, exist_ok=True)
    manifest = []
    n_jobs = 0
    for group, sessions in JOB_GROUPS:
        for session, workdir in sessions:
            jobs = sorted(p for p in (workdir / "jobs").iterdir()
                          if p.is_dir() and p.name.startswith("fit-"))
            if not jobs:
                sys.exit("no fit jobs in %s" % workdir)
            for job in jobs:
                dst = d / group / session / job.name
                dst.mkdir(parents=True, exist_ok=True)
                present = []
                for name in JOB_JSON:
                    if (job / name).exists():
                        copy_text(job / name, dst / name)
                        present.append(name)
                jd = json.loads((job / "job.json").read_text(encoding="utf-8"))
                rq = json.loads((job / "request.json").read_text(encoding="utf-8"))
                manifest.append((group, session, job.name,
                                 rq.get("measurement_id", ""),
                                 jd.get("state", ""),
                                 jd.get("best_value", ""),
                                 jd.get("started_utc", ""),
                                 jd.get("elapsed_s", ""),
                                 " ".join(present),
                                 str(job.relative_to(LAB)).replace("\\", "/")))
                n_jobs += 1
            print("jobs  %-22s %-24s %2d" % (group, session, len(jobs)))

    # the curve files the figure scripts read
    for name, workdir, job in FIGURE_JOBS:
        dst = d / "figure-data" / name
        dst.mkdir(parents=True, exist_ok=True)
        for f in FIGURE_DAT:
            src = workdir / "jobs" / job / f
            if src.exists():
                copy_text(src, dst / f)
        (dst / "SOURCE.txt").write_text(
            "%s\n%s\n" % (job, str((workdir / "jobs" / job).relative_to(LAB)).replace("\\", "/")),
            encoding="utf-8", newline="\n")
    print("jobs  figure-data            %d jobs" % len(FIGURE_JOBS))

    with (d / "MANIFEST.tsv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["group", "session", "job_id", "measurement", "state", "chi2",
                    "started_utc", "elapsed_s", "files", "source_in_record"])
        for row in manifest:
            w.writerow(row)
    return n_jobs, manifest


def build_procedure():
    d = OUT / "procedure"
    d.mkdir(parents=True, exist_ok=True)
    copy_text(PROCEDURE, d / "xrr-fitting-skill.md")
    for name, src in AS_SENT:
        copy_text(src, d / "as-sent" / name)
    return len(AS_SENT) + 1


def build_scripts():
    d = OUT / "scripts"
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    copy_text(PAPER / "make_figures_v3.py", d / "make_figures_v3.py")
    n += 1
    for name, src in QUAL_SCRIPTS:
        copy_text(src, d / "qualification" / name)
        n += 1
    for src in sorted(RESCORE.iterdir()):
        if src.is_file() and src.suffix in (".py", ".sh"):
            copy_text(src, d / "baseline-rescoring-2026-09-19" / src.name)
            n += 1
    for src in sorted((RESCORE / "out").iterdir()):
        copy_text(src, d / "baseline-rescoring-2026-09-19" / "out" / src.name)
        n += 1
    return n


def build_server():
    d = OUT / "server"
    d.mkdir(parents=True, exist_ok=True)
    for name, src in SERVER_FILES:
        if not src.exists():
            sys.exit("server file missing: %s" % src)
        if src.suffix in (".md", ".txt", ".ps1", ".json"):
            copy_text(src, d / name)
        else:
            copy_binary(src, d / name)
    return len(SERVER_FILES)


def zip_folder(folder):
    zpath = OUT / (folder + ".zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((OUT / folder).rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                z.write(f, f.relative_to(OUT).as_posix())
    return zpath


def main():
    curve_rows = build_curves()
    fit_rows = build_fits()
    n_jobs, _ = build_jobs()
    n_proc = build_procedure()
    n_scripts = build_scripts()
    n_server = build_server()

    for folder in ("curves", "fits", "jobs", "procedure", "scripts", "server"):
        z = zip_folder(folder)
        n = sum(1 for f in (OUT / folder).rglob("*") if f.is_file())
        print("%-10s %4d files  ->  %s (%.1f MB)"
              % (folder, n, z.name, z.stat().st_size / 1e6))

    print()
    print("curves    %d" % len(curve_rows))
    print("fits      %d" % len(fit_rows))
    print("jobs      %d fit jobs" % n_jobs)
    print("procedure %d files" % n_proc)
    print("scripts   %d files (plus build_deposit.py and build_transcript_deposit.py)" % n_scripts)
    print("server    %d files" % n_server)
    for pat, rep, desc, _ in REDACTIONS:
        if counts[pat]:
            print("  redacted %s -> %s: %d" % (desc, rep, counts[pat]))
    print()
    print("staged in", OUT)
    print("README.md and SHA256SUMS.txt are not written by this script.")


if __name__ == "__main__":
    main()
