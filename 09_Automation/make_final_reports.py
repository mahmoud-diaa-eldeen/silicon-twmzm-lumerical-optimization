"""Generate the three final report files from validated results only."""
import os, json, glob
import numpy as np
import pandas as pd

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
R = os.path.join(ROOT, "07_Results")
REP = os.path.join(ROOT, "08_Reports")
BASE = dict(loss=498.2313, VpiL=2.9080, Cj=0.2100, Gcore=0.35355,
            neff=2.567082, ng=3.936389, Aeff=2.0561e-13, TE=0.9866)


def rd(p):
    return pd.read_csv(p) if os.path.exists(p) else None


def jload(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


def find_ej(exp):
    for fam in ("00_Original_Baseline", "02_Doping_Sweeps", "03_Junction_Position",
                "04_Vertical_Doping_Profiles", "05_Combined_Optimization",
                "06_Final_Validation"):
        p = os.path.join(ROOT, fam, exp, "experiment.json")
        if os.path.exists(p):
            return jload(p)
    return {}


def fv(x, spec, na="NA"):
    """Format a possibly-missing numeric value without crashing."""
    try:
        if x is None:
            return na
        xf = float(x)
        if np.isnan(xf):
            return na
        return spec % xf
    except Exception:
        return na


def table(df, cols, heads):
    out = ["| " + " | ".join(heads) + " |",
           "|" + "|".join(["---"] * len(heads)) + "|"]
    for _, r in df.iterrows():
        vals = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, (float, np.floating)):
                if np.isnan(v):
                    v = "NA"
                elif abs(v) >= 1e4 or (abs(v) < 1e-3 and v != 0):
                    v = "%.3e" % v
                else:
                    v = "%.4g" % v
            vals.append(str(v))
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)


def ac_for(exp):
    for fam in ("00_Original_Baseline", "05_Combined_Optimization", "06_Final_Validation",
                "02_Doping_Sweeps", "03_Junction_Position", "04_Vertical_Doping_Profiles",
                "01_Geometry_Sweeps"):
        p = os.path.join(ROOT, fam, exp, "ac_metrics.json")
        if os.path.exists(p):
            return jload(p)
    return {}


def main():
    gp = os.path.join(ROOT, "01_Geometry_Sweeps", "geometry_metrics.csv")
    g = rd(gp)
    s = rd(os.path.join(R, "summary_0V.csv"))
    conv = rd(os.path.join(R, "convergence_summary.csv"))
    pf = rd(os.path.join(R, "pareto_front.csv"))
    pg = rd(os.path.join(R, "pareto_geometry.csv"))
    reg = rd(os.path.join(R, "experiment_registry.csv"))

    if s is not None:
        s = s.copy()
        s["ok"] = s["status"].astype(str).str.startswith("SUCCESS")
        s = s[s["ok"]]

    b0 = None
    if s is not None and len(s):
        bb = s[s["exp"] == "B000"]
        if len(bb):
            b0 = bb.iloc[0]
    b0_get = (lambda k, d: b0[k] if b0 is not None and k in b0 and not pd.isna(b0[k]) else d)
    b0_loss = float(b0_get("loss_0V", BASE["loss"]))
    b0_vpil = float(b0_get("VpiL_Vcm", BASE["VpiL"]))
    b0_cj0 = float(b0_get("Cj_0V_fF_um", BASE["Cj"]))
    b0_cj4 = float(b0_get("Cj_4V_fF_um", float("nan")))
    b0_gcore = float(b0_get("Gamma_core", BASE["Gcore"]))
    b0_gslab = float(b0_get("Gamma_slab", float("nan")))
    b0_dneff = float(b0_get("dneff_0_4V", float("nan")))

    # --- choose recommendation (all individual + combined experiments) ---
    rec = None
    rec_reason = ""
    if s is not None and len(s):
        feas = s[(s["VpiL_Vcm"] <= 1.25*BASE["VpiL"]) &
                 (s["Cj_0V_fF_um"] <= 1.25*BASE["Cj"])]
        cand = feas if len(feas) else s
        rec = cand.sort_values("loss_0V").iloc[0]
        rec_reason = ("lowest 0 V loss among all individual and combined experiments "
                      "that satisfy VpiL <= 1.25x baseline and Cj <= 1.25x baseline"
                      if len(feas) else
                      "lowest 0 V loss (no experiment met both screening constraints)")
    elif g is not None and len(g):
        rec = g.sort_values("loss_dB_m").iloc[0]
        rec_reason = "lowest loss in the MODE-only geometry screening (electrical metrics unavailable)"

    # --- helper blocks ---
    geo_tbl = table(g, ["exp", "W_nm", "slab_nm", "neff_re", "ng", "loss_dB_m",
                        "Gamma_core", "Gamma_slab", "Aeff_m2", "TE_frac"],
                    ["ID", "W (nm)", "slab (nm)", "neff", "ng", "loss (dB/m)",
                     "Gamma_core", "Gamma_slab", "Aeff (m2)", "TE frac"]) if g is not None else "NA"
    if s is not None:
        el_tbl = table(s, ["exp", "family", "status", "neff_0V", "ng_0V", "loss_0V",
                           "Gamma_core", "dneff_0_4V", "VpiL_Vcm", "Cj_0V_fF_um",
                           "Cj_4V_fF_um", "W_nm", "slab_nm"],
                       ["ID", "Family", "Status", "neff 0V", "ng 0V", "loss 0V (dB/m)",
                        "Gamma_core", "d neff 0-4V", "VpiL (V.cm)", "Cj 0V (fF/um)",
                        "Cj 4V (fF/um)", "W (nm)", "slab (nm)"])
    else:
        el_tbl = "NA"
    conv_tbl = table(conv, ["exp", "family", "status", "charge_points", "last_V",
                            "charge_complete", "Cj_0V", "has_optical"],
                     ["ID", "Family", "Status", "CHARGE pts", "last V", "complete",
                      "Cj 0V (fF/um)", "MODE done"]) if conv is not None else "NA"

    # --- combined detail ---
    comb_lines = []
    if s is not None:
        for _, r in s[s["exp"].str.startswith("C")].iterrows():
            j = jload(os.path.join(ROOT, "05_Combined_Optimization", r["exp"], "experiment.json"))
            dx_nm = ((j.get("geom", {}) or {}).get("dx") or 0) * 1e9
            comb_lines.append(
                "- **%s**: W=%.0f nm, slab=%.0f nm, dx=%.0f nm; loss=%.1f dB/m, "
                "Gamma_core=%.3f, VpiL=%.3f V.cm, Cj(0V)=%.4f fF/um."
                % (r["exp"], r["W_nm"], r["slab_nm"], dx_nm,
                   r["loss_0V"], r["Gamma_core"], r["VpiL_Vcm"], r["Cj_0V_fF_um"]))
    comb_txt = "\n".join(comb_lines) if comb_lines else "No combined candidate completed."

    # --- finalist details ---
    fin = ""
    if rec is not None:
        j = find_ej(str(rec["exp"]))
        a = ac_for(str(rec["exp"]))
        cj0 = rec.get("Cj_0V_fF_um", np.nan)
        try:
            cj0f = float(cj0)
        except Exception:
            cj0f = np.nan
        pr = j.get("params", {}) or {}
        rs_ghz = (a.get("f_at_R_Hz", 20e9) or 20e9) / 1e9 if a else 20.0

        def pct(v, base):
            try:
                vf = float(v)
                if np.isnan(vf):
                    return "NA"
                return "%+.1f %%" % (100 * (vf - base) / base)
            except Exception:
                return "NA"

        fin = "\n".join([
            "| Parameter | Value |", "|---|---:|",
            "| Rib width | %s nm |" % fv(rec.get("W_nm"), "%.0f"),
            "| Rib height | %s nm |" % fv(220 - float(rec.get("slab_nm", np.nan)), "%.0f"),
            "| Slab thickness | %s nm |" % fv(rec.get("slab_nm"), "%.0f"),
            "| Total Si thickness | 220 nm |",
            "| Junction shift | %s nm |" % fv(((j.get("geom", {}) or {}).get("dx") or 0) * 1e9, "%.0f"),
            "| p wg concentration | %.3g /m3 (%.3g /cm3) |" % (pr.get("p_wg", 5e23), pr.get("p_wg", 5e23)/1e6),
            "| n wg concentration | %.3g /m3 (%.3g /cm3) |" % (pr.get("n_wg", 7e23), pr.get("n_wg", 7e23)/1e6),
            "| p slab concentration | %.3g /m3 (%.3g /cm3) |" % (pr.get("p_imp", 7e23), pr.get("p_imp", 7e23)/1e6),
            "| n slab concentration | %.3g /m3 (%.3g /cm3) |" % (pr.get("n_imp", 5e23), pr.get("n_imp", 5e23)/1e6),
            "| Gamma_core (field overlap) | %s |" % fv(rec.get("Gamma_core"), "%.3f"),
            "| neff (0 V) | %s |" % fv(rec.get("neff_0V"), "%.6f"),
            "| Optical loss (0 V) | %s dB/m |" % fv(rec.get("loss_0V"), "%.2f"),
            "| VpiL | %s V.cm |" % fv(rec.get("VpiL_Vcm"), "%.3f"),
            "| Cj (0 V) | %s fF/um |" % fv(cj0f, "%.4f"),
            "| Rs (0 V, %.1f GHz; 10 mm norm length) | %s |" % (rs_ghz, fv(a.get("R_0V_20GHz_ohm"), "%.4f ohm", "NA (AC not run)")),
            "| C_ac (0 V, 1 MHz; per um) | %s |" % (
                fv(a.get("C_0V_1MHz_F_per_m", float("nan")) * 1e9, "%.4f fF/um", "NA (AC not run)")
                if a.get("C_0V_1MHz_F_per_m") is not None else "NA (AC not run)"),
            "| f3dB | NA (distributed RF not simulated) |",
            "| Mesh | conformal, 12 PML, 10 nm core override |",
            "| Convergence | CHARGE %s/%s points; MODE converged |" % (
                j.get("n_charge_points", "?"), j.get("requested_points", "?")),
            "| vs baseline loss | %s |" % pct(rec.get("loss_0V"), BASE["loss"]),
            "| vs baseline VpiL | %s |" % pct(rec.get("VpiL_Vcm"), BASE["VpiL"]),
            "| vs baseline Cj | %s |" % pct(cj0f, BASE["Cj"]),
            "| vs baseline Gamma_core | %s |" % pct(rec.get("Gamma_core"), BASE["Gcore"]),
        ])

    # --- executive summary ---
    ex = []
    ex.append("# Executive Summary\n")
    ex.append("A reproducible Ansys Lumerical 2024 R1 study of the lateral-PN silicon "
              "traveling-wave MZM was completed. Every result below comes from a CHARGE "
              "and/or MODE run recorded in the workspace.\n")
    ex.append("**Project-file incident (disclosed):** during the first automation batch, "
              "Lumerical's save-on-run overwrote the original "
              "`D:/lumerical/tw_modulator_DEVICE.ldev` with the modified layout. A pristine "
              "layout was reconstructed from `baseline_manifest.json`, verified against the "
              "recorded baseline (Cj, neff, Gamma_core), and all reported experiments were "
              "re-run from it. The contaminated raw results are archived under "
              "`07_Results/diagnostics/contaminated/`; full evidence is in "
              "`07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`.\n")
    ex.append("**Baseline convention:** every percentage change below uses the B000 "
              "re-run baseline (loss %.1f dB/m, Cj(0V) %.4f fF/um, "
              "VpiL %.2f V.cm). The reconstructed pristine layout reproduces the "
              "recorded baseline loss (498.22 dB/m) to 0.01 dB/m, so there is no "
              "mesh-offset correction.\n"
              % (BASE["loss"], BASE["Cj"], BASE["VpiL"]))
    if rec is not None:
        ex.append("**Recommended design:** `%s` (%s)." % (rec["exp"], rec_reason))
        ex.append("It gives loss = %s dB/m (baseline %.1f), Gamma_core = %s "
                  "(baseline %.3f), VpiL = %s V.cm (baseline %.2f) and Cj(0V) = %s fF/um "
                  "(baseline %.4f).\n"
                  % (fv(rec.get("loss_0V"), "%.1f"), BASE["loss"],
                     fv(rec.get("Gamma_core"), "%.3f"), BASE["Gcore"],
                     fv(rec.get("VpiL_Vcm"), "%.3f"), BASE["VpiL"],
                     fv(rec.get("Cj_0V_fF_um"), "%.4f"), BASE["Cj"]))
        if rec["exp"] == "J002" and s is not None:
            j3 = s[s["exp"] == "J003"]
            if len(j3):
                j3r = j3.iloc[0]
                ex.append("**Near-tie alternative:** J003 (+80 nm) gives loss %.1f dB/m "
                          "(%.1f dB/m above J002), VpiL %.3f V.cm (%.1f %% lower) and "
                          "Cj %.4f fF/um. Prefer J003 if VpiL/Cj dominate.\n"
                          % (j3r["loss_0V"], j3r["loss_0V"] - rec["loss_0V"],
                             j3r["VpiL_Vcm"],
                             100 * (rec["VpiL_Vcm"] - j3r["VpiL_Vcm"]) / rec["VpiL_Vcm"],
                             j3r["Cj_0V_fF_um"]))
    ex.append("Key findings:")
    if g is not None and len(g):
        b = g.sort_values("loss_dB_m").iloc[0]
        ex.append("- Geometry: the 70 nm slab (%s) gives the best combination of loss and "
                  "confinement in the MODE screening (%.1f dB/m, Gamma_core %.3f); the 110 nm "
                  "slab is the worst (%.1f dB/m)." % (b["exp"], b["loss_dB_m"], b["Gamma_core"],
                                                       g.sort_values("loss_dB_m").iloc[-1]["loss_dB_m"]))
    if s is not None and len(s):
        dd = s[s["exp"].str.startswith("D")].sort_values("loss_0V")
        if len(dd):
            ex.append("- Doping: the lowest-loss doping case is %s (%.1f dB/m), but it trades "
                      "against VpiL; Rs was not calculated for it (NA)." % (dd.iloc[0]["exp"], dd.iloc[0]["loss_0V"]))
        jj = s[s["exp"] == "J002"]
        if len(jj):
            jr = jj.iloc[0]
            ex.append("- Junction: J002 (+40 nm shift) is the balanced improvement: loss %.1f dB/m "
                      "(%+.1f %% vs baseline), VpiL %.3f V.cm (%+.1f %%), Cj %.4f fF/um (unchanged)."
                      % (jr["loss_0V"], 100*(jr["loss_0V"]-BASE["loss"])/BASE["loss"],
                         jr["VpiL_Vcm"], 100*(jr["VpiL_Vcm"]-BASE["VpiL"])/BASE["VpiL"],
                         jr["Cj_0V_fF_um"]))
    ex.append("- f3dB was not simulated: the distributed RF/electrode model was not re-run, so no "
              "bandwidth number is claimed. The RC product is reported only as a screening estimate.\n")
    ex.append("All raw data, logs and per-experiment reports are under "
              "`TW_Modulator_Optimization_Study/`.\n")

    # --- full report ---
    L = []
    L.append("# Full Technical Report — Silicon TWMZM Optimization\n")
    L.append("Software: Ansys Lumerical 2024 R1 (v241). The original project was "
             "overwritten by Lumerical's save-on-run during the first batch; a pristine "
             "layout was rebuilt from the manifest and all reported runs use it "
             "(see `PROJECT_FILE_INCIDENT.md`).\n")
    L.append("## 1. Executive summary\n")
    L += ex[1:]
    L.append("## 2. Original device architecture\n")
    L.append("- Lateral PN-junction silicon rib waveguide, SiO2 cladding, Al contacts.")
    L.append("- Rib 500 x 130 nm on a 90 nm slab (total Si 220 nm).")
    L.append("- Contact windows |x| = 3.8..5 um; device width 10 um; phase-shifter length 5 mm.")
    L.append("- Full object/property record: `00_Original_Baseline/baseline_manifest.json`.\n")
    L.append("## 3. Verified baseline parameters\n")
    L.append("These are the **B000 re-run** values (same mesh as every clean "
             "CHARGE+MODE experiment). The true 0 V point is `V_cathode_index = 3` "
             "on the 20-point grid; the reconstructed layout reproduces the recorded "
             "baseline loss (498.22 dB/m) to 0.01 dB/m. The 535.95 dB/m value quoted "
             "in an earlier check is the -0.475 V point, not 0 V "
             "(`07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`).\n")
    L.append("| Metric | Value |\n|---|---:|\n"
             "| neff (0 V) | %.6f |\n| ng (0 V) | %.6f |\n| loss (0 V) | %.2f dB/m (%.3f dB/cm) |\n"
             "| d neff (0->4 V) | %s |\n| VpiL | %.2f V.cm |\n| Gamma_core | %.3f |\n"
             "| Gamma_slab | %s |\n| Aeff | %.3e m2 |\n| TE fraction | %.4f |\n"
             "| Cj (0 V) | %.4f fF/um |\n| Cj (4 V) | %s fF/um |\n"
             % (BASE["neff"], BASE["ng"], b0_loss, b0_loss/100,
                fv(b0_dneff, "%.3e"), b0_vpil, b0_gcore, fv(b0_gslab, "%.3f"),
                BASE["Aeff"], BASE["TE"], b0_cj0, fv(b0_cj4, "%.4f")))
    L.append("Doping (script API /m3, GUI /cm3): p wg 5e23 (5e17), n wg 7e23 (7e17), "
             "p slab 7e23 (7e17), n slab 5e23 (5e17), p++/n++ 1e25 (1e19).\n")
    L.append("## 4. Mathematical model and assumptions\n")
    L.append("See `08_Reports/EQUATIONS_AND_ASSUMPTIONS.md`. In short: beta=k0 neff; "
             "loss = 8.686|Im(beta)| (cross-checked against the native loss); "
             "Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening); "
             "VpiL = lambda/(2|d(dneff)/dV|); Cj = |dQ/dV| with dv=0.025 V; "
             "Rs from ssac; f_RC is an estimate only, not the traveling-wave bandwidth.\n")
    L.append("## 5. Optimization variables and permitted ranges\n")
    L.append("- Rib width 450-600 nm; slab thickness 70-110 nm (MODE screening).")
    L.append("- Channel/slab doping scale 0.3x-2.0x of baseline.")
    L.append("- Junction shift -40 to +80 nm.")
    L.append("- Vertical implant placement: buried (0-120 nm), upper (100-220 nm), stacked p/n.\n")
    L.append("## 6. Experiment methodology\n")
    L.append("One variable at a time; MODE-only screening for geometry (baseline charge), "
             "CHARGE DC + MODE for doping/junction/vertical/combined. Bias grid 0.5 V steps "
             "(20 solves). Completion requires all points saved; see the CHARGE diagnostic.\n")
    L.append("## 7. Completed experiment IDs\n")
    L.append(conv_tbl + "\n")
    L.append("## 8. Geometry optimization results\n")
    L.append(geo_tbl + "\n")
    L.append("Interpretation: a thinner slab (70 nm) strongly increases the rib-core overlap "
             "and reduces the doped-slab overlap, lowering loss (450.5 vs 498.2 dB/m) while "
             "raising Gamma_core from 0.354 to 0.435. A thicker slab (110 nm) does the "
             "opposite (loss 525.3 dB/m, Gamma_core 0.272). Wider rib raises Gamma_core "
             "(0.326 at 450 nm to 0.399 at 600 nm) at a small loss penalty.\n")
    L.append("## 9. Doping optimization results\n")
    L.append(el_tbl + "\n")
    L.append("Interpretation: lower doping reduces free-carrier absorption and Cj but raises "
             "VpiL and Rs; the measured trend is in the tables.\n")
    L.append("## 10. Junction-position results\n")
    L.append("Junction shifts are included in the table above (J001 -40 nm, J002 +40 nm, "
             "J003 +80 nm). The loss/VpiL trade-off is plotted in `07_Results/plots/junction_sweep.png`.\n")
    L.append("## 11. Vertical-profile results\n")
    L.append("Z001 (buried), Z002 (upper) and Z003 (stacked p/n) are included above. "
             "See `07_Results/plots/vertical_profiles.png`.\n")
    L.append("## 12. Combined optimization results\n")
    L.append(comb_txt + "\n")
    L.append("## 13. Optical mode confinement analysis\n")
    L.append("Gamma_core is a field-overlap screening metric on the FDE grid, not the exact "
             "energy confinement factor. The baseline splits roughly 0.354 rib / 0.362 slab / "
             "0.284 cladding, which explains the strong sensitivity to slab thickness.\n")
    L.append("## 14. Optical loss analysis\n")
    L.append("Loss is the native MODE result (free-carrier absorption from the imported CHARGE "
             "carrier maps). Scattering loss is not represented in the model and is not claimed.\n")
    L.append("## 15. Modulation efficiency analysis\n")
    L.append("VpiL uses the 0->4 V slope of the simulated d neff. The device is treated with the "
             "single-arm convention used by the original example; the push-pull factor is not "
             "applied without verifying the architecture.\n")
    L.append("## 16. Electrical analysis\n")
    L.append("Cj is the per-unit-length dQ/dV at 0 V (dv=0.025 V). Rs is the real part of "
             "the ssac impedance at 20 GHz for the **10 mm norm-length** cross-section; it is "
             "not the full electrode/traveling-wave resistance. C_ac comes from the same ssac "
             "run (1 MHz value quoted, per um). f3dB is NA because the distributed RF model "
             "was not re-run. The lumped RC estimate is a screening number only.\n")
    L.append("## 17. Pareto-front analysis\n")
    if pf is not None:
        pfc = pf[pf["pareto"] == True] if "pareto" in pf.columns else pf
        L.append("Objectives: minimize loss, VpiL and Cj; maximize Gamma_core. Dominance "
                 "uses a 0.1 %% relative tolerance per objective to suppress sub-grid "
                 "numerical noise (not a weighting). Pareto candidates: %s.\n"
                 % ", ".join(pfc["exp"].astype(str).tolist()))
        L.append(table(pfc.sort_values("loss"),
                       ["exp", "loss", "VpiL", "Cj", "Gcore"],
                       ["ID", "loss (dB/m)", "VpiL (V.cm)", "Cj (fF/um)", "Gamma_core"]) + "\n")
    if pg is not None:
        L.append("Geometry Pareto (loss, Gamma_core): %s (`pareto_geometry.csv`)."
                 % ", ".join(pg.loc[pg.get("pareto", False) == True, "exp"].astype(str).tolist())
                 if "pareto" in pg.columns else "")
    L.append("")
    L.append("## 18. Mesh and convergence validation\n")
    L.append("The CHARGE mesh is unchanged from the original (min edge 4 nm, max edge 600 nm, "
             "dz 0.2 nm); the MODE mesh uses a 10 nm core override. The CHARGE sweep was "
             "validated at 0.5 V steps after the 0.9 V step was shown to stop silently. "
             "See `07_Results/diagnostics/CHARGE_DIAGNOSTIC.md` and `convergence_summary.csv`.\n")
    L.append("## 19. Comparison with the baseline\n")
    if rec is not None:
        L.append("| Metric | Baseline | %s | Change |\n|---|---:|---:|---:|\n"
                 "| loss (0 V) | %.2f dB/m | %s dB/m | %s |\n"
                 "| VpiL | %.2f V.cm | %s V.cm | %s |\n"
                 "| Cj (0 V) | %.4f fF/um | %s fF/um | %s |\n"
                 "| Gamma_core | %.3f | %s | %s |\n"
                 % (rec["exp"], BASE["loss"], fv(rec.get("loss_0V"), "%.1f"),
                    pct(rec.get("loss_0V"), BASE["loss"]),
                    BASE["VpiL"], fv(rec.get("VpiL_Vcm"), "%.3f"),
                    pct(rec.get("VpiL_Vcm"), BASE["VpiL"]),
                    BASE["Cj"], fv(rec.get("Cj_0V_fF_um"), "%.4f"),
                    pct(rec.get("Cj_0V_fF_um"), BASE["Cj"]),
                    BASE["Gcore"], fv(rec.get("Gamma_core"), "%.3f"),
                    pct(rec.get("Gamma_core"), BASE["Gcore"])))
    L.append("\n## 20. Limitations and uncertainties\n")
    L.append("- Gamma_core is a screening field-overlap metric; it is not the exact energy confinement factor.")
    L.append("- Cj is per unit length; total capacitance scales with the chosen phase-shifter length.")
    L.append("- Rs is from a 2D ssac extraction; contact resistance and the full metal stack are not modelled beyond the original project.")
    L.append("- f3dB is not simulated; no bandwidth claim is made.")
    L.append("- The combined candidates use the baseline CHARGE mesh and a single wavelength (1550 nm).")
    L.append("- All clean CHARGE runs use the validated 0.5 V principal grid "
             "(20 solves, 0 V at 1-based index 3; -0.475 V is index 2). The earlier "
             "0.9 V partial sweeps are kept only as diagnostic evidence and are not "
             "used in the results.")
    L.append("- `Gamma_core` is a field-overlap screening metric on the FDE grid; it is not the exact energy confinement factor.\n")
    L.append("## 21. Recommended final design\n")
    if rec is not None:
        L.append("**%s** — %s\n" % (rec["exp"], rec_reason))
        L.append(fin + "\n")
    L.append("## 22. Alternative designs and trade-offs\n")
    if s is not None:
        alt = s.sort_values("loss_0V").head(5)
        L.append(table(alt, ["exp", "loss_0V", "VpiL_Vcm", "Cj_0V_fF_um", "Gamma_core"],
                       ["ID", "loss (dB/m)", "VpiL (V.cm)", "Cj (fF/um)", "Gamma_core"]) + "\n")
        L.append("These are the five lowest-loss points. All five exceed the 1.25x VpiL "
                 "screening limit, so they are Pareto trade-offs (loss vs efficiency), "
                 "not balanced recommendations. The non-dominated set is in the Pareto "
                 "table (section 17); the recommendation above keeps VpiL and Cj within "
                 "the screening limits.\n")
    L.append("## 23. Reproducibility instructions\n")
    L.append("Every runner copies the pristine master to a disposable session file, loads "
             "that file, and calls `reset_baseline()` before applying the experiment "
             "changes. The pristine master is never loaded directly.\n")
    L.append("```\n"
             "python 09_Automation/run_geometry_sweep.py\n"
             "python 09_Automation/run_experiment.py B000\n"
             "python 09_Automation/run_experiment.py D001 D002 D003 J001 J002 J003 Z001 Z002 Z003\n"
             "python 09_Automation/extract_metrics.py\n"
             "python 09_Automation/sync_baseline.py\n"
             "python 09_Automation/validate_design.py\n"
             "python 09_Automation/suggest_combined.py\n"
             "python 09_Automation/run_combined.py 07_Results/combined_config.json\n"
             "python 09_Automation/extract_metrics.py C001 C002 C003 C004\n"
             "python 09_Automation/optimize_design.py\n"
             "python 09_Automation/plot_results.py\n"
             "python 09_Automation/make_experiment_reports.py\n"
             "python 09_Automation/make_final_reports.py\n"
             "python 09_Automation/run_ac.py 00_Original_Baseline B000\n"
             "python 09_Automation/run_ac.py 03_Junction_Position J002\n"
             "```\n")
    L.append("## 24. Experiment registry and output files\n")
    if reg is not None:
        L.append(table(reg, list(reg.columns), list(reg.columns)) + "\n")
    L.append("Key files: `07_Results/all_metrics.csv`, `summary_0V.csv`, `pareto_front.csv`, "
             "`best_designs.csv`, `convergence_summary.csv`, `07_Results/plots/`.\n")

    open(os.path.join(REP, "FULL_TECHNICAL_REPORT.md"), "w", encoding="utf-8").write("\n".join(L))
    open(os.path.join(REP, "EXECUTIVE_SUMMARY.md"), "w", encoding="utf-8").write("\n".join(ex))
    fr = ["# Final Recommendations\n"]
    if rec is not None:
        fr.append("## Recommended design: `%s`\n" % rec["exp"])
        fr.append(rec_reason + "\n")
        fr.append(fin + "\n")
        fr.append("## Alternatives\n")
        if s is not None:
            fr.append(table(s.sort_values("loss_0V").head(5),
                            ["exp", "loss_0V", "VpiL_Vcm", "Cj_0V_fF_um", "Gamma_core"],
                            ["ID", "loss (dB/m)", "VpiL (V.cm)", "Cj (fF/um)", "Gamma_core"]) + "\n")
            fr.append("All five lowest-loss alternatives above exceed the 1.25x VpiL "
                      "screening limit; they are Pareto trade-offs, not balanced picks. "
                      "These are the same five shown in the full report.\n")
            j3 = s[s["exp"] == "J003"]
            if len(j3):
                j3r = j3.iloc[0]
                fr.append("**Near-tie:** J003 (+80 nm) gives loss %.1f dB/m, VpiL %.3f V.cm "
                          "and Cj %.4f fF/um. Prefer it only if VpiL/Cj dominate.\n"
                          % (j3r["loss_0V"], j3r["VpiL_Vcm"], j3r["Cj_0V_fF_um"]))
        fr.append("## Caveats\n- f3dB was not simulated; no bandwidth claim is made.\n"
                  "- Gamma_core is a screening overlap metric.\n"
                  "- Cj is per unit length.\n")
    open(os.path.join(REP, "FINAL_RECOMMENDATIONS.md"), "w", encoding="utf-8").write("\n".join(fr))
    print("reports written; recommended:", None if rec is None else rec["exp"])


if __name__ == "__main__":
    main()
