"""Qualification check of a skill-test fit against the author's held-back reference fit.

usage: skilltest_compare.py <workdir> <job-id> <reference.xrcx> [<job-id> <reference.xrcx> ...]

For each job: parses the fitted structure from jobs/<job-id>/fit.xrcx (and its settings),
the reference structure from the author's .xrcx, prints both side by side with the
tolerances of 2026-09-18 (period 0.3 A, thickness 1 A, sigma 1 A on the right interface,
every visible order within 25 % (author 2026-09-18: kept at 25 % although his own fits lie at 0.69-1.76: the agent must do better), chi2 < 10; density not judged), and the order table and
residual by band from measured.dat / calc.dat.
"""
import sys, os, re, json, zipfile
import numpy as np

TOL = {"period": 0.3, "H": 1.0, "s": 1.0, "order": 0.25, "chi2": 10.0}


def read_xrcx(path):
    z = zipfile.ZipFile(path)
    raw = z.read("project.dsc")
    txt = raw.decode("utf-16-le", errors="replace")
    m = re.search(r'\{"Stacks".*?"Subs":\{[^}]*\}\}', txt)
    if not m:
        raise SystemExit(f"no structure JSON in {path}")
    struct = json.loads(m.group(0))
    params = {}
    for line in z.read("params.dsc").decode("utf-8", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            params[k.strip()] = v.strip()
    return struct, params


def layers(struct):
    out = []
    for st in struct["Stacks"]:
        N = st["N"]
        for L in st["Layers"]:
            out.append((L["M"], N, L["H"], L["s"], L["r"], (L["Hmin"], L["Hmax"]), (L["Smin"], L["Smax"]), (L["Rmin"], L["Rmax"])))
    return out


def period(struct):
    st = struct["Stacks"][0]
    return sum(L["H"] for L in st["Layers"]) if st["N"] > 1 else None


def near_bound(v, lo, hi, frac=0.05):
    rng = hi - lo
    return rng > 0 and (v - lo < frac * rng or hi - v < frac * rng)


def order_table(jobdir, d, lam=1.5406, window=0.06):
    """Bragg orders from the fitted period: n lambda = 2 d sin(theta); maximum of each curve within +-window."""
    m = np.loadtxt(os.path.join(jobdir, "measured.dat"), skiprows=1)
    c = np.loadtxt(os.path.join(jobdir, "calc.dat"), skiprows=1)
    rows = []
    n = 1
    while True:
        x = n * lam / (2 * d)
        if x >= 1:
            break
        tn = np.degrees(np.arcsin(x))
        if tn > m[-1, 0] - window:
            break
        if tn > m[0, 0] + window:
            sm = (m[:, 0] > tn - window) & (m[:, 0] < tn + window)
            sc = (c[:, 0] > tn - window) & (c[:, 0] < tn + window)
            im = np.argmax(np.where(sm, m[:, 1], -1))
            ic = np.argmax(np.where(sc, c[:, 1], -1))
            rows.append((n, m[im, 0], m[im, 1], c[ic, 0], c[ic, 1], c[ic, 1] / m[im, 1]))
        n += 1
    ok = (m[:, 1] > 0) & (c[:, 1] > 0)
    r = np.log10(c[ok, 1]) - np.log10(m[ok, 1])
    th = m[ok, 0]
    edges = np.linspace(th[0], th[-1], 9)
    bands = []
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (th >= a) & (th <= b)
        bands.append((a, b, r[sel].mean(), np.sqrt((r[sel] ** 2).mean())))
    return m, c, rows, bands


def main():
    workdir = sys.argv[1]
    pairs = list(zip(sys.argv[2::2], sys.argv[3::2]))
    for job, ref in pairs:
        jd = os.path.join(workdir, "jobs", job)
        fs, fp = read_xrcx(os.path.join(jd, "fit.xrcx"))
        rs, rp = read_xrcx(ref)
        jj = json.load(open(os.path.join(jd, "job.json"), encoding="utf-8-sig"))
        print("=" * 100)
        print(f"JOB {job}  state {jj.get('state')}  chi2 {jj.get('best_value')}  iter {jj.get('iteration')}/{jj.get('max_iterations')}  {jj.get('elapsed_s')} s")
        print(f"  fit settings: Mode {fp.get('Mode')} PolyOrder {fp.get('PolyOrder')} Pop {fp.get('Pop')} Namx {fp.get('Namx')} width {fp.get('width')} MinLimit {fp.get('MinLimit')} TWChi {fp.get('TWChi')} PWChi {fp.get('PWChi')} range {fp.get('Start')}-{fp.get('End')}")
        print(f"  ref settings: Mode {rp.get('Mode')} PolyOrder {rp.get('PolyOrder')} Pop {rp.get('Pop')} width {rp.get('width')} MinLimit {rp.get('MinLimit')} TWChi {rp.get('TWChi')} range {rp.get('Start')}-{rp.get('End')} 2teta={rp.get('2teta')}")
        chi2 = jj.get("best_value")
        verdict = []
        if chi2 is not None:
            verdict.append(("chi2 < 10", chi2 < TOL["chi2"], f"{chi2:.3f}"))
        pf, pr = period(fs), period(rs)
        if pf and pr:
            verdict.append(("period within 0.3 A", abs(pf - pr) <= TOL["period"], f"{pf:.2f} vs {pr:.2f} (d {pf-pr:+.2f})"))
        print(f"  substrate: fit s {fs['Subs']['s']:.2f} r {fs['Subs']['r']:.2f} | ref s {rs['Subs']['s']:.2f} r {rs['Subs']['r']:.2f}")
        print(f"  {'layer':6} {'N':>3} | {'H fit':>7} {'H ref':>7} {'dH':>6} | {'s fit':>6} {'s ref':>6} {'ds':>6} | {'r fit':>6} {'r ref':>6} | bound?")
        for (M, N, H, s, r, hb, sb, rb), (M2, N2, H2, s2, r2, *_) in zip(layers(fs), layers(rs)):
            flags = []
            if near_bound(H, *hb): flags.append("H")
            if near_bound(s, *sb): flags.append("s")
            if near_bound(r, *rb): flags.append("r")
            print(f"  {M:6} {N:3d} | {H:7.2f} {H2:7.2f} {H-H2:+6.2f} | {s:6.2f} {s2:6.2f} {s-s2:+6.2f} | {r:6.2f} {r2:6.2f} | {' '.join(flags) or '-'}")
            verdict.append((f"{M} thickness within 1 A", abs(H - H2) <= TOL["H"], f"{H-H2:+.2f}"))
            verdict.append((f"{M} sigma within 1 A", abs(s - s2) <= TOL["s"], f"{s-s2:+.2f}"))
        m, c, rows, bands = order_table(jd, pf or period(rs))
        print(f"  Bragg orders from the fitted period (+-0.06 deg): n theta_m R_m | theta_c R_c | ratio c/m   (visible = measured peak > 3x the local floor)")
        allok = True
        nvis = 0
        floor = np.median(m[-100:, 1])
        for (n, tm, rm, tc, rc, ratio) in rows:
            visible = rm > 3 * floor
            ok = abs(ratio - 1) <= TOL["order"]
            if visible:
                nvis += 1
                allok &= ok
            print(f"    {n}: {tm:.4f} {rm:.3e} | {tc:.4f} {rc:.3e} | {ratio:.2f} {'ok' if ok else 'OFF'}{'' if visible else '  (below 3x floor, not judged)'}")
        verdict.append(("every visible order within 25 %", allok, f"{nvis} visible orders"))
        print("  log10(calc/meas) by band: mean / rms")
        for a, b, mu, rms in bands:
            flag = abs(mu) > 0.1
            print(f"    {a:.2f}-{b:.2f}: {mu:+.3f} / {rms:.3f}{'  <-- one-sided' if flag else ''}")
        print(f"  (bands are informational; |mean| > 0.1 is flagged, not part of the verdict)")
        print("  VERDICT:")
        for name, ok, note in verdict:
            print(f"    [{'PASS' if ok else 'FAIL'}] {name}: {note}")


if __name__ == "__main__":
    main()
