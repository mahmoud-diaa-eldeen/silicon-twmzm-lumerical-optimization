# Silicon Traveling-Wave MZM — Lumerical Optimization Study

A reproducible optimization study of the lateral-PN silicon traveling-wave
Mach–Zehnder modulator (TWMZM) in **Ansys Lumerical 2024 R1 (v241)**. Every number
in this repository comes from a real CHARGE / MODE / ssac run; nothing is
fabricated or hand-entered.

The study covers geometry (rib width, slab thickness), doping concentration,
junction position, vertical implant profiles, and four combined candidates.
It uses a Pareto analysis (minimize loss, VπL and Cj; maximize Γcore) instead of
arbitrary scalar weights, and reports **f3dB = NA** because the distributed
RF/electrode model was not re-run.

## Key results

| Design | What it is | loss (dB/m) | VπL (V·cm) | Cj (fF/µm) | Γcore | Note |
|---|---|---:|---:|---:|---:|---|
| **B000** | validated baseline | 498.23 | 2.908 | 0.2100 | 0.354 | reproduces the recorded 498.22 dB/m |
| **J002** | junction shift **+40 nm** | **478.57** | **2.692** | **0.2100** | 0.354 | **recommended balanced design** |
| J003 | junction shift +80 nm | 479.58 | 2.591 | 0.2095 | 0.354 | near-tie; 3.7 % lower VπL |
| G004 | slab **70 nm** (MODE screening) | 450.46 | NA | NA | 0.435 | best geometry point |
| C004 | G004 + low-loss doping (D001 ×0.5) | 196.66 | 3.966 | 0.1876 | 0.435 | low-loss Pareto end |
| D002 | channel/slab doping ×0.3 | 120.73 | 5.749 | 0.1689 | 0.354 | lowest loss, high VπL |
| C002 | G004 + ×2 doping + J002 | 892.11 | 2.139 | 0.2309 | 0.435 | lowest VπL, high loss |

**Recommendation: J002 (+40 nm).** It is the lowest-loss design that satisfies
the screening limits VπL ≤ 1.25× baseline and Cj ≤ 1.25× baseline, and it
improves both loss (−3.9 %) and VπL (−7.4 %) at unchanged Cj. J003 (+80 nm) is a
near-tie if VπL/Cj matter more than the last 1 dB/m.

The Pareto front (0.1 % relative dominance tolerance) is:
D002, C004, D001, Z002, Z003, Z001, J002, J003, C003, C002. B000 and J001 are
dominated by J002.

## Repository layout

```
00_Original_Baseline/       pristine .ldev master, baseline manifest, B000 raw data
01_Geometry_Sweeps/          MODE-only geometry screening (G000–G005)
02_Doping_Sweeps/            D001–D003 CHARGE+MODE
03_Junction_Position/        J001–J003 CHARGE+MODE (J002 finalist)
04_Vertical_Doping_Profiles/ Z001–Z003 CHARGE+MODE
05_Combined_Optimization/    C001–C004 CHARGE+MODE
06_Final_Validation/         saved J002 device .ldev and optical .lms
07_Results/                  summary CSVs, Pareto front, registry, diagnostics
08_Reports/                  full technical report, executive summary,
                             final recommendations, Egyptian-Arabic explainer
09_Automation/               reproducible Python runners + report generators
```

Start with:

- `08_Reports/EXECUTIVE_SUMMARY.md` — one-page overview.
- `08_Reports/FULL_TECHNICAL_REPORT.md` — full methodology, tables, limitations.
- `08_Reports/FINAL_RECOMMENDATIONS.md` — finalist details.
- `08_Reports/STUDENT_EXPLAINER_AR.md` — Egyptian-Arabic explanation for a student.
- `07_Results/diagnostics/PROJECT_FILE_INCIDENT.md` — the project-file incident
  and the baseline validation.

## Important conventions

- **Bias grid:** V = [-0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4] V, each followed by
  V + 0.025 V (20 solves). The +0.025 V twin is used only for the Cj finite
  difference.
- **0 V index:** in the 20-point file, 0 V is **1-based index 3**
  (`[-0.5, -0.475, 0.0, ...]`). Index 2 is −0.475 V. The Cj array has 10 principal
  points, so `Cj_fF_um[1]` (0-based) is the 0 V value.
- **Doping units:** the API writes **/m³**; the GUI shows **/cm³**.
  `1e21 /m³ = 1e15 /cm³`. For example `5e23 /m³ = 5e17 /cm³`.
- **Γcore** is a field-overlap screening metric on the FDE grid, not the exact
  energy confinement factor.
- **f3dB = NA.** The lumped `1/(2πRC)` number is a screening estimate only.
- **Rs** is the real part of the ssac impedance at 20 GHz for the **10 mm
  norm-length** cross-section, not the full electrode/TW resistance.

## Reproduce

The analysis scripts use the system Python; the Lumerical scripts must use the
Lumerical-bundled Python 3.9:

```bash
# CHARGE: baseline + one-variable-at-a-time
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/run_experiment.py B000
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/run_experiment.py D001 D002 D003 J001 J002 J003 Z001 Z002 Z003

# Geometry screening (MODE-only)
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/run_geometry_sweep.py

# MODE pass for all CHARGE experiments
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/extract_metrics.py

# Baseline sync, validation, combined config
python 09_Automation/sync_baseline.py
python 09_Automation/validate_design.py
python 09_Automation/validate_batch.py
python 09_Automation/rebuild_registry.py
python 09_Automation/suggest_combined.py

# Combined CHARGE + MODE
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/run_combined.py 07_Results/combined_config.json
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/extract_metrics.py C001 C002 C003 C004

# Analysis and reports
python 09_Automation/optimize_design.py
python 09_Automation/plot_results.py
python 09_Automation/make_experiment_reports.py
python 09_Automation/make_final_reports.py
python 09_Automation/make_student_explainer_ar.py

# Finalist AC and saved variants
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/run_ac.py 00_Original_Baseline B000
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/run_ac.py 03_Junction_Position J002
"C:\Program Files\Lumerical\v241\python\python.exe" 09_Automation/save_finalist.py 03_Junction_Position J002
```

See `09_Automation/README.md` for the full pipeline and safety rules.

## Project-file incident (disclosed)

During the first automation batch, Lumerical's save-on-run overwrote the
original `D:/lumerical/tw_modulator_DEVICE.ldev` with the modified layout. A
pristine layout was reconstructed from `baseline_manifest.json`, verified against
the recorded baseline (loss 498.23 vs 498.22 dB/m, Cj 0.2100 fF/µm, neff
2.567082, Γcore 0.354), and every reported experiment was re-run from it. The
contaminated raw results are archived under `07_Results/diagnostics/contaminated/`.
The 175 MB contaminated project is published as the
[`data-v1.0` GitHub Release asset](https://github.com/mahmoud-diaa-eldeen/silicon-twmzm-lumerical-optimization/releases/tag/data-v1.0)
(it exceeds GitHub's 100 MB per-file limit). Full evidence:
`07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`.

The original `.lms` was loaded read-only and verified unchanged; the saved
finalist `.lms` is written to a new path.

## Software and data

- Ansys Lumerical **2024 R1 (v241)**, Windows.
- Lumerical Python 3.9 (`lumapi`); analysis with Python 3.11+ (pandas, numpy,
  matplotlib).
- Raw data: CHARGE `charge.mat` (20 bias points), MODE `optical_metrics.json`
  (20 V points), ssac `ac_metrics.json` (B000 + J002), experiment metadata,
  validation and diagnostic reports.

## License

No license has been specified by the author. Add one before making the
repository public.
