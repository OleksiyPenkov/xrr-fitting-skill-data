"""Like-for-like chi2 on the AUTHOR's data (2026-09-19): his fitted curve (calc.dat inside his .xrcx, the true profile
model) and the session's fitted structure (rendered by the tool on his grid) against his data file, over his fit range,
with the engine's chi2 formula reproduced offline (chi2_offline.py), under his settings (TWChi, PWChi, Window, width)
and under the skill's (theta_weight 1).

usage: score_on_author_grid.py <session-workdir> <job-id> <reference.xrcx> [session_resolution]

Both curves are compared on the same points (his data grid within [Start, End] of his [ANGLE] section, 2theta -> theta),
so the only asymmetry is that his curve was optimized on these points and the session's on its own conditioning.
"""
import sys, os, json, zipfile, re, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from skilltest_compare import read_xrcx
from chi2_offline import chi2
from score_author_model import xrcx_to_json, MCP


def author_params(path):
    z = zipfile.ZipFile(path)
    txt = z.read("params.dsc").decode("utf-8", errors="replace")
    sec, out = None, {}
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            sec = line[1:-1]
        elif "=" in line and sec:
            k, v = line.split("=", 1)
            out[f"{sec}.{k.strip()}"] = v.strip()
    dname = [n for n in z.namelist() if n.startswith("data")][0]
    data = np.loadtxt(z.open(dname), skiprows=2)
    calc = np.loadtxt(z.open("calc.dat"), skiprows=2)
    return out, data, calc


def main():
    workdir, job, ref = sys.argv[1:4]
    jd = os.path.join(workdir, "jobs", job)
    req = json.load(open(os.path.join(jd, "request.json"), encoding="utf-8-sig"))
    sess_res = float(sys.argv[4]) if len(sys.argv) > 4 else float(req.get("resolution", 0.012))
    P, data, calc = author_params(ref)
    start, end = float(P["ANGLE.Start"]), float(P["ANGLE.End"])
    width = float(P["ANGLE.width"]); tw = int(P["FIT.TWChi"]); pw = int(P["FIT.PWChi"]) == 1; win = float(P["FIT.Window"])
    minlim = float(P["PARAMS.MinLimit"])
    sel = (data[:, 0] >= start - 1e-6) & (data[:, 0] <= end + 1e-6)
    two_theta = P.get("ANGLE.2teta", "1") == "1"   # the GUI stores the angle axis of the data: 1 = 2theta, 0 = theta
    th = data[sel, 0] / 2.0 if two_theta else data[sel, 0]
    print(f"data axis: {'2theta' if two_theta else 'theta'}")
    D = data[sel, 1]
    Ra = calc[sel, 1]
    assert np.allclose(calc[sel, 0], data[sel, 0])
    print(f"author fit: range 2theta {start}-{end} ({sel.sum()} points), width {width}, TWChi {tw}, PWChi {pw}, Window {win}, MinLimit {minlim}, Mode {P['FIT.Mode']} PolyOrder {P['FIT.PolyOrder']}")
    sess = xrcx_to_json(read_xrcx(os.path.join(jd, "fit.xrcx"))[0])
    spec = req["measurement_id"].split("/")[0]
    sw = os.path.join(HERE, f"workdir-SCORE-{spec}")
    for sub in ("jobs", "log", "projects", "inbox"):
        os.makedirs(os.path.join(sw, sub), exist_ok=True)
    mcp = MCP(sw)
    curves = {}
    for label, res in (("his width", width), ("session's dtheta", sess_res)):
        r = mcp.tool("calc_reflectivity", {"structure": sess, "lambda": req.get("lambda", 1.5406), "polarization": req.get("polarization", "s"),
                                           "theta_min": float(th[0]), "theta_max": float(th[-1]), "points": int(len(th)), "delta_theta": res, "r_min": minlim, "max_inline_points": 0})
        jid = r.get("job_id")
        cfile = None
        if jid:
            cfile = os.path.join(sw, "jobs", jid, "curve.dat")
        elif isinstance(r, dict) and r.get("curve_file"):
            cfile = r["curve_file"]
        if not cfile or not os.path.exists(cfile):
            print("calc_reflectivity result:", json.dumps(r)[:600]); continue
        c = np.loadtxt(cfile, skiprows=1)
        if len(c) != len(th) or abs(c[0, 0] - th[0]) > 1e-4:
            print(f"grid mismatch: tool {len(c)} points {c[0,0]}-{c[-1,0]} vs {len(th)} {th[0]}-{th[-1]}")
        curves[label] = (res, np.maximum(c[:, 1], minlim))
    mcp.close()
    Ra_f = np.maximum(Ra, minlim)
    rows = []
    for wname, tw_use in ((f"author's weights (TWChi {tw})", tw), ("skill's weights (theta_weight 1)", 1)):
        rows.append((f"author's curve (his calc.dat), {wname}", chi2(th, D, Ra_f, tw_use, width, win, pw)))
        for label, (res, Rs) in curves.items():
            rows.append((f"session structure at {label} {res}, {wname}", chi2(th, D, Rs, tw_use, res, win, pw)))
    for name, v in rows:
        print(f"  {v:10.4f}  {name}")
    json.dump({"session_job": job, "reference": os.path.basename(ref), "range_2theta": [start, end], "rows": rows},
              open(os.path.join(jd, "author-grid-score.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
