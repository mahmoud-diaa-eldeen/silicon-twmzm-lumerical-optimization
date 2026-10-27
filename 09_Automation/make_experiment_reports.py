"""Generate a structured report.md for every experiment from validated JSON/CSV."""
import os, json, glob
import pandas as pd

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
BASE = dict(loss=498.2313, VpiL=2.9080, Cj=0.2100, Gcore=0.35355,
            neff=2.567082, ng=3.936389, Aeff=2.0561e-13, TE=0.9866)

FAM = {
 "B": dict(
  q="Reference run: reproduce the baseline on the validated fine bias grid.",
  why="The earlier baseline charge file started at V=0.4 V and therefore had no true 0 V point; its Cj was mislabelled. This run re-establishes the baseline with the same 0.5 V grid used by the optimization experiments.",
  obj="Provide a like-for-like baseline for every comparison.",
  pred="The 0 V Cj should be slightly higher than the 0.4 V value. (hypothesis)"),
 "D": dict(
  q="How does the channel/slab doping concentration change optical loss, modulation efficiency and junction capacitance at fixed geometry?",
  why="Free-carrier absorption scales with carrier density (Delta alpha = 8.5e-18 dNe + 6.0e-18 dNh cm^-1), while the depletion charge and dNeff/dV also depend on doping. Lower doping lowers neutral-region absorption but raises series resistance and can lower dNeff/dV.",
  obj="Find a doping level that lowers propagation loss without an unacceptable VpiL penalty.",
  pred="Lower doping -> lower loss and lower Cj, but higher VpiL and higher Rs. (hypothesis)"),
 "J": dict(
  q="How does the lateral junction position relative to the optical-mode maximum change loss and modulation efficiency?",
  why="dNeff(V)=integral dN(x,z,V)|E|^2 dA. Shifting the junction changes the overlap of the depletion region (useful index change) and of the neutral doped regions (absorption) with |E|^2.",
  obj="Test both shift directions and look for a loss/efficiency optimum near the mode peak.",
  pred="Moving the junction away from the mode peak lowers loss but also lowers dNeff; a trade-off is expected. (hypothesis)"),
 "Z": dict(
  q="How does the vertical placement/extent of the waveguide implants change confinement-weighted loss and modulation?",
  why="The vertical overlap integral weights doping by |E(x,z)|^2. Restricting an implant to a low-field region reduces absorption, at the cost of available depletion charge.",
  obj="Screen vertical-placement variants for a better loss/efficiency point.",
  pred="Pushing doping away from the field maximum lowers loss but weakens modulation. (hypothesis)"),
 "C": dict(
  q="Do the individually best geometry, doping and junction choices combine without breaking the physical constraints or the performance ranking?",
  why="The objective vector is multi-dimensional; the combined candidate tests additivity and interactions of the individual improvements.",
  obj="Produce a combined candidate for finalist validation.",
  pred="Combined changes should preserve the individual loss reduction if the mechanisms are independent. (hypothesis)"),
}


def fmt(v):
    if isinstance(v, (int, float)):
        return "%.4g" % v
    return str(v)


def read_json(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


for ed in sorted(glob.glob(os.path.join(ROOT, "0[0-6]_*", "*"))):
    if not os.path.isdir(ed):
        continue
    exp = os.path.basename(ed)
    # geometry screening folders have no experiment.json and are summarised in
    # the final report / geometry tables instead of per-experiment reports
    if not os.path.exists(os.path.join(ed, "experiment.json")):
        continue
    j = read_json(os.path.join(ed, "experiment.json"))
    o = read_json(os.path.join(ed, "optical_metrics.json"))
    info = FAM.get(exp[0], FAM["C"])
    status = j.get("status", "NOT RUN")
    lines = ["# Experiment %s" % exp, "", "**Status: %s**" % status, "",
             "## Research question", info["q"], "",
             "## Baseline configuration",
             "- Rib 500 x 130 nm on 90 nm slab (total Si 220 nm), SiO2 cladding.",
             "- Doping: p wg 5e23 /m3 (5e17 cm-3), n wg 7e23 /m3 (7e17 cm-3), "
             "p slab 7e23, n slab 5e23, p++/n++ 1e25 /m3 (1e19 cm-3).",
             "- Baseline metrics: neff %.4f, loss %.1f dB/m, VpiL %.3f V.cm, Cj %.4f fF/um."
             % (BASE["neff"], BASE["loss"], BASE["VpiL"], BASE["Cj"]),
             "", "## Modified parameters"]
    params = j.get("params", {}) or {}
    basep = dict(p_wg=5e23, n_wg=7e23, p_imp=7e23, n_imp=5e23)
    lines += ["| Object | Property | Original | New | Unit (script API) | Region |",
              "|---|---|---:|---:|---|---|"]
    regions = {"p_wg": "rib x -300..+60 nm, z 0..255 nm",
               "n_wg": "rib x -40..+250 nm, z 2.5..237.5 nm",
               "p_imp": "slab x -6..-0.15 um, z -300..90 nm",
               "n_imp": "slab x +0.15..6 um, z -300..90 nm"}
    for k, obj in [("p_wg", "p wg implant"), ("n_wg", "n wg implant"),
                   ("p_imp", "p implant"), ("n_imp", "n implant")]:
        orig = basep[k]; new = params.get(k, orig)
        lines.append("| %s | concentration | %s | %s | /m3 (%s /cm3) | %s |"
                     % (obj, fmt(orig), fmt(new), fmt(new/1e6), regions[k]))
    geo = j.get("geom", {}) or {}
    if geo.get("dx"):
        lines.append("| p/n wg + slab implants | x position | 0 | %+d nm | m (script) | junction shift |"
                     % round(geo["dx"]*1e9))
    for side in ("p", "n"):
        if geo.get("zmin_"+side) is not None:
            lines.append("| %s wg implant | z range | baseline | %.1f..%.1f nm | m (script) | vertical profile |"
                         % (side, geo["zmin_"+side]*1e9, geo["zmax_"+side]*1e9))
    for k in ("W_nm", "slab_nm"):
        if k in j and (j[k] != (500 if k == "W_nm" else 90)):
            lines.append("| rib/slab | %s | baseline | %s nm | geometry | waveguide |" % (k, j[k]))
    lines += ["", "**Unit source:** values written through the Lumerical script API are in /m^3. "
              "The GUI displays the same concentrations in /cm^3 (1e21 /m^3 = 1e15 /cm^3).",
              "", "## Physical rationale", info["why"], "",
              "## Objective", info["obj"], "",
              "## Prediction (hypothesis, not a result)", info["pred"], "",
              "## Simulation settings",
              "- Software: Ansys Lumerical 2024 R1 (v241).",
              "- CHARGE: steady state DC, Newton, Fermi statistics, T=300 K, norm length 10 mm.",
              "- Bias grid: %s V principal, each +%.3f V." %
              (j.get("bias_grid_V", "[-0.5..4]"), j.get("dv_V", 0.025)),
              "- MODE: FDE 2D Y-normal, 1550 nm, 10 trial modes, conformal mesh, 12 PML, 10 nm core override.",
              "- Requested CHARGE points: %s; completed: %s." %
              (j.get("requested_points", "12"), j.get("n_charge_points", "NA")),
              "", "## Convergence evidence",
              "- The sweep is accepted only if all requested points are saved and the final bias is 4.025 V.",
              "- This experiment: **%s** (%s points)." %
              (status, j.get("n_charge_points", "NA")),
              "- Detailed incident analysis: `07_Results/diagnostics/CHARGE_DIAGNOSTIC.md`.",
              "", "## Raw result files"]
    for fn in ("charge.mat", "cj_derived.csv", "optical_metrics.json"):
        if os.path.exists(os.path.join(ed, fn)):
            lines.append("- `%s` (%d bytes)" % (fn, os.path.getsize(os.path.join(ed, fn))))
    lines += ["", "## Equations used",
              "- VpiL = lambda/(2|d(dNeff)/dV|), slope over 0->4 V.",
              "- Cj = 0.5(|dQn|+|dQp|)/dV, dV = 0.025 V; F/m converted to fF/um by x1e9.",
              "- Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening overlap).",
              "", "## Actual results"]
    if o and o.get("V"):
        r0 = min(o["V"], key=lambda r: abs(r["V"]))
        r4 = max(o["V"], key=lambda r: r["V"])
        lines += ["| Metric | Value |", "|---|---:|",
                  "| neff (0 V) | %.6f |" % r0["neff_re"],
                  "| ng (0 V) | %.4f |" % r0["ng"],
                  "| loss (0 V) | %.2f dB/m |" % r0["loss"],
                  "| loss (4 V) | %.2f dB/m |" % r4["loss"],
                  "| d neff (0->4 V) | %.3e |" % r4["dneff"],
                  "| VpiL | %.3f V.cm |" % o.get("VpiL_Vcm", float("nan")),
                  "| Gamma_core (0 V) | %.3f |" % r0["Gcore"],
                  "| Gamma_slab (0 V) | %.3f |" % r0["Gslab"],
                  "| Aeff (0 V) | %.3e m^2 |" % r0["Aeff"],
                  "| TE fraction | %.4f |" % r0["TE"]]
        cj = j.get("Cj_fF_um") or []
        if cj:
            lines += ["| Cj (0 V) | %.4f fF/um |" % cj[1],
                      "| Cj (4 V) | %.4f fF/um |" % cj[-1]]
        lines += ["", "### Bias dependence", "",
                  "| V (V) | neff | loss (dB/m) | d neff | Gamma_core |", "|---:|---:|---:|---:|---:|"]
        for r in o["V"]:
            lines.append("| %.3f | %.6f | %.2f | %.3e | %.3f |"
                         % (r["V"], r["neff_re"], r["loss"], r["dneff"], r["Gcore"]))
        lines += ["", "## Difference from baseline",
                  "| Metric | Baseline | This experiment | Change |", "|---|---:|---:|---:|",
                  "| loss (0 V) | %.2f dB/m | %.2f dB/m | %+.1f %% |"
                  % (BASE["loss"], r0["loss"], 100*(r0["loss"]-BASE["loss"])/BASE["loss"]),
                  "| VpiL | %.2f V.cm | %.3f V.cm | %+.1f %% |"
                  % (BASE["VpiL"], o.get("VpiL_Vcm", float("nan")),
                     100*(o.get("VpiL_Vcm", float("nan"))-BASE["VpiL"])/BASE["VpiL"]),
                  "| Gamma_core | %.3f | %.3f | %+.1f %% |"
                  % (BASE["Gcore"], r0["Gcore"], 100*(r0["Gcore"]-BASE["Gcore"])/BASE["Gcore"])]
        if cj:
            lines.append("| Cj (0 V) | %.4f fF/um | %.4f fF/um | %+.1f %% |"
                         % (BASE["Cj"], cj[1], 100*(cj[1]-BASE["Cj"])/BASE["Cj"]))
    else:
        lines.append("Optical metrics unavailable (MODE pass not completed for this experiment).")
    lines += ["", "## Trade-offs and Pareto impact",
              "See `07_Results/pareto_front.csv` and `07_Results/best_designs.csv`; "
              "this experiment is included in the multi-objective comparison when all of "
              "loss, VpiL, Cj and Gamma_core are available.",
              "", "## Decision"]
    if status != "SUCCESS":
        dec = "RETEST / INCOMPLETE — raw results do not cover the full requested bias grid."
    elif not o:
        dec = "RETEST — MODE extraction missing."
    else:
        r0 = min(o["V"], key=lambda r: abs(r["V"]))
        better_loss = r0["loss"] < BASE["loss"]
        better_vpil = o.get("VpiL_Vcm", 9e9) < BASE["VpiL"]
        if better_loss and better_vpil:
            dec = "KEEP — improves both loss and VpiL vs baseline."
        elif better_loss:
            dec = ("TRADE-OFF — lower loss but higher VpiL; keep only as a Pareto "
                   "alternative, not as the balanced finalist.")
        elif better_vpil:
            dec = ("TRADE-OFF — lower VpiL but higher loss; keep only as a Pareto "
                   "alternative, not as the balanced finalist.")
        else:
            dec = ("REJECT on loss+VpiL; it can still appear on the multi-objective "
                   "Pareto front through Cj or Gamma_core.")
    lines += [dec, "", "## Limitations / reproduction",
              "- Gamma_core is a field-overlap screening metric on the FDE output grid, not the exact energy confinement factor.",
              "- Cj is a per-unit-length small-signal value at dv = 0.025 V; it is not the total device capacitance.",
              "- Reproduce with `09_Automation/run_experiment.py %s` then `09_Automation/extract_metrics.py`." % exp,
              ""]
    with open(os.path.join(ed, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", exp)
print("REPORTS DONE")
