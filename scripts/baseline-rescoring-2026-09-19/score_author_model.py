"""Score the author's reference structure with the tool under a test session's own cost function (2026-09-19).

usage: score_author_model.py <session-workdir> <job-id> <reference.xrcx> <stream.jsonl> [theta_weight_override]

The author's fit files carry no chi2, and his GUI settings (TWChi 0) differ from the skill's (theta_weight 1), so the
only like-for-like number is chi2 of BOTH structures on the SAME conditioned curve under ONE cost function.  This
script clones the session's accepted fit request (same measurement, range, r_min, smoothing, resolution, chi2 weights,
numeric scale as echoed in the stream), swaps in the author's structure, submits it with iterations 1 / population 2
and one dummy free parameter, and reads `report.chi2_start` = chi2 of the author's model as the start model.  It does the
same for the session's own fitted structure (from fit.xrcx) so the two numbers come from identical calls.  With a
theta_weight override both are also scored under that weighting (0 = the author's GUI setting).
Runs in a scratch copy of the inbox (workdir-SCORE-<spec>), never in the session's workdir.
"""
import sys, os, json, shutil, subprocess, time, copy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from skilltest_compare import read_xrcx

XRC = r"D:\DelphiProjects\X-RayCalc\X-RayCalc3_Working\_Out\BIN\XRC_MCP.exe"
MAT = {"RU": "Ru", "C": "C", "CO": "Co", "SIO2": "SiO2", "SI": "Si", "W": "W", "NI": "Ni", "CR": "Cr"}


def xrcx_to_json(struct):
    """The .xrcx lists stacks top-down; the tool lists them substrate-up, with single layers as cap/buffer."""
    stacks = struct["Stacks"]
    main_i = [i for i, st in enumerate(stacks) if st["N"] > 1]
    lay = lambda L: {"material": MAT.get(L["M"].upper(), L["M"]), "thickness": L["H"], "sigma": L["s"], "density": L["r"]}
    out = {"substrate": {"material": MAT.get(struct["Subs"]["M"].upper(), struct["Subs"]["M"]), "density": struct["Subs"]["r"], "sigma": struct["Subs"]["s"]}}
    if not main_i:  # single film (+ possible cap above it)
        out["stacks"] = [{"N": 1, "layers": [lay(L) for L in stacks[-1]["Layers"]]}]
        if len(stacks) > 1:
            out["cap"] = lay(stacks[0]["Layers"][0])
        return out
    mi = main_i[0]
    out["stacks"] = [{"N": stacks[mi]["N"], "layers": [lay(L) for L in stacks[mi]["Layers"]]}]
    above = [st for st in stacks[:mi]]
    below = [st for st in stacks[mi + 1:]]
    if above:
        if len(above) == 1 and above[0]["N"] == 1 and len(above[0]["Layers"]) == 1:
            out["cap"] = lay(above[0]["Layers"][0])
        else:
            out["stacks"] += [{"N": st["N"], "layers": [lay(L) for L in st["Layers"]]} for st in above[::-1]]
    if below:
        if len(below) == 1 and below[0]["N"] == 1 and len(below[0]["Layers"]) == 1:
            out["buffer"] = lay(below[0]["Layers"][0])
        else:
            out["stacks"] = [{"N": st["N"], "layers": [lay(L) for L in st["Layers"]]} for st in below[::-1]] + out["stacks"]
    return out


def scale_from_stream(stream, job_id):
    """The numeric scale the server echoed for this job (scale "auto" is resolved against the start model)."""
    for line in open(stream, encoding="utf-8"):
        if job_id not in line or "scale" not in line:
            continue
        d = json.loads(line)
        for c in d.get("message", {}).get("content", []):
            if c.get("type") == "tool_result":
                txt = c["content"] if isinstance(c["content"], str) else " ".join(x.get("text", "") for x in c["content"])
                try:
                    j = json.loads(txt)
                except Exception:
                    continue
                if isinstance(j, dict) and j.get("job_id") == job_id and isinstance(j.get("scale"), (int, float)):
                    return j["scale"]
                for v in j.values() if isinstance(j, dict) else []:
                    if isinstance(v, dict) and v.get("job_id") == job_id and isinstance(v.get("scale"), (int, float)):
                        return v["scale"]
    return None


class MCP:
    def __init__(self, workdir):
        self.p = subprocess.Popen([XRC, "--workdir", workdir], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1)
        self.n = 0
        self.call_raw("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "score", "version": "0"}})
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"); self.p.stdin.flush()

    def call_raw(self, method, params):
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}) + "\n"); self.p.stdin.flush()
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("server closed")
            d = json.loads(line)
            if d.get("id") == self.n:
                return d

    def tool(self, name, args):
        d = self.call_raw("tools/call", {"name": name, "arguments": args})
        r = d.get("result", d)
        txt = " ".join(c.get("text", "") for c in r.get("content", [])) if isinstance(r, dict) and "content" in r else json.dumps(r)
        try:
            return json.loads(txt)
        except Exception:
            return {"raw": txt, "error": d.get("error")}

    def close(self):
        try:
            self.p.stdin.close(); self.p.wait(timeout=10)
        except Exception:
            self.p.kill()


def score(mcp, req, structure, label):
    r = copy.deepcopy(req)
    r["structure"] = structure
    r["free"] = [{"stack": 0, "layer": 0, "parameters": ["sigma"]}]
    s0 = structure["stacks"][0]["layers"][0]["sigma"]
    r["bounds"] = [{"stack": 0, "layer": 0, "parameter": "sigma", "min": max(0.1, s0 - 0.5), "max": s0 + 0.5}]
    r["optimizer"] = {"iterations": 1, "population": 2, "range_seed": False}
    r.pop("profile", None); r.pop("paired", None); r.pop("poly_order", None)
    res = mcp.tool("fit_xrr", r)
    jid = res.get("job_id")
    if not jid:
        return {"label": label, "error": res}
    for _ in range(40):
        w = mcp.tool("job_wait", {"job_id": jid, "wait_s": 60})
        if w.get("state") in ("finished", "failed", "error"):
            break
    out = mcp.tool("job_result", {"job_id": jid})
    rep = out.get("report", {}) if isinstance(out, dict) else {}
    return {"label": label, "job": jid, "chi2_start": rep.get("chi2_start"), "chi2_after_1_iter": rep.get("chi2"), "period_A": rep.get("period_A"),
            "orders_start": [(o.get("n"), o.get("ratio")) for o in ((rep.get("start") or {}).get("orders") or [])], "error": out.get("error") if isinstance(out, dict) else None}


def main():
    workdir, job, ref, stream = sys.argv[1:5]
    tw = float(sys.argv[5]) if len(sys.argv) > 5 else None
    jd = os.path.join(workdir, "jobs", job)
    req = json.load(open(os.path.join(jd, "request.json"), encoding="utf-8-sig"))
    spec = req["measurement_id"].split("/")[0]
    sc = scale_from_stream(stream, job)
    if sc is None and not isinstance(req.get("scale"), (int, float)):
        raise SystemExit("numeric scale not found in the stream for " + job)
    if sc is not None:
        req["scale"] = sc
    req.pop("auto_theta_max", None); req.pop("scale_auto", None)
    author = xrcx_to_json(read_xrcx(ref)[0])
    session = xrcx_to_json(read_xrcx(os.path.join(jd, "fit.xrcx"))[0])
    sw = os.path.join(HERE, f"workdir-SCORE-{spec}")
    for sub in ("jobs", "log", "projects"):
        os.makedirs(os.path.join(sw, sub), exist_ok=True)
    dst = os.path.join(sw, "inbox", spec)
    if not os.path.exists(dst):
        shutil.copytree(os.path.join(workdir, "inbox", spec), dst)
    print(f"session job {job}  scale {req['scale']}  range {req['theta_range']}  r_min {req['r_min']}  res {req['resolution']}  chi2 {req['chi2']}")
    print("author structure:", json.dumps(author))
    print("session structure:", json.dumps(session))
    mcp = MCP(sw)
    results = []
    variants = [("session weights", req["chi2"])]
    if tw is not None:
        variants.append((f"theta_weight {tw:g}", {**req["chi2"], "theta_weight": tw}))
    for vname, chi in variants:
        r = copy.deepcopy(req); r["chi2"] = chi
        results.append(score(mcp, r, author, f"author model, {vname}"))
        results.append(score(mcp, r, session, f"session model, {vname}"))
    mcp.close()
    print()
    for x in results:
        print(json.dumps(x))
    json.dump({"session_job": job, "reference": os.path.basename(ref), "results": results}, open(os.path.join(jd, "author-model-score.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
