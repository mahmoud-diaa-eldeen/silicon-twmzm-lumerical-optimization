# Automation Pipeline

All experiments are driven by the Ansys Lumerical 2024 R1 (v241) Python API.
The study is reproducible from the pristine master layout
`00_Original_Baseline/tw_modulator_DEVICE_pristine.ldev`; the contaminated
original `D:/lumerical/tw_modulator_DEVICE.ldev` is never used as an input.

## Files

| Script | Purpose |
|---|---|
| `baseline_utils.py` | Pristine/session paths, `prepare_session()`, `reset_baseline()`, baseline constants. |
| `run_experiment.py` | CHARGE DC for B000 / D001-D003 / J001-J003 / Z001-Z003; writes `charge.mat`, `cj_derived.csv`, `experiment.json`. |
| `run_geometry_sweep.py` | MODE-only geometry screening at 0 V on the recorded baseline charge (G000-G005). |
| `run_geometry_sweep_b000.py` | Cross-check of the geometry screening on the B000 charge (0 V, index 3). Diagnostic. |
| `run_combined.py` | CHARGE runs for C001-C004; reads `07_Results/combined_config.json`. |
| `extract_metrics.py` | Imports each `charge.mat` into MODE, extracts neff/ng/loss/Gamma/VpiL at all 20 bias points; writes `all_metrics.csv`, `summary_0V.csv`, `optical_metrics.json`. Accepts experiment IDs to merge a subset. |
| `sync_baseline.py` | Propagates the validated B000 0 V baseline into the analysis/report scripts. |
| `validate_design.py` | Checks 20/20 points, last bias 4.025 V, Cj presence; writes `convergence_summary.csv`. |
| `validate_batch.py` | Checks each clean experiment against its declared one-variable spec; writes `CLEAN_BATCH_VALIDATION.md`. |
| `rebuild_registry.py` | Rebuilds `experiment_registry.csv` from the `experiment.json` files. |
| `suggest_combined.py` | Builds C001-C004 from the validated sweeps; writes `combined_config.json`. |
| `optimize_design.py` | Pareto analysis (loss, VpiL, Cj, Gamma_core); writes `pareto_front.csv`, `pareto_geometry.csv`, `best_designs.csv`. |
| `plot_results.py` | All plots, including the small-signal AC figure when `ac_metrics.json` exists. |
| `make_experiment_reports.py` | Per-experiment `report.md`. |
| `make_final_reports.py` | `EXECUTIVE_SUMMARY.md`, `FULL_TECHNICAL_REPORT.md`, `FINAL_RECOMMENDATIONS.md`. |
| `make_student_explainer_ar.py` | Egyptian-Arabic student explainer (`08_Reports/STUDENT_EXPLAINER_AR.md`). |
| `run_ac.py` | Small-signal AC (ssac) for a finalist; writes `ac_metrics.json` (Rs, C_ac). Usage: `run_ac.py <family_dir> <exp>`. |
| `save_finalist.py` | Saves a layout-only `<exp>_device.ldev` and a geometry-matched `<exp>_optical.lms` under `06_Final_Validation/`. |

## Reproduction order

```bash
# 1) baseline + one-variable-at-a-time experiments (CHARGE, ~53 min)
python 09_Automation/run_experiment.py B000
python 09_Automation/run_experiment.py D001 D002 D003 J001 J002 J003 Z001 Z002 Z003

# 2) geometry screening (MODE-only, 0 V)
python 09_Automation/run_geometry_sweep.py

# 3) MODE pass for all CHARGE experiments (0 V, 0->4 V slope)
python 09_Automation/extract_metrics.py

# 4) baseline sync, validation, combined config
python 09_Automation/sync_baseline.py
python 09_Automation/validate_design.py
python 09_Automation/validate_batch.py
python 09_Automation/rebuild_registry.py
python 09_Automation/suggest_combined.py

# 5) combined CHARGE + MODE
python 09_Automation/run_combined.py 07_Results/combined_config.json
python 09_Automation/extract_metrics.py C001 C002 C003 C004

# 6) analysis and reports
python 09_Automation/optimize_design.py
python 09_Automation/plot_results.py
python 09_Automation/make_experiment_reports.py
python 09_Automation/make_final_reports.py
python 09_Automation/make_student_explainer_ar.py

# 7) finalists: AC + saved variants
python 09_Automation/run_ac.py 00_Original_Baseline B000
python 09_Automation/run_ac.py 03_Junction_Position J002
python 09_Automation/save_finalist.py 03_Junction_Position J002
```

## Conventions

- **Bias grid:** V = [-0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4] V, each followed
  by V+0.025 V (20 solves). The +0.025 V twin is used only for the Cj finite
  difference.
- **0 V indexing:** in the 20-point file, 0 V is **1-based index 3**
  (`[-0.5, -0.475, 0.0, ...]`). Index 2 is -0.475 V.
- **Cj:** `Cj[fF/um] = 0.5*(|dQn|+|dQp|)/dV * 1e9`, dV = 0.025 V,
  `Cj_fF_um[1]` is the 0 V value.
- **Concentrations:** written through the API in /m^3; the GUI shows /cm^3
  (1e21 /m^3 = 1e15 /cm^3).
- **f3dB:** NA. The distributed RF/electrode model was not re-run; the lumped
  `1/(2*pi*R*C)` number is a screening estimate only.
- **Gamma_core:** a field-overlap screening metric on the FDE grid, not the
  exact energy confinement factor.
- **Python:** `lumapi` scripts must run with
  `C:\Program Files\Lumerical\v241\python\python.exe` (Python 3.9 + h5py);
  the analysis/report scripts use the system Python.

## Project-file safety

- The original `D:/lumerical/tw_modulator_DEVICE.ldev` was overwritten by
  Lumerical's save-on-run during the first batch. The pristine layout was
  reconstructed and validated; see
  `07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`.
- `prepare_session()` copies the pristine master to a disposable session file.
  Every DEVICE runner loads the session file and calls `reset_baseline()`
  before applying its own changes.
- The MODE `.lms` is loaded read-only; its size and mtime are verified
  unchanged after the runs. Finalist `.lms` variants are saved to new paths.
