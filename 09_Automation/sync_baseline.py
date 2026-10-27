"""Propagate the validated B000 (same-mesh) baseline into every analysis script.

Run after `extract_metrics.py` has produced
00_Original_Baseline/B000/optical_metrics.json.  It rewrites the BASE = dict(...)
literal in the report/analysis scripts so all comparisons use one baseline.
"""
import os, re, json, csv

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
B = os.path.join(ROOT, "00_Original_Baseline", "B000")

om = json.load(open(os.path.join(B, "optical_metrics.json"), encoding="utf-8"))
ej = json.load(open(os.path.join(B, "experiment.json"), encoding="utf-8"))
r0 = min(om["V"], key=lambda r: abs(r["V"]))
r4 = min(om["V"], key=lambda r: abs(r["V"] - 4.0))
vals = dict(
    loss=r0["loss"], VpiL=om["VpiL_Vcm"], Cj=ej["Cj_fF_um"][1],
    Gcore=r0["Gcore"], neff=r0["neff_re"], ng=r0["ng"],
    Aeff=r0["Aeff"], TE=r0["TE"],
)
print("B000 baseline:", {k: round(v, 6) if isinstance(v, float) else v for k, v in vals.items()})

scripts = ["make_experiment_reports.py", "make_final_reports.py",
           "plot_results.py", "optimize_design.py", "suggest_combined.py"]
pat = re.compile(r"BASE\s*=\s*dict\([^)]*\)", re.S)
new = ("BASE = dict(loss=%(loss).4f, VpiL=%(VpiL).4f, Cj=%(Cj).4f, "
       "Gcore=%(Gcore).5f,\n            neff=%(neff).6f, ng=%(ng).6f, "
       "Aeff=%(Aeff).4e, TE=%(TE).4f)" % vals)
for s in scripts:
    p = os.path.join(ROOT, "09_Automation", s)
    txt = open(p, encoding="utf-8").read()
    if not pat.search(txt):
        print("WARN no BASE literal in", s)
        continue
    txt2 = pat.sub(new, txt, count=1)
    if txt2 != txt:
        open(p, "w", encoding="utf-8").write(txt2)
        print("updated", s)

with open(os.path.join(ROOT, "00_Original_Baseline", "baseline_metrics_b000.csv"), "w",
          newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["metric", "value", "unit", "note"])
    w.writerow(["neff_0V", "%.6f" % vals["neff"], "dimensionless", "B000 re-run, same mesh"])
    w.writerow(["ng_0V", "%.6f" % vals["ng"], "dimensionless", "B000 re-run"])
    w.writerow(["loss_0V", "%.2f" % vals["loss"], "dB/m", "B000 0 V (index 3); recorded baseline 498.22"])
    w.writerow(["VpiL", "%.3f" % vals["VpiL"], "V.cm", "0->4 V slope, 1.55 um"])
    w.writerow(["Cj_0V", "%.4f" % vals["Cj"], "fF/um", "dQ/dV at 0 V"])
    w.writerow(["Gamma_core", "%.4f" % vals["Gcore"], "dimensionless", "|E|^2 overlap"])
    w.writerow(["Aeff", "%.4e" % vals["Aeff"], "m^2", "MODE native"])
    w.writerow(["TE_fraction", "%.4f" % vals["TE"], "dimensionless", "MODE native"])
print("wrote baseline_metrics_b000.csv")
