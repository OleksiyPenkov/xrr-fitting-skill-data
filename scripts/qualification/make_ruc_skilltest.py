"""Ru/C transfer test of the XRR fitting skill (2026-09-19): build the isolated workdirs, MCP configs and task
prompts for the six published Ru/C curves of paper 1 (arXiv:2609.12796, Zenodo deposit v1.1, fits.zip).

usage: python make_ruc_skilltest.py [--check-p205]

For every specimen and every repeat (a, b) it writes
  workdir-<TAG>/inbox/<specimen>/xrr.dat   two columns "2theta_deg counts", from the .xrdml (same format as P2-05)
  workdir-<TAG>/inbox/<specimen>/meta.json instrument and scan facts read from the .xrdml
  mcp.skilltest-<TAG>.json                 the xrc server on that workdir
  prompt-<TAG>-task.md                     the task header (nominal design from paper 1's record, no fitted numbers)
TAG = RuC-<specimen>-<a|b>.  --check-p205 regenerates P2-05's xrr.dat from its .xrdml and diffs it against the
inbox file the stage-1 sessions used, as a check of the converter.
"""
import sys, os, re, json

HERE = r"D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments\skill-dev-2026-09-18"
ZEN = r"D:\MultilayerLab\Papers\Agentic-Deposition-Control\submission\zenodo\fits"
XRC = r"D:\DelphiProjects\X-RayCalc\X-RayCalc3_Working\_Out\BIN\XRC_MCP.exe"

# Nominal designs as deposited, from paper 1's record (drafts/section-06-design.md, section-07-*.md), not from the fits.
SPECIMENS = {
    "260511B": "The specimen is a 50-period Ru/C multilayer on a glass substrate, deposited with the intention of a period of about 68.5 Å with Ru about 15 Å and C about 54 Å per period, on a Ru adhesion layer of about 200 Å nominal beneath the first period; a thin low-density carbon layer on top is possible. Cu Kα.",
    "260908A": "The specimen is a 30-period Ru/C multilayer on a glass substrate, deposited with the intention of a period of about 68.5 Å with Ru about 15 Å and C about 54 Å per period, on a Ru adhesion layer of about 200 Å nominal beneath the first period; a thin low-density carbon layer on top is possible. Cu Kα.",
    "260908B": "The specimen is a 30-period Ru/C multilayer on a glass substrate, deposited with the intention of a period of about 68.5 Å with Ru about 15 Å and C about 54 Å per period, on a Ru adhesion layer of about 200 Å nominal beneath the first period; a thin low-density carbon layer on top is possible. Cu Kα.",
    "260909A": "The specimen is a 30-period Ru/C multilayer on a glass substrate, deposited with the intention of a period of about 68.5 Å with Ru about 15 Å and C about 54 Å per period, on a Ru adhesion layer of about 200 Å nominal beneath the first period; a thin low-density carbon layer on top is possible. Cu Kα.",
    "260910A": "The specimen is a 30-period Ru/C multilayer on a glass substrate, deposited with the intention of a period of about 68.5 Å with Ru about 15 Å and C about 54 Å per period, on a Ru adhesion layer of about 200 Å nominal beneath the first period; a thin low-density carbon layer on top is possible. Cu Kα.",
    "260910B": "The specimen is a single Ru film on a glass substrate, deposited with the intention of a thickness of about 200 Å; a thin low-density carbon layer on top is possible. Cu Kα.",
}

TASK = (
    "You are the designer of an X-ray multilayer mirror in a thin-film laboratory, and you fit X-ray reflectivity curves with the `xrc` tool server (X-Ray Calc 3 engine). "
    "One measured curve is in your inbox: `{spec}/xrr.dat` with its `meta.json`. {design}\n\n"
    "Your task: fit this curve according to the laboratory's fitting procedure that follows this task, and deliver the report of its section 13 as your final message. "
    "Apply the procedure as written, in order, with its settings and its judging criteria; where the procedure leaves a choice to you (bounds around your expected values, the end of the fitting range, the resolution within its interval, periodic or profile mode), decide it, state the reason in one sentence, and go on. "
    "Do not ask questions: nobody answers during this session. Work only with the tools; you have no file access outside them.\n\n"
    "Practical notes: `fit_xrr` returns a job id at once and a fit with population 5000 takes about ten minutes; `job_wait` blocks up to 300 s per call and returns the state; call it again while the job is still running. "
    "Your budget is enough for a sensitivity check, {budget} and the recomputation needed for the judgment. Save the accepted fit with `save_project` under the name `skilltest-{spec}-{rep}`."
)

# Round a (08:15-11:06 launches) carried the Co/C header's "up to three fits"; the author ruled at 11:10 that multiple
# fitting attempts are fine ("I often do the same"), so round b lifts the cap.
BUDGET = {"a": "up to three fits", "b": "as many fits as the procedure requires"}

WAVELENGTH_NOTE = "Cu K-alpha as recorded in the instrument file: K-alpha1 {ka1} A, K-alpha2 {ka2} A with ratio K-alpha2/K-alpha1 {ratio}, K-beta {kb} A. No monochromator; the incident optic is a parallel-beam mirror."
ABORTED_NOTE = "The operator stopped the scan once only background was left, to save time; this is routine practice and not a fault."


def tag(t, txt, attr=""):
    m = re.search(r"<%s%s[^>]*>([^<]*)</%s>" % (t, attr, t), txt)
    return m.group(1).strip() if m else None


def fnum(x):
    return float(x) if x is not None else None


def parse_xrdml(path):
    t = open(path, encoding="utf-8").read()
    n = int(re.search(r"<intensities[^>]*>([^<]*)", t).group(1).split().__len__())
    counts = [float(v) for v in re.search(r"<intensities[^>]*>([^<]*)", t).group(1).split()]
    scan = re.search(r'<scan\s+([^>]*)>', t).group(1)
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', scan))
    pos2t = re.search(r'<positions axis="2Theta"[^>]*>(.*?)</positions>', t, re.S).group(1)
    start = float(re.search(r"<startPosition>([^<]*)", pos2t).group(1))
    end = float(re.search(r"<endPosition>([^<]*)", pos2t).group(1))
    step = (end - start) / (n - 1)
    two_theta = [start + i * step for i in range(n)]
    d = {
        "id": tag("id", t),
        "ka1": tag("kAlpha1", t), "ka2": tag("kAlpha2", t), "kb": tag("kBeta", t), "ratio": tag("ratioKAlpha2KAlpha1", t),
        "tension": tag("tension", t), "current": tag("current", t),
        "radius": tag("radius", t),
        "acceptance": tag("acceptanceAngle", t),
        "soller": re.findall(r"<sollerSlit[^>]*>\s*<opening[^>]*>([^<]*)", t),
        "divslit": re.findall(r"<divergenceSlit[^>]*>.*?<height[^>]*>([^<]*)", t, re.S),
        "detector": (re.search(r'<detector[^>]*name="([^"]*)"', t) or [None, None])[1],
        "phd_lo": tag("lowerLevel", t), "phd_hi": tag("upperLevel", t),
        "chan_eq": tag("activeChannelsEquatorial", t), "chan_ax": tag("activeChannelsAxial", t),
        "mode": tag("mode", t),
        "scan_mode": attrs.get("mode"), "axis": attrs.get("scanAxis"), "status": attrs.get("status"),
        "t0": tag("startTimeStamp", t), "t1": tag("endTimeStamp", t),
        "count_time": tag("commonCountingTime", t),
        "start": start, "end": end, "step": step, "n": n, "two_theta": two_theta, "counts": counts,
        "offset": {m.group(1): float(m.group(2)) for m in re.finditer(r'<sampleOffset>.*?<position axis="(\w+)"[^>]*>([^<]*)', t, re.S)},
    }
    # sample offsets (all axes) and stage positions of the scan
    d["offset"] = {a: float(v) for a, v in re.findall(r'<position axis="(\w+)" unit="deg">([^<]*)</position>', re.search(r"<sampleOffset>(.*?)</sampleOffset>", t, re.S).group(1))} if "<sampleOffset>" in t else {}
    d["stage"] = {a: float(v) for a, v in re.findall(r'<positions axis="(Chi|Phi|Z)"[^>]*>\s*<commonPosition>([^<]*)', t)}
    d["config"] = (re.search(r"Configuration=([^,<]*)", t) or [None, None])[1]
    return d


def write_xrr_dat(d, path):
    with open(path, "w", newline="\n") as f:
        for x, c in zip(d["two_theta"], d["counts"]):
            f.write(f"{x:.5f} {c:.1f}\n")


def meta(d, spec, raw_name):
    aborted = (d["status"] or "").lower() == "aborted"
    return {
        "specimen": spec,
        "specimen_id_on_instrument": d["id"],
        "lambda": float(d["ka1"]),
        "wavelength_note": WAVELENGTH_NOTE.format(ka1=d["ka1"], ka2=d["ka2"], ratio=d["ratio"], kb=d["kb"]),
        "theta_unit": "2theta",
        "columns": "2theta_deg intensity_counts",
        "date": (d["t0"] or "")[:10],
        "scan_start": d["t0"], "scan_end": d["t1"],
        "instrument": f"PANalytical Empyrean, Cu LFF HR tube {d['tension']} kV {d['current']} mA, incident parallel-beam W/Si graded parabolic mirror (acceptance {d['acceptance']} deg), fixed divergence slit (height {d['divslit'][0] if d['divslit'] else '?'} as recorded in the file), Soller slits {d['soller'][0] if d['soller'] else '?'} rad on both sides, {d['detector']} in {d['mode']} mode ({d['chan_eq']} equatorial x {d['chan_ax']} axial channels), goniometer radius {d['radius']} mm, {d['config']}",
        "scan": {
            "axis": d["axis"], "mode": (d["scan_mode"] or "").lower(),
            "status_in_file": d["status"],
            "status_note": ABORTED_NOTE if aborted else "The scan ran to the end of its program.",
            "two_theta_start_deg": d["start"], "two_theta_end_deg": d["end"],
            "step_deg": round(d["step"], 4), "points": d["n"],
            "counting_time_s_per_point": float(d["count_time"]),
            "intensity_unit": "counts",
        },
        "detector_phd": {"lower_level_percent": float(d["phd_lo"]), "upper_level_percent": float(d["phd_hi"])},
        "sample_offset_deg": {k.lower(): v for k, v in d["offset"].items()},
        "stage": {("z_mm" if k == "Z" else k.lower() + "_deg"): v for k, v in d["stage"].items()},
        "raw_file": raw_name,
        "processing": "none: the intensities are as exported by the instrument software; no background, footprint or absorption correction",
    }


def main():
    if "--check-p205" in sys.argv:
        src = r"D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments\runs\exp-03\raw\XRR 1_Co-C(260917A).xrdml"
        d = parse_xrdml(src)
        out = os.path.join(HERE, "check-p205-xrr.dat")
        write_xrr_dat(d, out)
        ref = open(os.path.join(HERE, "workdir-T05c", "inbox", "P2-05", "xrr.dat")).read()
        new = open(out).read()
        print("P2-05 regenerated:", "IDENTICAL" if ref == new else "DIFFERENT", len(ref), len(new))
        print(json.dumps(meta(d, "P2-05", os.path.basename(src)), indent=1, ensure_ascii=False)[:1500])
        return
    for spec, design in SPECIMENS.items():
        src = os.path.join(ZEN, spec + ".xrdml")
        d = parse_xrdml(src)
        for rep in ("a", "b"):
            T = f"RuC-{spec}-{rep}"
            wd = os.path.join(HERE, f"workdir-{T}")
            inbox = os.path.join(wd, "inbox", spec)
            for sub in ("inbox", "jobs", "log", "projects"):
                os.makedirs(os.path.join(wd, sub), exist_ok=True)
            os.makedirs(inbox, exist_ok=True)
            write_xrr_dat(d, os.path.join(inbox, "xrr.dat"))
            json.dump(meta(d, spec, os.path.basename(src)), open(os.path.join(inbox, "meta.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
            json.dump({"mcpServers": {"xrc": {"type": "stdio", "command": XRC, "args": ["--workdir", wd], "env": {}}}},
                      open(os.path.join(HERE, f"mcp.skilltest-{T}.json"), "w"), indent=2)
            open(os.path.join(HERE, f"prompt-{T}-task.md"), "w", encoding="utf-8", newline="\n").write(TASK.format(spec=spec, design=design, rep=rep, budget=BUDGET[rep]))
        print(f"{spec}: {d['n']} points {d['start']}-{d['end']} step {d['step']:.4f} status {d['status']} id {d['id']} counts[0] {d['counts'][0]:.0f}")


if __name__ == "__main__":
    main()
