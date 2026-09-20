"""Overlay: measured (scaled) curve of a skill-test job, its calculated curve, and the author's calculated curve
from his reference .xrcx (his data are shown too, on his own normalization).
usage: overlay_vs_author.py <workdir> <job-id> <reference.xrcx> <out.png> <title>"""
import sys, os, zipfile, io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

workdir, job, ref, out, title = sys.argv[1:6]
jd = os.path.join(workdir, "jobs", job)
m = np.loadtxt(os.path.join(jd, "measured.dat"), skiprows=1)
c = np.loadtxt(os.path.join(jd, "calc.dat"), skiprows=1)


def load_xrcx_curve(z, name):
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


z = zipfile.ZipFile(ref)
rc = load_xrcx_curve(z, "calc.dat")
rd = load_xrcx_curve(z, [n for n in z.namelist() if n.startswith("data")][0])

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
ax.semilogy(m[:, 0], m[:, 1], color="0.3", lw=0.8, label="measured (skill session's normalization)")
ax.semilogy(c[:, 0], c[:, 1], color="tab:red", lw=1.0, label=f"skill session fit {job[-4:]}")
ax.semilogy(rc[:, 0], rc[:, 1], color="tab:blue", lw=1.0, ls="--", label="author's fit (his normalization)")
ax.set_ylabel("reflectivity")
ax.set_title(title)
ax.legend(loc="upper right", fontsize=9)
ax.grid(alpha=0.3)
# residuals on a common grid
ok = (m[:, 1] > 0) & (c[:, 1] > 0)
ax2.plot(m[ok, 0], np.log10(c[ok, 1] / m[ok, 1]), color="tab:red", lw=0.7, label="log10(calc/meas), skill session")
rci = np.interp(rd[:, 0], rc[:, 0], rc[:, 1])
okr = (rd[:, 1] > 0) & (rci > 0)
ax2.plot(rd[okr, 0], np.log10(rci[okr] / rd[okr, 1]), color="tab:blue", lw=0.7, ls="--", label="log10(calc/meas), author")
ax2.axhline(0, color="k", lw=0.5)
ax2.set_ylim(-1, 1)
ax2.set_xlabel("theta (deg)")
ax2.set_ylabel("log residual")
ax2.legend(loc="upper right", fontsize=8)
ax2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(out, dpi=130)
print("wrote", out)
