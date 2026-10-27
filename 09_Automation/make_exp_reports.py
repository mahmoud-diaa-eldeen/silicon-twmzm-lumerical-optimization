import os, json, glob
ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"

FAMILY_INFO = {
 "D": {
   "question": "How does the channel/slab doping concentration affect optical loss, modulation efficiency and junction capacitance at fixed geometry?",
   "justification": "Free-carrier absorption scales with carrier density (d_alpha = 8.5e-18 dNe + 6.0e-18 dNh, cm^-1) while the junction depletion charge and dNeff also depend on doping. Lower doping reduces the neutral-region absorption but increases series resistance and can reduce dNeff/dV.",
   "objective": "Find the doping level that lowers propagation loss without an unacceptable VpiL increase.",
   "prediction": "Lower doping -> lower loss and lower Cj, but higher VpiL and higher Rs. (hypothesis)"
 },
 "J": {
   "question": "How does the lateral junction position relative to the optical mode maximum affect loss and modulation efficiency?",
   "justification": "dNeff(V) = integral dN(x,z,V)|E|^2 dA. Moving the junction changes the overlap of the depletion region (useful dN) and of the neutral doped regions (loss) with |E|^2.",
   "objective": "Test whether a small junction offset improves the loss/efficiency trade-off.",
   "prediction": "Offset away from the mode peak reduces loss but also reduces dNeff; an optimum may exist near the peak. (hypothesis)"
 },
 "Z": {
   "question": "How does the vertical placement/extent of the waveguide implants affect confinement-weighted loss and modulation?",
   "justification": "The vertical overlap integral weights the doping by |E(x,z)|^2. Confining the implant to a region of lower field reduces absorption at the cost of available depletion charge.",
   "objective": "Screen vertical-placement variants for a better loss/efficiency point.",
   "prediction": "Pushing the implant away from the field maximum lowers loss but weakens modulation. (hypothesis)"
 },
 "C": {
   "question": "Can the individually best geometry and doping choices be combined without violating physical constraints?",
   "justification": "The objective vector is multi-dimensional; the combined candidate tests additivity of the individual improvements.",
   "objective": "Produce a combined candidate for finalist validation.",
   "prediction": "Combined changes should preserve the loss reduction if the mechanisms are independent. (hypothesis)"
 },
}

def fmt(v):
    if isinstance(v, float):
        return "%.4g" % v
    return str(v)

for ed in sorted(glob.glob(os.path.join(ROOT, "0[2-6]_*", "*"))):
    ej = os.path.join(ed, "experiment.json")
    oj = os.path.join(ed, "optical_metrics.json")
    if not os.path.exists(ej):
        continue
    j = json.load(open(ej)); exp = j["exp"]
    info = FAMILY_INFO.get(exp[0], FAMILY_INFO["C"])
    o = json.load(open(oj)) if os.path.exists(oj) else None
    lines = ["# Experiment %s" % exp, "", "## Research question", info["question"], "",
             "## Baseline configuration",
             "- Geometry: rib 500 x 130 nm on 90 nm slab (unless stated).",
             "- Baseline doping: p wg 5e23 /m3 (5e17 cm-3), n wg 7e23 /m3 (7e17 cm-3), p slab 7e23, n slab 5e23, p++/n++ 1e25.",
             "- Baseline metrics: neff(0V)=2.5671, loss(0V)=498.2 dB/m, VpiL=2.90 V.cm, Cj(0V)=0.210 fF/um.",
             "", "## Modified parameters"]
    params = j.get("params", {})
    base = dict(p_wg=5e23, n_wg=7e23, p_imp=7e23, n_imp=5e23)
    lines.append("| Object | Property | Original (/m3) | New (/m3) | Original (/cm3) | New (/cm3) |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for k, obj in [("p_wg","p wg implant"),("n_wg","n wg implant"),("p_imp","p implant"),("n_imp","n implant")]:
        orig = base.get(k); new = params.get(k, orig)
        lines.append("| %s | concentration | %s | %s | %s | %s |" % (obj, fmt(orig), fmt(new), fmt(orig/1e6), fmt(new/1e6)))
    geo = j.get("geom", {})
    if "dx" in geo:
        lines.append("| p/n wg + slab implants | x (junction shift) | - | %+d nm | - | - |" % round(geo["dx"]*1e9))
    if "zmin" in geo:
        lines.append("| p/n wg implants | z range | baseline | %.0f..%.0f nm | - | - |" % (geo["zmin"]*1e9, geo["zmax"]*1e9))
    if "W_nm" in j:
        lines.append("| rib / slab | width / thickness | 500 / 90 nm | %.0f / %.0f nm | - | - |" % (j["W_nm"], j.get("slab_nm",90)))
    lines += ["", "## Mathematical justification", info["justification"], "",
              "## Objective", info["objective"], "",
              "## Predicted outcome (hypothesis)", info["prediction"], "",
              "## Simulation settings",
              "- CHARGE steady-state DC, Fermi statistics, value table V=[-0.5,0,1,2,3,4] V with dv=0.025 V.",
              "- MODE FDE 2D-Y-normal, 1550 nm, 10 trial modes, conformal mesh, 10 nm core override.",
              "- Software: Ansys Lumerical 2024 R1 (v241).", "", "## Actual results"]
    if o:
        r0 = min(o["V"], key=lambda r: abs(r["V"]))
        lines.append("| V (V) | neff | ng | loss (dB/m) | d neff | Gamma_core |")
        lines.append("|---:|---:|---:|---:|---:|---:|")
        for r in o["V"]:
            lines.append("| %.3f | %.6f | %.4f | %.2f | %.3e | %.3f |" % (r["V"], r["neff_re"], r["ng"], r["loss"], r["dneff"], r["Gcore"]))
        lines += ["", "**VpiL = %.3f V.cm**" % o["VpiL_Vcm"],
                  "**Cj(0V) = %.4f fF/um**" % (j.get("Cj_fF_um",[None,float('nan')])[1] if "Cj_fF_um" in j else float('nan'))]
    else:
        lines.append("Optical metrics not available (MODE pass not run or failed).")
    lines += ["", "## Baseline comparison",
              "Computed automatically in 07_Results/all_metrics.csv and best_designs.csv.", "",
              "## Interpretation",
              "Free-carrier absorption in the neutral doped regions competes with the depletion-region index change; see the plots for the measured trend.", "",
              "## Decision",
              ("Promising" if o and r0["loss"] < 498.22 else "Requires further validation") + " — based on measured loss and VpiL.",
              "", "## Files"]
    for fn in ["experiment.json","optical_metrics.json","charge.mat"]:
        if os.path.exists(os.path.join(ed, fn)):
            lines.append("- `%s`" % fn)
    with open(os.path.join(ed, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", exp)
print("DONE")
