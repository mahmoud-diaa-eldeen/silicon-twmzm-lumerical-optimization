# Full Technical Report — Silicon TWMZM Optimization

Software: Ansys Lumerical 2024 R1 (v241). The original project was overwritten by Lumerical's save-on-run during the first batch; a pristine layout was rebuilt from the manifest and all reported runs use it (see `PROJECT_FILE_INCIDENT.md`).

## 1. Executive summary

A reproducible Ansys Lumerical 2024 R1 study of the lateral-PN silicon traveling-wave MZM was completed. Every result below comes from a CHARGE and/or MODE run recorded in the workspace.

**Project-file incident (disclosed):** during the first automation batch, Lumerical's save-on-run overwrote the original `D:/lumerical/tw_modulator_DEVICE.ldev` with the modified layout. A pristine layout was reconstructed from `baseline_manifest.json`, verified against the recorded baseline (Cj, neff, Gamma_core), and all reported experiments were re-run from it. The contaminated raw results are archived under `07_Results/diagnostics/contaminated/`; full evidence is in `07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`.

**Baseline convention:** every percentage change below uses the B000 re-run baseline (loss 498.2 dB/m, Cj(0V) 0.2100 fF/um, VpiL 2.91 V.cm). The reconstructed pristine layout reproduces the recorded baseline loss (498.22 dB/m) to 0.01 dB/m, so there is no mesh-offset correction.

**Recommended design:** `J002` (lowest 0 V loss among all individual and combined experiments that satisfy VpiL <= 1.25x baseline and Cj <= 1.25x baseline).
It gives loss = 478.6 dB/m (baseline 498.2), Gamma_core = 0.354 (baseline 0.354), VpiL = 2.692 V.cm (baseline 2.91) and Cj(0V) = 0.2100 fF/um (baseline 0.2100).

**Near-tie alternative:** J003 (+80 nm) gives loss 479.6 dB/m (1.0 dB/m above J002), VpiL 2.591 V.cm (3.7 % lower) and Cj 0.2095 fF/um. Prefer J003 if VpiL/Cj dominate.

Key findings:
- Geometry: the 70 nm slab (G004) gives the best combination of loss and confinement in the MODE screening (450.5 dB/m, Gamma_core 0.435); the 110 nm slab is the worst (525.3 dB/m).
- Doping: the lowest-loss doping case is D002 (120.7 dB/m), but it trades against VpiL; Rs was not calculated for it (NA).
- Junction: J002 (+40 nm shift) is the balanced improvement: loss 478.6 dB/m (-3.9 % vs baseline), VpiL 2.692 V.cm (-7.4 %), Cj 0.2100 fF/um (unchanged).
- f3dB was not simulated: the distributed RF/electrode model was not re-run, so no bandwidth number is claimed. The RC product is reported only as a screening estimate.

All raw data, logs and per-experiment reports are under `TW_Modulator_Optimization_Study/`.

## 2. Original device architecture

- Lateral PN-junction silicon rib waveguide, SiO2 cladding, Al contacts.
- Rib 500 x 130 nm on a 90 nm slab (total Si 220 nm).
- Contact windows |x| = 3.8..5 um; device width 10 um; phase-shifter length 5 mm.
- Full object/property record: `00_Original_Baseline/baseline_manifest.json`.

## 3. Verified baseline parameters

These are the **B000 re-run** values (same mesh as every clean CHARGE+MODE experiment). The true 0 V point is `V_cathode_index = 3` on the 20-point grid; the reconstructed layout reproduces the recorded baseline loss (498.22 dB/m) to 0.01 dB/m. The 535.95 dB/m value quoted in an earlier check is the -0.475 V point, not 0 V (`07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`).

| Metric | Value |
|---|---:|
| neff (0 V) | 2.567082 |
| ng (0 V) | 3.936389 |
| loss (0 V) | 498.23 dB/m (4.982 dB/cm) |
| d neff (0->4 V) | 1.066e-04 |
| VpiL | 2.91 V.cm |
| Gamma_core | 0.354 |
| Gamma_slab | 0.362 |
| Aeff | 2.056e-13 m2 |
| TE fraction | 0.9866 |
| Cj (0 V) | 0.2100 fF/um |
| Cj (4 V) | 0.1398 fF/um |

Doping (script API /m3, GUI /cm3): p wg 5e23 (5e17), n wg 7e23 (7e17), p slab 7e23 (7e17), n slab 5e23 (5e17), p++/n++ 1e25 (1e19).

## 4. Mathematical model and assumptions

See `08_Reports/EQUATIONS_AND_ASSUMPTIONS.md`. In short: beta=k0 neff; loss = 8.686|Im(beta)| (cross-checked against the native loss); Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening); VpiL = lambda/(2|d(dneff)/dV|); Cj = |dQ/dV| with dv=0.025 V; Rs from ssac; f_RC is an estimate only, not the traveling-wave bandwidth.

## 5. Optimization variables and permitted ranges

- Rib width 450-600 nm; slab thickness 70-110 nm (MODE screening).
- Channel/slab doping scale 0.3x-2.0x of baseline.
- Junction shift -40 to +80 nm.
- Vertical implant placement: buried (0-120 nm), upper (100-220 nm), stacked p/n.

## 6. Experiment methodology

One variable at a time; MODE-only screening for geometry (baseline charge), CHARGE DC + MODE for doping/junction/vertical/combined. Bias grid 0.5 V steps (20 solves). Completion requires all points saved; see the CHARGE diagnostic.

## 7. Completed experiment IDs

| ID | Family | Status | CHARGE pts | last V | complete | Cj 0V (fF/um) | MODE done |
|---|---|---|---|---|---|---|---|
| B000 | 00_Original_Baseline | SUCCESS | 20 | 4.025 | True | 0.21 | True |
| G000 | 01_Geometry_Sweeps | SUCCESS (MODE-only, baseline charge) | 0 | NA | True | NA | True |
| G001 | 01_Geometry_Sweeps | SUCCESS (MODE-only, baseline charge) | 0 | NA | True | NA | True |
| G002 | 01_Geometry_Sweeps | SUCCESS (MODE-only, baseline charge) | 0 | NA | True | NA | True |
| G003 | 01_Geometry_Sweeps | SUCCESS (MODE-only, baseline charge) | 0 | NA | True | NA | True |
| G004 | 01_Geometry_Sweeps | SUCCESS (MODE-only, baseline charge) | 0 | NA | True | NA | True |
| G005 | 01_Geometry_Sweeps | SUCCESS (MODE-only, baseline charge) | 0 | NA | True | NA | True |
| D001 | 02_Doping_Sweeps | SUCCESS | 20 | 4.025 | True | 0.1873 | True |
| D002 | 02_Doping_Sweeps | SUCCESS | 20 | 4.025 | True | 0.1689 | True |
| D003 | 02_Doping_Sweeps | SUCCESS | 20 | 4.025 | True | 0.2311 | True |
| J001 | 03_Junction_Position | SUCCESS | 20 | 4.025 | True | 0.2101 | True |
| J002 | 03_Junction_Position | SUCCESS | 20 | 4.025 | True | 0.21 | True |
| J003 | 03_Junction_Position | SUCCESS | 20 | 4.025 | True | 0.2095 | True |
| Z001 | 04_Vertical_Doping_Profiles | SUCCESS | 20 | 4.025 | True | 0.1913 | True |
| Z002 | 04_Vertical_Doping_Profiles | SUCCESS | 20 | 4.025 | True | 0.1955 | True |
| Z003 | 04_Vertical_Doping_Profiles | SUCCESS | 20 | 4.025 | True | 0.1886 | True |
| C001 | 05_Combined_Optimization | SUCCESS | 20 | 4.025 | True | 0.2313 | False |
| C002 | 05_Combined_Optimization | SUCCESS | 20 | 4.025 | True | 0.2309 | False |
| C003 | 05_Combined_Optimization | SUCCESS | 20 | 4.025 | True | 0.2148 | False |
| C004 | 05_Combined_Optimization | SUCCESS | 20 | 4.025 | True | 0.1876 | False |

## 8. Geometry optimization results

| ID | W (nm) | slab (nm) | neff | ng | loss (dB/m) | Gamma_core | Gamma_slab | Aeff (m2) | TE frac |
|---|---|---|---|---|---|---|---|---|---|
| G000 | 500 | 90 | 2.567 | 3.936 | 498.2 | 0.3535 | 0.3619 | 2.056e-13 | 0.9866 |
| G001 | 450 | 90 | 2.521 | 3.931 | 478.6 | 0.3264 | 0.367 | 2.084e-13 | 0.9835 |
| G002 | 550 | 90 | 2.605 | 3.931 | 500 | 0.3831 | 0.358 | 2.051e-13 | 0.9892 |
| G003 | 600 | 90 | 2.636 | 3.921 | 501.2 | 0.3988 | 0.355 | 2.065e-13 | 0.9913 |
| G004 | 500 | 70 | 2.533 | 3.998 | 450.5 | 0.4351 | 0.2659 | 1.998e-13 | 0.9856 |
| G005 | 500 | 110 | 2.604 | 3.883 | 525.3 | 0.2719 | 0.4596 | 2.150e-13 | 0.9883 |

Interpretation: a thinner slab (70 nm) strongly increases the rib-core overlap and reduces the doped-slab overlap, lowering loss (450.5 vs 498.2 dB/m) while raising Gamma_core from 0.354 to 0.435. A thicker slab (110 nm) does the opposite (loss 525.3 dB/m, Gamma_core 0.272). Wider rib raises Gamma_core (0.326 at 450 nm to 0.399 at 600 nm) at a small loss penalty.

## 9. Doping optimization results

| ID | Family | Status | neff 0V | ng 0V | loss 0V (dB/m) | Gamma_core | d neff 0-4V | VpiL (V.cm) | Cj 0V (fF/um) | Cj 4V (fF/um) | W (nm) | slab (nm) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B000 | 00_Original_Baseline | SUCCESS | 2.567 | 3.936 | 498.2 | 0.3535 | 1.066e-04 | 2.908 | 0.21 | 0.1398 | 500 | 90 |
| D001 | 02_Doping_Sweeps | SUCCESS | 2.567 | 3.936 | 226 | 0.3536 | 7.572e-05 | 4.094 | 0.1873 | 0.114 | 500 | 90 |
| D002 | 02_Doping_Sweeps | SUCCESS | 2.567 | 3.936 | 120.7 | 0.3536 | 5.392e-05 | 5.749 | 0.1689 | 0.09484 | 500 | 90 |
| D003 | 02_Doping_Sweeps | SUCCESS | 2.567 | 3.936 | 1051 | 0.3535 | 1.306e-04 | 2.374 | 0.2311 | 0.1671 | 500 | 90 |
| J001 | 03_Junction_Position | SUCCESS | 2.567 | 3.936 | 513.2 | 0.3536 | 9.540e-05 | 3.249 | 0.2101 | 0.1393 | 500 | 90 |
| J002 | 03_Junction_Position | SUCCESS | 2.567 | 3.936 | 478.6 | 0.3535 | 1.152e-04 | 2.692 | 0.21 | 0.1398 | 500 | 90 |
| J003 | 03_Junction_Position | SUCCESS | 2.567 | 3.936 | 479.6 | 0.3535 | 1.196e-04 | 2.591 | 0.2095 | 0.138 | 500 | 90 |
| Z001 | 04_Vertical_Doping_Profiles | SUCCESS | 2.567 | 3.937 | 414.6 | 0.3536 | 8.475e-05 | 3.658 | 0.1913 | 0.122 | 500 | 90 |
| Z002 | 04_Vertical_Doping_Profiles | SUCCESS | 2.567 | 3.937 | 362.4 | 0.3536 | 7.900e-05 | 3.924 | 0.1955 | 0.1304 | 500 | 90 |
| Z003 | 04_Vertical_Doping_Profiles | SUCCESS | 2.567 | 3.937 | 378.5 | 0.3536 | 8.069e-05 | 3.842 | 0.1886 | 0.1268 | 500 | 90 |
| C001 | 05_Combined_Optimization | SUCCESS | 2.533 | 3.998 | 941.9 | 0.4351 | 1.374e-04 | 2.257 | 0.2313 | 0.1673 | 500 | 70 |
| C002 | 05_Combined_Optimization | SUCCESS | 2.532 | 3.997 | 892.1 | 0.4351 | 1.449e-04 | 2.139 | 0.2309 | 0.1668 | 500 | 70 |
| C003 | 05_Combined_Optimization | SUCCESS | 2.533 | 3.998 | 658.5 | 0.4351 | 1.054e-04 | 2.942 | 0.2148 | 0.1552 | 500 | 70 |
| C004 | 05_Combined_Optimization | SUCCESS | 2.533 | 3.998 | 196.7 | 0.4352 | 7.816e-05 | 3.966 | 0.1876 | 0.1136 | 500 | 70 |

Interpretation: lower doping reduces free-carrier absorption and Cj but raises VpiL and Rs; the measured trend is in the tables.

## 10. Junction-position results

Junction shifts are included in the table above (J001 -40 nm, J002 +40 nm, J003 +80 nm). The loss/VpiL trade-off is plotted in `07_Results/plots/junction_sweep.png`.

## 11. Vertical-profile results

Z001 (buried), Z002 (upper) and Z003 (stacked p/n) are included above. See `07_Results/plots/vertical_profiles.png`.

## 12. Combined optimization results

- **C001**: W=500 nm, slab=70 nm, dx=0 nm; loss=941.9 dB/m, Gamma_core=0.435, VpiL=2.257 V.cm, Cj(0V)=0.2313 fF/um.
- **C002**: W=500 nm, slab=70 nm, dx=40 nm; loss=892.1 dB/m, Gamma_core=0.435, VpiL=2.139 V.cm, Cj(0V)=0.2309 fF/um.
- **C003**: W=500 nm, slab=70 nm, dx=0 nm; loss=658.5 dB/m, Gamma_core=0.435, VpiL=2.942 V.cm, Cj(0V)=0.2148 fF/um.
- **C004**: W=500 nm, slab=70 nm, dx=0 nm; loss=196.7 dB/m, Gamma_core=0.435, VpiL=3.966 V.cm, Cj(0V)=0.1876 fF/um.

## 13. Optical mode confinement analysis

Gamma_core is a field-overlap screening metric on the FDE grid, not the exact energy confinement factor. The baseline splits roughly 0.354 rib / 0.362 slab / 0.284 cladding, which explains the strong sensitivity to slab thickness.

## 14. Optical loss analysis

Loss is the native MODE result (free-carrier absorption from the imported CHARGE carrier maps). Scattering loss is not represented in the model and is not claimed.

## 15. Modulation efficiency analysis

VpiL uses the 0->4 V slope of the simulated d neff. The device is treated with the single-arm convention used by the original example; the push-pull factor is not applied without verifying the architecture.

## 16. Electrical analysis

Cj is the per-unit-length dQ/dV at 0 V (dv=0.025 V). Rs is the real part of the ssac impedance at 20 GHz for the **10 mm norm-length** cross-section; it is not the full electrode/traveling-wave resistance. C_ac comes from the same ssac run (1 MHz value quoted, per um). f3dB is NA because the distributed RF model was not re-run. The lumped RC estimate is a screening number only.

## 17. Pareto-front analysis

Objectives: minimize loss, VpiL and Cj; maximize Gamma_core. Dominance uses a 0.1 % relative tolerance per objective to suppress sub-grid numerical noise (not a weighting). Pareto candidates: D002, C004, D001, Z002, Z003, Z001, J002, J003, C003, C002.

| ID | loss (dB/m) | VpiL (V.cm) | Cj (fF/um) | Gamma_core |
|---|---|---|---|---|
| D002 | 120.7 | 5.749 | 0.1689 | 0.3536 |
| C004 | 196.7 | 3.966 | 0.1876 | 0.4352 |
| D001 | 226 | 4.094 | 0.1873 | 0.3536 |
| Z002 | 362.4 | 3.924 | 0.1955 | 0.3536 |
| Z003 | 378.5 | 3.842 | 0.1886 | 0.3536 |
| Z001 | 414.6 | 3.658 | 0.1913 | 0.3536 |
| J002 | 478.6 | 2.692 | 0.21 | 0.3535 |
| J003 | 479.6 | 2.591 | 0.2095 | 0.3535 |
| C003 | 658.5 | 2.942 | 0.2148 | 0.4351 |
| C002 | 892.1 | 2.139 | 0.2309 | 0.4351 |

Geometry Pareto (loss, Gamma_core): G004 (`pareto_geometry.csv`).

## 18. Mesh and convergence validation

The CHARGE mesh is unchanged from the original (min edge 4 nm, max edge 600 nm, dz 0.2 nm); the MODE mesh uses a 10 nm core override. The CHARGE sweep was validated at 0.5 V steps after the 0.9 V step was shown to stop silently. See `07_Results/diagnostics/CHARGE_DIAGNOSTIC.md` and `convergence_summary.csv`.

## 19. Comparison with the baseline

| Metric | Baseline | J002 | Change |
|---|---:|---:|---:|
| loss (0 V) | 498.23 dB/m | 478.6 dB/m | -3.9 % |
| VpiL | 2.91 V.cm | 2.692 V.cm | -7.4 % |
| Cj (0 V) | 0.2100 fF/um | 0.2100 fF/um | +0.0 % |
| Gamma_core | 0.354 | 0.354 | -0.0 % |


## 20. Limitations and uncertainties

- Gamma_core is a screening field-overlap metric; it is not the exact energy confinement factor.
- Cj is per unit length; total capacitance scales with the chosen phase-shifter length.
- Rs is from a 2D ssac extraction; contact resistance and the full metal stack are not modelled beyond the original project.
- f3dB is not simulated; no bandwidth claim is made.
- The combined candidates use the baseline CHARGE mesh and a single wavelength (1550 nm).
- All clean CHARGE runs use the validated 0.5 V principal grid (20 solves, 0 V at 1-based index 3; -0.475 V is index 2). The earlier 0.9 V partial sweeps are kept only as diagnostic evidence and are not used in the results.
- `Gamma_core` is a field-overlap screening metric on the FDE grid; it is not the exact energy confinement factor.

## 21. Recommended final design

**J002** — lowest 0 V loss among all individual and combined experiments that satisfy VpiL <= 1.25x baseline and Cj <= 1.25x baseline

| Parameter | Value |
|---|---:|
| Rib width | 500 nm |
| Rib height | 130 nm |
| Slab thickness | 90 nm |
| Total Si thickness | 220 nm |
| Junction shift | 40 nm |
| p wg concentration | 5e+23 /m3 (5e+17 /cm3) |
| n wg concentration | 7e+23 /m3 (7e+17 /cm3) |
| p slab concentration | 7e+23 /m3 (7e+17 /cm3) |
| n slab concentration | 5e+23 /m3 (5e+17 /cm3) |
| Gamma_core (field overlap) | 0.354 |
| neff (0 V) | 2.567032 |
| Optical loss (0 V) | 478.57 dB/m |
| VpiL | 2.692 V.cm |
| Cj (0 V) | 0.2100 fF/um |
| Rs (0 V, 20.0 GHz; 10 mm norm length) | 1.6033 ohm |
| C_ac (0 V, 1 MHz; per um) | 0.2158 fF/um |
| f3dB | NA (distributed RF not simulated) |
| Mesh | conformal, 12 PML, 10 nm core override |
| Convergence | CHARGE 20/20 points; MODE converged |
| vs baseline loss | -3.9 % |
| vs baseline VpiL | -7.4 % |
| vs baseline Cj | +0.0 % |
| vs baseline Gamma_core | -0.0 % |

## 22. Alternative designs and trade-offs

| ID | loss (dB/m) | VpiL (V.cm) | Cj (fF/um) | Gamma_core |
|---|---|---|---|---|
| D002 | 120.7 | 5.749 | 0.1689 | 0.3536 |
| C004 | 196.7 | 3.966 | 0.1876 | 0.4352 |
| D001 | 226 | 4.094 | 0.1873 | 0.3536 |
| Z002 | 362.4 | 3.924 | 0.1955 | 0.3536 |
| Z003 | 378.5 | 3.842 | 0.1886 | 0.3536 |

These are the five lowest-loss points. All five exceed the 1.25x VpiL screening limit, so they are Pareto trade-offs (loss vs efficiency), not balanced recommendations. The non-dominated set is in the Pareto table (section 17); the recommendation above keeps VpiL and Cj within the screening limits.

## 23. Reproducibility instructions

Every runner copies the pristine master to a disposable session file, loads that file, and calls `reset_baseline()` before applying the experiment changes. The pristine master is never loaded directly.

```
python 09_Automation/run_geometry_sweep.py
python 09_Automation/run_experiment.py B000
python 09_Automation/run_experiment.py D001 D002 D003 J001 J002 J003 Z001 Z002 Z003
python 09_Automation/extract_metrics.py
python 09_Automation/sync_baseline.py
python 09_Automation/validate_design.py
python 09_Automation/suggest_combined.py
python 09_Automation/run_combined.py 07_Results/combined_config.json
python 09_Automation/extract_metrics.py C001 C002 C003 C004
python 09_Automation/optimize_design.py
python 09_Automation/plot_results.py
python 09_Automation/make_experiment_reports.py
python 09_Automation/make_final_reports.py
python 09_Automation/run_ac.py 00_Original_Baseline B000
python 09_Automation/run_ac.py 03_Junction_Position J002
```

## 24. Experiment registry and output files

| exp | family | description | status | runtime_s | n_charge_points | W_nm | slab_nm | p_wg | n_wg | dx_nm | Cj_0V_fF_um | Cj_4V_fF_um |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B000 | 00_Original_Baseline | baseline (fine bias grid) | SUCCESS | 354.2 | 20 | 500 | 90 | 5.000e+23 | 7.000e+23 | 0 | 0.21 | 0.1398 |
| D001 | 02_Doping_Sweeps | channel+slab doping x0.5 | SUCCESS | 352.9 | 20 | 500 | 90 | 2.500e+23 | 3.500e+23 | 0 | 0.1873 | 0.114 |
| D002 | 02_Doping_Sweeps | channel+slab doping x0.3 | SUCCESS | 352.7 | 20 | 500 | 90 | 1.500e+23 | 2.100e+23 | 0 | 0.1689 | 0.09484 |
| D003 | 02_Doping_Sweeps | channel+slab doping x2.0 | SUCCESS | 371.9 | 20 | 500 | 90 | 1.000e+24 | 1.400e+24 | 0 | 0.2311 | 0.1671 |
| J001 | 03_Junction_Position | junction shift -40 nm | SUCCESS | 358.9 | 20 | 500 | 90 | 5.000e+23 | 7.000e+23 | -40 | 0.2101 | 0.1393 |
| J002 | 03_Junction_Position | junction shift +40 nm | SUCCESS | 347.3 | 20 | 500 | 90 | 5.000e+23 | 7.000e+23 | 40 | 0.21 | 0.1398 |
| J003 | 03_Junction_Position | junction shift +80 nm | SUCCESS | 344.9 | 20 | 500 | 90 | 5.000e+23 | 7.000e+23 | 80 | 0.2095 | 0.138 |
| Z001 | 04_Vertical_Doping_Profiles | buried wg implants z=0..120 nm | SUCCESS | 342.2 | 20 | 500 | 90 | 5.000e+23 | 7.000e+23 | 0 | 0.1913 | 0.122 |
| Z002 | 04_Vertical_Doping_Profiles | upper wg implants z=100..220 nm | SUCCESS | 357.5 | 20 | 500 | 90 | 5.000e+23 | 7.000e+23 | 0 | 0.1955 | 0.1304 |
| Z003 | 04_Vertical_Doping_Profiles | vertically stacked p (0-110 nm) / n (110-237 nm) | SUCCESS | 346.9 | 20 | 500 | 90 | 5.000e+23 | 7.000e+23 | 0 | 0.1886 | 0.1268 |
| C001 | 05_Combined_Optimization | best geometry + best doping (D003) | SUCCESS | 366.1 | 20 | 500 | 70 | 1.000e+24 | 1.400e+24 | 0 | 0.2313 | 0.1673 |
| C002 | 05_Combined_Optimization | best geometry + best doping + junction J002 | SUCCESS | 354.6 | 20 | 500 | 70 | 1.000e+24 | 1.400e+24 | 40 | 0.2309 | 0.1668 |
| C003 | 05_Combined_Optimization | best geometry + best doping + vertical Z002 | SUCCESS | 314 | 20 | 500 | 70 | 1.000e+24 | 1.400e+24 | 0 | 0.2148 | 0.1552 |
| C004 | 05_Combined_Optimization | best geometry + low-loss doping (D001, Pareto low-loss end) | SUCCESS | 313.7 | 20 | 500 | 70 | 2.500e+23 | 3.500e+23 | 0 | 0.1876 | 0.1136 |

Key files: `07_Results/all_metrics.csv`, `summary_0V.csv`, `pareto_front.csv`, `best_designs.csv`, `convergence_summary.csv`, `07_Results/plots/`.
