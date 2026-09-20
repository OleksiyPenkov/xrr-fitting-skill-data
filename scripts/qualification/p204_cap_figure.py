"""P2-04 fringe fields: measured, the no-cap fit (sigma swapped, chi2 7.94), the same with a light surface layer
(12.6 A, rho 0.68, chi2 6.09) and the round-3 fit in the other sigma minimum (chi2 7.28)."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
E = r"D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments"
nocap = os.path.join(E, r"skill-dev-2026-09-18\workdir-CAP\A-S\jobs\fit-20260919-061017-879e")
cap = os.path.join(E, r"skill-dev-2026-09-18\workdir-CAP\B-S\jobs\fit-20260919-061017-4587")
other = os.path.join(E, r"skill-dev-2026-09-18\workdir-T04c\jobs\fit-20260918-222358-b830")
m = np.loadtxt(os.path.join(nocap, "measured.dat"), skiprows=1)
c0 = np.loadtxt(os.path.join(nocap, "calc.dat"), skiprows=1)
c1 = np.loadtxt(os.path.join(cap, "calc.dat"), skiprows=1)
c2 = np.loadtxt(os.path.join(other, "calc.dat"), skiprows=1)
fig, axs = plt.subplots(1, 3, figsize=(14, 4.6))
wins = [(0.95, 1.65, 3e-5, 3e-2, "between orders 1 and 2"), (1.75, 2.4, 1e-6, 3e-3, "between orders 2 and 3"), (0.2, 0.9, 1e-3, 1.2, "edge and first fringes")]
for a, (x0, x1, y0, y1, t) in zip(axs, wins):
    a.semilogy(m[:, 0], m[:, 1], color="0.25", lw=0.8, label="measured × scale")
    a.semilogy(c0[:, 0], c0[:, 1], color="tab:red", lw=1.0, label="no surface layer, σ 0.264 / 0.433 nm, χ² 7.94")
    a.semilogy(c1[:, 0], c1[:, 1], color="tab:orange", lw=1.0, label="+ C 1.26 nm ρ 0.68 on top, σ 0.263 / 0.446 nm, χ² 6.09")
    a.semilogy(c2[:, 0], c2[:, 1], color="tab:green", lw=1.0, ls="--", label="other minimum, σ 0.570 / 0.275 nm, no layer, χ² 7.28")
    a.set_xlim(x0, x1); a.set_ylim(y0, y1); a.set_title(t, fontsize=10); a.grid(alpha=0.3); a.set_xlabel("theta (deg)")
axs[0].set_ylabel("reflectivity")
axs[0].legend(fontsize=7, loc="lower left")
fig.suptitle("P2-04: does a light surface layer explain the fringe mismatch of the swapped-σ fit?")
fig.tight_layout()
out = os.path.join(E, r"fit-review-2026-09-18\P2-04-surface-layer-hypothesis.png")
fig.savefig(out, dpi=130); print("wrote", out)
