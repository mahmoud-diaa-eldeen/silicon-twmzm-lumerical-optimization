"""Suggest combined candidates from the validated individual sweeps.

Selection rule (documented, not a universal threshold):
  * feasibility: VpiL <= 1.25 x baseline and Cj <= 1.25 x baseline;
  * among feasible doping/junction/vertical variants pick the lowest loss;
  * combine the winners with the best geometry (thinnest slab that improved
    both Gamma_core and loss in the MODE-only sweep) and store the full
    parameter set in combined_config.json.
"""
import os, json
import pandas as pd
import numpy as np

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
R = os.path.join(ROOT, "07_Results")
# Recorded baseline (original 25,271-point charge mesh).  Overwritten below by
# the B000 re-run (same mesh as all clean experiments) when available.
BASE = dict(loss=498.2313, VpiL=2.9080, Cj=0.2100, Gcore=0.35355,
            neff=2.567082, ng=3.936389, Aeff=2.0561e-13, TE=0.9866)

s = pd.read_csv(os.path.join(R, "summary_0V.csv"))
s = s[s["status"].astype(str).str.startswith("SUCCESS")].copy()
s = s.dropna(subset=["loss_0V", "VpiL_Vcm", "Cj_0V_fF_um"])
b0 = s[s["exp"] == "B000"]
if len(b0):
    b0 = b0.iloc[0]
    BASE.update(loss=float(b0["loss_0V"]), VpiL=float(b0["VpiL_Vcm"]),
                Cj=float(b0["Cj_0V_fF_um"]), Gcore=float(b0["Gamma_core"]))
    print("baseline (B000): loss=%.1f VpiL=%.3f Cj=%.4f Gcore=%.3f"
          % (BASE["loss"], BASE["VpiL"], BASE["Cj"], BASE["Gcore"]))

def pick(prefix):
    d = s[s["exp"].str.startswith(prefix)].copy()
    if not len(d):
        return None
    feas = d[(d["VpiL_Vcm"] <= 1.25*BASE["VpiL"]) &
             (d["Cj_0V_fF_um"] <= 1.25*BASE["Cj"])]
    pool = feas if len(feas) else d
    return pool.sort_values("loss_0V").iloc[0]

dD, dJ, dZ = pick("D"), pick("J"), pick("Z")
print("doping pick  :", None if dD is None else
      (dD["exp"], round(dD["loss_0V"], 1), round(dD["VpiL_Vcm"], 3), round(dD["Cj_0V_fF_um"], 4)))
print("junction pick:", None if dJ is None else
      (dJ["exp"], round(dJ["loss_0V"], 1), round(dJ["VpiL_Vcm"], 3), round(dJ["Cj_0V_fF_um"], 4)))
print("vertical pick:", None if dZ is None else
      (dZ["exp"], round(dZ["loss_0V"], 1), round(dZ["VpiL_Vcm"], 3), round(dZ["Cj_0V_fF_um"], 4)))

# best geometry: lowest loss among geometry cases that also improve Gamma_core.
# The geometry screening was run at 0 V on the recorded baseline charge; its
# G000 case reproduces the B000 0 V baseline (498.2 dB/m), so it is directly
# comparable with the CHARGE+MODE experiments.
gpath = os.path.join(ROOT, "01_Geometry_Sweeps", "geometry_metrics.csv")
g = pd.read_csv(gpath)
best_g = g[g["Gamma_core"] > BASE["Gcore"]].sort_values("loss_dB_m").iloc[0]
print("geometry pick:", best_g["exp"], best_g["W_nm"], best_g["slab_nm"],
      round(best_g["loss_dB_m"], 1), round(best_g["Gamma_core"], 3))
W = float(best_g["W_nm"]); ts = float(best_g["slab_nm"])

def exparams(row):
    j = json.load(open(os.path.join(ROOT, "02_Doping_Sweeps", row["exp"], "experiment.json"),
                       encoding="utf-8")) if row["exp"].startswith("D") else None
    if j is None:
        # junction / vertical experiments use baseline doping
        for fam in ("03_Junction_Position", "04_Vertical_Doping_Profiles"):
            p = os.path.join(ROOT, fam, row["exp"], "experiment.json")
            if os.path.exists(p):
                j = json.load(open(p, encoding="utf-8"))
                break
    return (j or {}).get("params", {})

pD = exparams(dD) if dD is not None else {}
pJ = exparams(dJ) if dJ is not None else {}
pZ = exparams(dZ) if dZ is not None else {}

def geo_of(row):
    if row is None:
        return {}
    for fam in ("03_Junction_Position", "04_Vertical_Doping_Profiles"):
        p = os.path.join(ROOT, fam, row["exp"], "experiment.json")
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8")).get("geom", {}) or {}
    return {}

cfgs = []
base_params = dict(p_wg=5e23, n_wg=7e23, p_imp=7e23, n_imp=5e23)
cfgs.append(dict(exp="C001", W_nm=W, slab_nm=ts,
                 **{k: pD.get(k, base_params[k]) for k in base_params},
                 description="best geometry + best doping (%s)" % (dD["exp"] if dD is not None else "baseline"),
                 dx=0, zmin_p=None, zmax_p=None, zmin_n=None, zmax_n=None))
gj = geo_of(dJ)
cfgs.append(dict(exp="C002", W_nm=W, slab_nm=ts,
                 **{k: pD.get(k, base_params[k]) for k in base_params},
                 description="best geometry + best doping + junction %s" % (dJ["exp"] if dJ is not None else ""),
                 dx=gj.get("dx", 0),
                 zmin_p=None, zmax_p=None, zmin_n=None, zmax_n=None))
gz = geo_of(dZ)
cfgs.append(dict(exp="C003", W_nm=W, slab_nm=ts,
                 **{k: pD.get(k, base_params[k]) for k in base_params},
                 description="best geometry + best doping + vertical %s" % (dZ["exp"] if dZ is not None else ""),
                 dx=0,
                 zmin_p=gz.get("zmin_p"), zmax_p=gz.get("zmax_p"),
                 zmin_n=gz.get("zmin_n"), zmax_n=gz.get("zmax_n")))

# Low-loss end of the Pareto front: the feasibility screen excludes D001/D002
# because of their VpiL penalty, but the study must also quantify the low-loss
# combined point.  C004 combines the best geometry with D001 (x0.5 doping).
d_low = s[s["exp"] == "D001"]
d_low = d_low.iloc[0] if len(d_low) else None
pD_low = exparams(d_low) if d_low is not None else {}
if d_low is not None:
    cfgs.append(dict(exp="C004", W_nm=W, slab_nm=ts,
                     **{k: pD_low.get(k, base_params[k]) for k in base_params},
                     description="best geometry + low-loss doping (D001, Pareto low-loss end)",
                     dx=0, zmin_p=None, zmax_p=None, zmin_n=None, zmax_n=None))

out = os.path.join(R, "combined_config.json")
json.dump(cfgs, open(out, "w"), indent=1)
print("wrote", out)
for c in cfgs:
    print(c["exp"], c["description"], "W=%.0f slab=%.0f" % (c["W_nm"], c["slab_nm"]),
          "dx=%s" % c.get("dx"), "z=%s..%s/%s..%s" %
          (c.get("zmin_p"), c.get("zmax_p"), c.get("zmin_n"), c.get("zmax_n")))
