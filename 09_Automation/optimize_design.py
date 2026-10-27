"""Pareto analysis and shortlist generation.

Reads:
  07_Results/summary_0V.csv      (D/J/Z/C experiments, MODE + CHARGE)
  01_Geometry_Sweeps/geometry_metrics.csv (MODE-only geometry screening)
Writes:
  07_Results/pareto_front.csv
  07_Results/best_designs.csv
  07_Results/pareto_geometry.csv
"""
import os, json, glob
import numpy as np
import pandas as pd

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
R = os.path.join(ROOT, "07_Results")

BASE = dict(loss=498.2313, VpiL=2.9080, Cj=0.2100, Gcore=0.35355,
            neff=2.567082, ng=3.936389, Aeff=2.0561e-13, TE=0.9866)


def pareto_mask(df, minimize, maximize, rtol=1e-3):
    """Boolean mask of non-dominated rows (NaN rows excluded).

    Dominance uses a 0.1 % relative tolerance per objective so that sub-grid
    numerical noise (e.g. 1e-5 differences in Gamma_core / Cj) does not keep a
    clearly inferior design on the front.  The tolerance is a numerical
    robustness choice, not a weighting between objectives.
    """
    cols = minimize + maximize
    d = df.dropna(subset=cols)
    keep = []
    for i, r in d.iterrows():
        dom = False
        for j, s in d.iterrows():
            if i == j:
                continue
            ok = True
            strict = False
            for c in minimize:
                tol = rtol * max(abs(float(r[c])), 1e-12)
                if s[c] > r[c] + tol:
                    ok = False
                    break
                if s[c] < r[c] - tol:
                    strict = True
            if ok:
                for c in maximize:
                    tol = rtol * max(abs(float(r[c])), 1e-12)
                    if s[c] < r[c] - tol:
                        ok = False
                        break
                    if s[c] > r[c] + tol:
                        strict = True
            if ok and strict:
                dom = True
                break
        if not dom:
            keep.append(i)
    return set(keep)


def main():
    frames = []
    sp = os.path.join(R, "summary_0V.csv")
    if os.path.exists(sp):
        s = pd.read_csv(sp)
        s = s.rename(columns={"loss_0V": "loss", "VpiL_Vcm": "VpiL",
                              "Cj_0V_fF_um": "Cj", "Gamma_core": "Gcore"})
        s["source"] = "CHARGE+MODE"
        frames.append(s)
    gp = os.path.join(ROOT, "01_Geometry_Sweeps", "geometry_metrics.csv")
    if os.path.exists(gp):
        g = pd.read_csv(gp)
        g = g.rename(columns={"loss_dB_m": "loss"})
        g["Gcore"] = g["Gamma_core"]
        g["status"] = "SUCCESS (MODE-only, baseline charge)"
        g["source"] = "MODE-only"
        g["VpiL"] = np.nan
        g["Cj"] = np.nan
        g["family"] = "01_Geometry_Sweeps"
        g["neff_0V"] = g["neff_re"]
        g["ng_0V"] = g["ng"]
        g["dneff_0_4V"] = np.nan
        g["Aeff"] = g["Aeff_m2"]
        g["TE_frac"] = g["TE_frac"]
        frames.append(g)
    if not frames:
        print("no data"); return
    df = pd.concat(frames, ignore_index=True, sort=False)

    # improvements vs baseline
    df["d_loss_pct"] = 100 * (BASE["loss"] - df["loss"]) / abs(BASE["loss"])
    df["d_Gcore_pct"] = 100 * (df["Gcore"] - BASE["Gcore"]) / abs(BASE["Gcore"])
    df["d_VpiL_pct"] = 100 * (BASE["VpiL"] - df["VpiL"]) / abs(BASE["VpiL"])
    df["d_Cj_pct"] = 100 * (BASE["Cj"] - df["Cj"]) / abs(BASE["Cj"])

    # geometry Pareto: min loss, max Gcore
    geo = df[df["source"] == "MODE-only"].dropna(subset=["loss", "Gcore"]).copy()
    if len(geo):
        idx = pareto_mask(geo.set_index("exp"), ["loss"], ["Gcore"])
        geo["pareto"] = [e in idx for e in geo["exp"]]
        geo.sort_values("loss").to_csv(os.path.join(R, "pareto_geometry.csv"), index=False)
        print("geometry Pareto:", list(geo.loc[geo["pareto"], "exp"]))

    # electrical family Pareto: min loss, min VpiL, min Cj, max Gcore
    el = df[df["source"] == "CHARGE+MODE"].dropna(
        subset=["loss", "VpiL", "Cj", "Gcore"]).copy()
    if len(el):
        idx = pareto_mask(el.set_index("exp"), ["loss", "VpiL", "Cj"], ["Gcore"])
        el["pareto"] = [e in idx for e in el["exp"]]
        el.sort_values(["loss"]).to_csv(os.path.join(R, "pareto_front.csv"), index=False)
        print("electrical Pareto:", list(el.loc[el["pareto"], "exp"]))

    df.to_csv(os.path.join(R, "best_designs.csv"), index=False)
    print("wrote best_designs.csv, pareto_front.csv, pareto_geometry.csv")


if __name__ == "__main__":
    main()
