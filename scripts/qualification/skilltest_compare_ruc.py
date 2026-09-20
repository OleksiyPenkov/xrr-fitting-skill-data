"""Ru/C transfer test (2026-09-19): compare a skill-test fit against the author's published reference fit
(paper 1, Zenodo v1.1 fits.zip), matching stacks by role instead of by position.

usage: skilltest_compare_ruc.py <workdir> <job-id> <reference.xrcx> [paper_mean_period_A]

Roles: "main" = the periodic stack (N > 1), "cap" = a single-layer stack listed before it, "buffer" = a single-layer
stack listed after it (the Ru adhesion layer), "film" = the only stack of a single-film model.  Tolerances as fixed by
the author on 2026-09-18 and confirmed for Ru/C on 2026-09-19: period 0.3 A, thickness 1 A, sigma 1 A, every visible
order within 25 %, chi2 < 10; density not judged; sigma assignment not judged (author 2026-09-19, peaks over fringes).
The period of a reference is the sum of its main-stack thicknesses as stored; paper 1 reports the MEAN period of a
polynomial (profile) fit, which differs by a few tenths of an Angstrom, so the optional fourth argument prints the
comparison against the published mean as well.
"""
import sys, os, json
import numpy as np
from skilltest_compare import read_xrcx, order_table, near_bound, TOL


def roles(struct):
    stacks = struct["Stacks"]
    out = {}
    main_i = [i for i, st in enumerate(stacks) if st["N"] > 1]
    if not main_i:
        # .xrcx lists stacks top-down (the tool writes it the same way): the film is the thickest single layer,
        # anything above it is a cap
        film = max(stacks, key=lambda st: st["Layers"][0]["H"])
        out["film"] = film
        for st in stacks:
            if st is not film:
                out.setdefault("cap" if stacks.index(st) < stacks.index(film) else "extra", st)
        return out
    mi = main_i[0]
    out["main"] = stacks[mi]
    for i, st in enumerate(stacks):
        if i == mi:
            continue
        key = "cap" if st["Layers"][0]["M"].upper() == "C" and st["N"] == 1 else ("buffer" if st["N"] == 1 else "extra")
        if i < mi and key == "buffer":
            key = "cap"  # a single non-carbon layer above the stack
        if i > mi and key == "cap":
            key = "buffer-C"
        out[key] = st
    return out


def fmt_layer(L):
    return f"{L['M']:5} H {L['H']:7.2f} s {L['s']:5.2f} r {L['r']:6.2f}"


def main():
    workdir, job, ref = sys.argv[1:4]
    paper_mean = float(sys.argv[4]) if len(sys.argv) > 4 else None
    jd = os.path.join(workdir, "jobs", job)
    fs, fp = read_xrcx(os.path.join(jd, "fit.xrcx"))
    rs, rp = read_xrcx(ref)
    jj = json.load(open(os.path.join(jd, "job.json"), encoding="utf-8-sig"))
    print("=" * 100)
    print(f"JOB {job}  state {jj.get('state')}  chi2 {jj.get('best_value')}  iter {jj.get('iteration')}/{jj.get('max_iterations')}  {jj.get('elapsed_s')} s")
    print(f"  fit settings: Mode {fp.get('Mode')} PolyOrder {fp.get('PolyOrder')} Pop {fp.get('Pop')} width {fp.get('width')} MinLimit {fp.get('MinLimit')} TWChi {fp.get('TWChi')} PWChi {fp.get('PWChi')}")
    print(f"  ref settings: Mode {rp.get('Mode')} PolyOrder {rp.get('PolyOrder')} Pop {rp.get('Pop')} width {rp.get('width')} MinLimit {rp.get('MinLimit')} TWChi {rp.get('TWChi')}")
    print(f"  substrate: fit s {fs['Subs']['s']:.2f} r {fs['Subs']['r']:.2f} | ref s {rs['Subs']['s']:.2f} r {rs['Subs']['r']:.2f}")
    rf, rr = roles(fs), roles(rs)
    print(f"  fit stacks: {[(k, v['N'], [L['M'] for L in v['Layers']]) for k, v in rf.items()]}")
    print(f"  ref stacks: {[(k, v['N'], [L['M'] for L in v['Layers']]) for k, v in rr.items()]}")
    verdict = []
    chi2 = jj.get("best_value")
    if chi2 is not None:
        verdict.append(("chi2 < 10", chi2 < TOL["chi2"], f"{chi2:.3f}"))
    d_fit = None
    if "main" in rr:
        if "main" not in rf:
            verdict.append(("periodic stack present", False, "the fit has no periodic stack"))
        else:
            mf, mr = rf["main"], rr["main"]
            d_fit = sum(L["H"] for L in mf["Layers"])
            d_ref = sum(L["H"] for L in mr["Layers"])
            verdict.append(("period within 0.3 A (ref = stored layer sum)", abs(d_fit - d_ref) <= TOL["period"], f"{d_fit:.2f} vs {d_ref:.2f} (d {d_fit-d_ref:+.2f}); N fit {mf['N']} ref {mr['N']}"))
            if paper_mean:
                verdict.append(("period within 0.3 A (ref = paper 1 mean period)", abs(d_fit - paper_mean) <= TOL["period"], f"{d_fit:.2f} vs {paper_mean:.2f} (d {d_fit-paper_mean:+.2f})"))
            print(f"  {'main':6} | {'H fit':>7} {'H ref':>7} {'dH':>6} | {'s fit':>6} {'s ref':>6} {'ds':>6} | {'r fit':>6} {'r ref':>6} | bound?")
            byM_r = {L["M"].upper(): L for L in mr["Layers"]}
            for L in mf["Layers"]:
                R = byM_r.get(L["M"].upper())
                flags = [k for k, key in (("H", ("Hmin", "Hmax")), ("s", ("Smin", "Smax")), ("r", ("Rmin", "Rmax"))) if near_bound(L[{"H": "H", "s": "s", "r": "r"}[k]], L[key[0]], L[key[1]])]
                if R is None:
                    print(f"  {L['M']:6} | {L['H']:7.2f} {'-':>7} {'':>6} | {L['s']:6.2f} {'-':>6} | {L['r']:6.2f} | {' '.join(flags) or '-'}  (no counterpart in the reference)")
                    continue
                print(f"  {L['M']:6} | {L['H']:7.2f} {R['H']:7.2f} {L['H']-R['H']:+6.2f} | {L['s']:6.2f} {R['s']:6.2f} {L['s']-R['s']:+6.2f} | {L['r']:6.2f} {R['r']:6.2f} | {' '.join(flags) or '-'}")
                verdict.append((f"{L['M']} thickness within 1 A", abs(L["H"] - R["H"]) <= TOL["H"], f"{L['H']-R['H']:+.2f}"))
                verdict.append((f"{L['M']} sigma within 1 A (not judged: assignment)", abs(L["s"] - R["s"]) <= TOL["s"], f"{L['s']-R['s']:+.2f}"))
    if "film" in rr:
        Lf = rf.get("film", rf.get("main", {"Layers": [None]}))["Layers"][0]
        Lr = rr["film"]["Layers"][0]
        if Lf is None:
            verdict.append(("film thickness within 1 A", False, "no film layer in the fit"))
        else:
            print(f"  film: fit {fmt_layer(Lf)} | ref {fmt_layer(Lr)}")
            verdict.append(("film thickness within 1 A", abs(Lf["H"] - Lr["H"]) <= TOL["H"], f"{Lf['H']-Lr['H']:+.2f}"))
            verdict.append(("film sigma within 1 A (not judged: single film gives thickness only)", abs(Lf["s"] - Lr["s"]) <= TOL["s"], f"{Lf['s']-Lr['s']:+.2f}"))
    for key in ("cap", "buffer"):
        Lr = rr[key]["Layers"][0] if key in rr else None
        Lf = rf[key]["Layers"][0] if key in rf else None
        if Lr is None and Lf is None:
            continue
        print(f"  {key:6}: fit {fmt_layer(Lf) if Lf else 'absent'} | ref {fmt_layer(Lr) if Lr else 'absent'}")
        if Lr is not None and Lf is not None:
            verdict.append((f"{key} thickness within 1 A (reported, the author's ruling on whether it is judged is pending)", abs(Lf["H"] - Lr["H"]) <= TOL["H"], f"{Lf['H']-Lr['H']:+.2f}"))
        elif Lr is not None:
            verdict.append((f"{key} present in the model", False, "the reference has it, the fit does not"))
    d_for_orders = d_fit or (sum(L["H"] for L in rr["main"]["Layers"]) if "main" in rr else None)
    if d_for_orders:
        m, c, rows, bands = order_table(jd, d_for_orders)
        print("  Bragg orders from the fitted period (+-0.06 deg): n theta_m R_m | theta_c R_c | ratio c/m")
        allok, nvis = True, 0
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
            print(f"    {a:.2f}-{b:.2f}: {mu:+.3f} / {rms:.3f}{'  <-- one-sided' if abs(mu) > 0.1 else ''}")
    print("  VERDICT:")
    for name, ok, note in verdict:
        print(f"    [{'PASS' if ok else 'FAIL'}] {name}: {note}")


if __name__ == "__main__":
    main()
