"""Validate every experiment's raw results and write convergence_summary.csv."""
import os, json, glob, csv
import numpy as np
import h5py

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
FAMS = ["00_Original_Baseline", "01_Geometry_Sweeps", "02_Doping_Sweeps",
        "03_Junction_Position", "04_Vertical_Doping_Profiles",
        "05_Combined_Optimization", "06_Final_Validation"]


def meta(p):
    try:
        with h5py.File(p, "r") as f:
            v = np.array(f["#refs#/#v#"]).ravel() if "#refs#" in f and "#v#" in f["#refs#"] else []
            n = 0
            if "#refs#" in f:
                for k in ("#y#", "#z#"):
                    if k in f["#refs#"]:
                        n = int(f["#refs#"][k].shape[0])
                        break
            return len(v), v, n
    except Exception as e:
        return 0, [], 0


rows = []
for fam in FAMS:
    for ed in sorted(glob.glob(os.path.join(ROOT, fam, "*"))):
        if not os.path.isdir(ed):
            continue
        exp = os.path.basename(ed)
        cf = os.path.join(ed, "charge.mat")
        ej = os.path.join(ed, "experiment.json")
        oj = os.path.join(ed, "optical_metrics.json")
        j = {}
        if os.path.exists(ej):
            try: j = json.load(open(ej, encoding="utf-8"))
            except Exception: pass
        if os.path.exists(cf):
            nv, v, nmap = meta(cf)
            lastV = float(v[-1]) if nv else float("nan")
            complete = nv >= 12 and abs(lastV - 4.025) < 1e-6
            status = j.get("status", "UNKNOWN")
            if complete and status not in ("SUCCESS",):
                status = "SUCCESS (raw complete)"
            if not complete:
                status = "INCOMPLETE"
        elif fam == "01_Geometry_Sweeps" and os.path.exists(os.path.join(ed, "metrics.json")):
            nv, lastV, complete, status = 0, float("nan"), True, "SUCCESS (MODE-only, baseline charge)"
        else:
            nv, lastV, complete, status = 0, float("nan"), False, j.get("status", "NOT RUN")
        rows.append(dict(
            exp=exp, family=fam, status=status,
            charge_points=nv, last_V=lastV, charge_complete=complete,
            has_Cj=bool(j.get("Cj_fF_um")), n_Cj=j.get("n_Cj", ""),
            Cj_0V=(j.get("Cj_fF_um") or [None, None])[1] if j.get("Cj_fF_um") else "",
            has_optical=(os.path.exists(oj) or os.path.exists(os.path.join(ed, "metrics.json"))),
            runtime_s=j.get("runtime_s", ""), charge_size=j.get("charge_size", ""),
            error=j.get("error", "")))

out = os.path.join(ROOT, "07_Results", "convergence_summary.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                       ["exp","family","status","charge_points","last_V","charge_complete",
                        "has_Cj","n_Cj","Cj_0V","has_optical","runtime_s","charge_size","error"])
    w.writeheader()
    for r in rows: w.writerow(r)
for r in rows:
    print("%-6s %-28s %-22s pts=%2d lastV=%7.3f Cj0=%s opt=%s"
          % (r["exp"], r["family"], r["status"], r["charge_points"], r["last_V"],
             ("%.4f" % r["Cj_0V"]) if isinstance(r["Cj_0V"], (int, float)) else "-",
             r["has_optical"]))
print("wrote", out)
