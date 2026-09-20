"""Seed variation of the cap test (same requests, seeds 1 and 2; with range_seed the start model is irrelevant).
Original docstring: Author's hypothesis (2026-09-19 00:40): the fringe mismatch of the swapped-sigma P2-04 fit comes from a light surface
layer (hydrocarbons) missing from the model. Test: refit P2-04 under the agent's segment-17 conditioning (scale 1.3716e-6,
r_min the same, range 0.20825-5.6, smooth 1, dtheta 0.012, theta^2 + point weighting, 100 x 5000, seed 20260918) with
(A) no cap and (B) a light carbon cap (thickness 5-40 A, sigma 1-10, density 0.6-1.4, all free) on top of the stack,
each from two starts: S = the agent's swapped assignment (sigma_C 2.6 / sigma_Co 4.3), R = the author's (5.6 / 2.5).
Four servers in parallel, each in its own workdir. Prints the fitted structures, chi2, report orders and fringe contrasts.
usage: p204_cap_hypothesis.py <root-workdir>"""
import json, subprocess, sys, os, shutil, threading, time

EXE = r"D:\DelphiProjects\X-RayCalc\X-RayCalc3_Working\_Out\BIN\XRC_MCP.exe"
SRC = r"D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments\runs\exp-03\workdir\inbox\P2-04"
ROOT = sys.argv[1]

def server(w):
    os.makedirs(os.path.join(w, "inbox", "P2-04"), exist_ok=True)
    for f in ("xrr.dat", "meta.json"):
        shutil.copy(os.path.join(SRC, f), os.path.join(w, "inbox", "P2-04", f))
    p = subprocess.Popen([EXE, "--workdir", w], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1)
    st = {"id": 0}
    def rpc(method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None: msg["params"] = params
        if not notify:
            st["id"] += 1; msg["id"] = st["id"]
        p.stdin.write(json.dumps(msg) + "\n"); p.stdin.flush()
        if notify: return None
        while True:
            line = p.stdout.readline()
            if not line: raise RuntimeError("server closed: " + p.stderr.read()[:500])
            try: r = json.loads(line)
            except json.JSONDecodeError: continue
            if r.get("id") == st["id"]:
                if "error" in r: raise RuntimeError(json.dumps(r["error"]))
                return r["result"]
    def call(tool, args):
        r = rpc("tools/call", {"name": tool, "arguments": args})
        text = "".join(c.get("text", "") for c in r.get("content", []))
        if r.get("isError"): raise RuntimeError(text)
        return json.loads(text)
    rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "cap", "version": "0"}})
    rpc("notifications/initialized", notify=True)
    return p, call

def layers(sC, sCo):
    return [{"material": "C", "thickness": 31.2, "sigma": sC, "density": 1.8},
            {"material": "Co", "thickness": 23.5, "sigma": sCo, "density": 7.9}]

def request(cap, sC, sCo, seed=20260918):
    stacks = [{"N": 20, "layers": layers(sC, sCo)}]
    free = [{"stack": 0, "layer": 0, "parameters": ["thickness", "sigma", "density"]},
            {"stack": 0, "layer": 1, "parameters": ["thickness", "sigma", "density"]},
            {"target": "period", "stack": 0}]
    bounds = [{"stack": 0, "layer": 0, "parameter": "thickness", "min": 21.6, "max": 43.2},
              {"stack": 0, "layer": 0, "parameter": "sigma", "min": 1, "max": 8},
              {"stack": 0, "layer": 0, "parameter": "density", "min": 1.5, "max": 2.4},
              {"stack": 0, "layer": 1, "parameter": "thickness", "min": 14.5, "max": 28.9},
              {"stack": 0, "layer": 1, "parameter": "sigma", "min": 1, "max": 8},
              {"stack": 0, "layer": 1, "parameter": "density", "min": 6.0, "max": 8.9},
              {"target": "period", "stack": 0, "min": 48.7, "max": 59.5}]
    if cap:
        stacks.append({"N": 1, "layers": [{"material": "C", "thickness": 15, "sigma": 5, "density": 1.0}]})
        free.append({"stack": 1, "layer": 0, "parameters": ["thickness", "sigma", "density"]})
        bounds += [{"stack": 1, "layer": 0, "parameter": "thickness", "min": 5, "max": 40},
                   {"stack": 1, "layer": 0, "parameter": "sigma", "min": 1, "max": 10},
                   {"stack": 1, "layer": 0, "parameter": "density", "min": 0.6, "max": 1.4}]
    return {"measurement_id": "P2-04/xrr.dat", "lambda": 1.5406, "polarization": "s",
            "structure": {"substrate": {"material": "SiO2", "density": 2.65, "sigma": 3.8}, "stacks": stacks},
            "free": free, "bounds": bounds, "scale": 1.3716e-6, "smooth": {"passes": 1}, "r_min": 1.3716e-6,
            "theta_range": {"min": 0.20825, "max": 5.6}, "resolution": 0.012,
            "chi2": {"theta_weight": 1, "point_weight": True},
            "optimizer": {"iterations": 100, "population": 5000, "range_seed": True},
            "points_inline_max": 0, "seed": seed}

CASES = [("A1 nocap seed 1", False, 2.6, 4.3, 1), ("A2 nocap seed 2", False, 2.6, 4.3, 2),
         ("B1 cap seed 1", True, 2.6, 4.3, 1), ("B2 cap seed 2", True, 2.6, 4.3, 2)]
results = {}

def run(name, cap, sC, sCo, seed):
    w = os.path.join(ROOT, name.split()[0])
    p, call = server(w)
    try:
        j = call("fit_xrr", request(cap, sC, sCo, seed))["job_id"]
        while True:
            s = call("job_wait", {"job_id": j, "wait_s": 300})
            if s.get("state") in ("finished", "failed", "cancelled"): break
        r = call("job_result", {"job_id": j})
        results[name] = (w, j, r)
    except Exception as e:
        results[name] = (w, None, {"error": str(e)})
    finally:
        p.stdin.close()

threads = [threading.Thread(target=run, args=c) for c in CASES]
for t in threads: t.start()
for t in threads: t.join()

for name, cap, sC, sCo, seed in CASES:
    w, j, r = results[name]
    print("=" * 90)
    print(name, "| job", j, "| workdir", w)
    if "error" in r:
        print("  ERROR", r["error"][:400]); continue
    print("  chi2", round(r["chi2"], 3), "from", round(r["chi2_start"], 1), "| period_mode", r.get("period_mode"))
    for st in r["fitted_structure"]["stacks"]:
        for L in st["layers"]:
            print(f"   N{st['N']:2d} {L['material']:3} H {L['thickness']:6.2f} s {L['sigma']:5.2f} r {L['density']:5.2f}")
    rep = r.get("report", {})
    print("  orders:", [(o["n"], round(o["ratio"], 3)) for o in rep.get("orders", []) if o.get("visible")])
    fr = rep.get("fringes", {})
    print("  fringe mean contrast meas", round(fr.get("measured", {}).get("mean_contrast") or 0, 3), "calc", round(fr.get("calculated", {}).get("mean_contrast") or 0, 3))
    print("  bands mean:", [round(b["mean"], 3) for b in rep.get("bands", [])])
    print("  near_bounds:", [(n.get("stack"), n.get("layer"), n.get("parameter"), round(n.get("value"), 3), n.get("bound")) for n in rep.get("near_bounds", [])])
