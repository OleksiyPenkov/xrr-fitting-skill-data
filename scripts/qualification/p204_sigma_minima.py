"""P2-04: the two sigma minima. Measured (agent's normalization), the agent's segment-17 fit (sigma_C 2.64 / sigma_Co 4.33),
the round-3 Sonnet fit (5.70 / 2.75, the author's assignment) and the author's own fit; full range plus two zooms."""
import os, zipfile, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = r"D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments"
agent = os.path.join(E, r"runs\exp-03\workdir\jobs\fit-20260918-233743-691e")
sonnet = os.path.join(E, r"skill-dev-2026-09-18\workdir-T04c\jobs\fit-20260918-222358-b830")
ref = os.path.join(E, r"runs\exp-03\author-reference\author-fit-P2-04-full-fit.xrcx")

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
    a.semilogy(ca[:, 0], ca[:, 1], color="tab:red", lw=1.0, label="agent, segment 17 (σ_C 0.264 / σ_Co 0.433 nm, χ² 7.94)")
    a.semilogy(cs[:, 0], cs[:, 1], color="tab:green", lw=1.0, label="skill session round 3 (σ_C 0.570 / σ_Co 0.275 nm, χ² 7.28)")
    a.semilogy(cr[:, 0], cr[:, 1], color="tab:blue", lw=1.0, ls="--", label="author (σ_C 0.558 / σ_Co 0.246 nm, his normalization)")
    a.grid(alpha=0.3)
ax.set_title("P2-04: the two σ minima of the periodic fit")
ax.set_xlim(0.2, 5.6)
ax.legend(loc="upper right", fontsize=8)
ax.set_ylabel("reflectivity")
z1.set_xlim(0.95, 1.65); z1.set_ylim(3e-5, 3e-2); z1.set_title("fringes between orders 1 and 2", fontsize=10)
z2.set_xlim(3.05, 5.0); z2.set_ylim(1e-6, 2e-3); z2.set_title("orders 4, 5, 6", fontsize=10)
for a in (z1, z2):
    a.set_xlabel("theta (deg)")
z1.set_ylabel("reflectivity")
fig.tight_layout()
out = os.path.join(E, r"fit-review-2026-09-18\P2-04-segment17-two-sigma-minima.png")
fig.savefig(out, dpi=130)
print("wrote", out)
