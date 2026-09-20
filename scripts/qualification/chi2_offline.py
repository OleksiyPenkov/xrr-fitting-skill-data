"""Offline reproduction of X-Ray Calc's chi2 (Shared/Math/unit_calc.pas, TCalc.CalcChiSquare), 2026-09-19.

chi2 = 1000/(N-1) * sum_{i=tail}^{N-tail-2} w_i * theta_w(theta_i) * ((log10 D_i - log10 R_i) / log10 R_i)^2
  w_i = D_i / movavg(D)_i when that ratio > 3, else 1     (point weight; movavg window in theta, default 0.05 deg)
  theta_w = theta^2 for theta_weight 1, 1 for theta_weight 0
  tail = round(0.1/delta) made odd, delta = (theta_last - theta_first)/N, when the calculated curve is convolved
         (resolution > 0); 0 otherwise.  Points with R_i = 0 are skipped.

usage: chi2_offline.py <measured.dat> <calc.dat> <theta_weight> <resolution> [movavg_window]
  (two-column files with one header line; theta in degrees; same grid)
or import chi2(theta, D, R, theta_weight, resolution, movavg_window).
"""
import sys
import numpy as np


def movavg(theta, D, W):
    """unit_DataProcessing.MovAvg(Inp, W): W > 1 = a point count, W <= 1 = that FRACTION of the curve's points
    (the server's default 0.05 is 5 % of the points, not 0.05 degrees).  Trailing average of Window+1 points written
    at i - Window div 2; the first Offset+1 points are copied; the last Offset+1 points get the last average."""
    n = len(D)
    window = int(W) if W > 1 else int(round(n * W))
    offset = window // 2
    out = np.empty_like(D)
    V = 0.0
    for i in range(window, n):
        V = D[i - window:i + 1].sum() / (window + 1)
        out[i - offset] = V
    out[:offset + 1] = D[:offset + 1]
    out[n - 1 - offset:] = V
    return out


def chi2(theta, D, R, theta_weight=1, resolution=0.012, movavg_window=0.05, point_weight=True, tail=None):
    N = len(D)
    if tail is None:
        if resolution > 0:
            delta = (theta[-1] - theta[0]) / N
            tail = int(round(0.1 / delta))
            if tail % 2 == 0:
                tail -= 1
        else:
            tail = 0
    ma = movavg(theta, D, movavg_window) if point_weight else None
    s = 0.0
    for i in range(tail, N - tail - 1):
        if R[i] <= 0 or D[i] <= 0:
            continue
        lr = np.log10(R[i])
        c = ((np.log10(D[i]) - lr) / lr) ** 2
        if ma is not None:
            ratio = D[i] / ma[i]
            if ratio > 3:
                c *= ratio
        if theta_weight == 1:
            c *= theta[i] ** 2
        elif theta_weight == 2:
            c *= theta[i]
        s += c
    return s / (N - 1) * 1000


def load(path):
    a = np.loadtxt(path, skiprows=1)
    return a[:, 0], a[:, 1]


if __name__ == "__main__":
    m, c = sys.argv[1], sys.argv[2]
    tw = int(sys.argv[3]); res = float(sys.argv[4]); win = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
    t, D = load(m); t2, R = load(c)
    assert len(t) == len(t2)
    print(chi2(t, D, R, tw, res, win))
