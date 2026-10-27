"""Rebuild experiment_registry.csv from the per-experiment experiment.json files.

The runner appends to the registry; after a re-run of previously failed/contaminated
experiments that leaves stale duplicate rows.  This script replaces the registry with
one row per experiment directory that actually contains an experiment.json.
"""
import os, json, csv

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
FAMS = ["00_Original_Baseline", "02_Doping_Sweeps", "03_Junction_Position",
        "04_Vertical_Doping_Profiles", "05_Combined_Optimization", "06_Final_Validation"]

rows = []
for fam in FAMS:
    d = os.path.join(ROOT, fam)
    if not os.path.isdir(d):
        continue
    for exp in sorted(os.listdir(d)):
        ed = os.path.join(d, exp)
        ej = os.path.join(ed, "experiment.json")
        if not (os.path.isdir(ed) and os.path.exists(ej)):
            continue
        try:
            j = json.load(open(ej, encoding="utf-8"))
        except Exception:
            continue
        cj = j.get("Cj_fF_um") or []
        rows.append(dict(
            exp=exp, family=fam, description=j.get("description", j.get("desc", "")),
            status=j.get("status", ""), runtime_s=j.get("runtime_s", ""),
            n_charge_points=j.get("n_charge_points", ""),
            W_nm=j.get("W_nm", 500), slab_nm=j.get("slab_nm", 90),
            p_wg=j.get("params", {}).get("p_wg", ""),
            n_wg=j.get("params", {}).get("n_wg", ""),
            dx_nm=(j.get("geom", {}) or {}).get("dx", 0) * 1e9 if j.get("geom") else 0,
            Cj_0V_fF_um=(cj[1] if len(cj) > 1 else ""),
            Cj_4V_fF_um=(cj[-1] if cj else ""),
        ))

out = os.path.join(ROOT, "07_Results", "experiment_registry.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["exp"])
    w.writeheader()
    for r in rows:
        w.writerow(r)
print("registry rebuilt:", len(rows), "experiments ->", out)
