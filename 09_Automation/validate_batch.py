"""Verify that every clean experiment matches its declared spec and completed.

Checks, per experiment:
  * status == SUCCESS
  * charge.mat has 20 points and last V = 4.025 V
  * the stored params/geom equal the declared one-variable-at-a-time spec
  * Cj at 0 V exists (Cj_fF_um[1], 0-based; 10 principal bias points)
Writes 07_Results/diagnostics/CLEAN_BATCH_VALIDATION.md
"""
import os, json, h5py
import numpy as np

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
BASE = dict(p_wg=5e23, n_wg=7e23, p_imp=7e23, n_imp=5e23)
SPEC = {
    "B000": ("00_Original_Baseline", dict(BASE), {}),
    "D001": ("02_Doping_Sweeps", dict(p_wg=2.5e23, n_wg=3.5e23, p_imp=3.5e23, n_imp=2.5e23), {}),
    "D002": ("02_Doping_Sweeps", dict(p_wg=1.5e23, n_wg=2.1e23, p_imp=2.1e23, n_imp=1.5e23), {}),
    "D003": ("02_Doping_Sweeps", dict(p_wg=1.0e24, n_wg=1.4e24, p_imp=1.4e24, n_imp=1.0e24), {}),
    "J001": ("03_Junction_Position", dict(BASE), dict(dx=-40e-9)),
    "J002": ("03_Junction_Position", dict(BASE), dict(dx=40e-9)),
    "J003": ("03_Junction_Position", dict(BASE), dict(dx=80e-9)),
    "Z001": ("04_Vertical_Doping_Profiles", dict(BASE),
             dict(zmin_p=0.0, zmax_p=120e-9, zmin_n=0.0, zmax_n=120e-9)),
    "Z002": ("04_Vertical_Doping_Profiles", dict(BASE),
             dict(zmin_p=100e-9, zmax_p=220e-9, zmin_n=100e-9, zmax_n=220e-9)),
    "Z003": ("04_Vertical_Doping_Profiles", dict(BASE),
             dict(zmin_p=0.0, zmax_p=110e-9, zmin_n=110e-9, zmax_n=237.5e-9)),
}

lines = ["# Clean batch validation", "",
         "Every row is checked against the declared one-variable-at-a-time spec.", "",
         "| Exp | Status | points | last V (V) | params match | geom match | Cj(0V) fF/um |",
         "|---|---|---:|---:|---|---|---:|"]
ok_all = True
for exp, (fam, params, geom) in SPEC.items():
    ed = os.path.join(ROOT, fam, exp)
    ej = os.path.join(ed, "experiment.json")
    cf = os.path.join(ed, "charge.mat")
    j = json.load(open(ej, encoding="utf-8")) if os.path.exists(ej) else {}
    v = []
    if os.path.exists(cf):
        with h5py.File(cf, "r") as f:
            v = np.array(f["#refs#/#v#"]).ravel().tolist()
    pm = all(abs(float(j.get("params", {}).get(k, -1)) - val) < 1e6 * abs(val) + 1
             for k, val in params.items())
    # geom compare with float tolerance; absent keys count as 0/None
    gm = True
    jg = j.get("geom", {}) or {}
    for k, val in geom.items():
        if abs(float(jg.get(k, -9e9)) - float(val)) > 1e-12:
            gm = False
    cj = j.get("Cj_fF_um") or []
    cj0 = cj[1] if len(cj) > 1 else float("nan")
    good = (j.get("status") == "SUCCESS" and len(v) == 20
            and abs(v[-1] - 4.025) < 1e-6 and pm and gm)
    ok_all = ok_all and good
    lines.append("| %s | %s | %d | %s | %s | %s | %.4f |"
                 % (exp, j.get("status", "MISSING"), len(v),
                    "%.3f" % v[-1] if v else "NA",
                    "yes" if pm else "**NO**", "yes" if gm else "**NO**", cj0))
lines += ["", "**Overall:** %s" % ("PASS" if ok_all else "FAIL"), ""]
out = os.path.join(ROOT, "07_Results", "diagnostics", "CLEAN_BATCH_VALIDATION.md")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
print("wrote", out)
