# Project-file incident: cumulative layout contamination (2026-10-27)

## What happened

The first automation batch loaded the original device project directly:

```
D:\lumerical\tw_modulator_DEVICE.ldev
```

Lumerical finalises every CHARGE run by **saving the loaded project back to the
same path** (the solver log ends with “time to finalize and save data”).  Because
the runner had modified the loaded layout (doping concentrations, junction
position, vertical implant windows), each run wrote those modifications back to
the original file.  The next run then loaded that already-modified file and
applied its own changes on top.  The experiments were therefore **not
one-variable-at-a-time**: modifications accumulated.

## Evidence

At the start of the study the original file was the user's ~443 MB project
(with stored results).  At 22:15:37 (during the B000 run) it was:

| Property | Value |
|---|---|
| size | 183,366,104 bytes (~183 MB) |
| last write | 2026-10-27 22:15:37 |
| p wg implant x | -40 nm (baseline -120 nm, i.e. +80 nm shift) |
| n wg implant x | +185 nm (baseline +105 nm) |
| p implant x | -2995 nm (baseline -3075 nm) |
| n implant x | +3155 nm (baseline +3075 nm) |
| p wg implant z | 0 … 110 nm (Z003 stacked) |
| n wg implant z | 110 … 237.5 nm (Z003 stacked) |
| concentrations | 5e23 / 7e23 / 7e23 / 5e23 (baseline, written by B000) |
| cathode value table | 20 points, -0.5 … 4.025 V (fine grid) |

This is exactly `J003 (+80 nm) + Z003 (stacked vertical) + B000 (baseline
concentrations + fine bias table)`.  The B000 “baseline” run had inherited the
contaminated geometry.

## Contamination chain

| Run | Inherited from previous save | Valid? |
|---|---|---|
| D001 (18:24) | pristine original | yes (but later overwritten by the retry) |
| D002, D003 | D001 save (doping only, geometry pristine) | yes (coarse 0.9 V grid) |
| J001 … Z003 | D003 doping; then J shifts; then Z vertical windows | **no** |
| D001/J001/Z001 retry | J002/Z002 geometry from the previous batch | **no** |
| J003, Z003 retry | D001 retry doping + previous vertical windows | **no** |
| B000 | Z003 geometry + +80 nm shift | **no** |

All invalid raw results were moved to
`07_Results/diagnostics/contaminated/<EXP>/` (charge.mat, experiment.json,
cj_derived.csv) and are kept only as evidence.

## Recovery

1. The pristine layout was reconstructed from
   `00_Original_Baseline/baseline_manifest.json` (the authoritative object tree
   captured at the start of the study) and saved as
   `00_Original_Baseline/tw_modulator_DEVICE_pristine.ldev` (3.4 MB, layout
   only).
2. The four modified doping objects and the rib/slab were reset and verified:

   | Object | x (m) | z min (m) | z max (m) | concentration (/m3) | junction width (m) |
   |---|---:|---:|---:|---:|---:|
   | p wg implant | -1.20e-7 | 0 | 2.55e-7 | 5e23 | 1.2e-7 |
   | n wg implant | 1.05e-7 | 2.5e-9 | 2.375e-7 | 7e23 | 1.1e-7 |
   | p implant | -3.075e-6 | -3e-7 | 9e-8 | 7e23 | 1e-7 |
   | n implant | 3.075e-6 | -3e-7 | 9e-8 | 5e23 | 1e-7 |

   Rib: 500 nm wide, z = 90…220 nm.  Slab: z = 0…90 nm.
3. B000 was re-run from the reconstructed pristine layout with the validated
   20-point grid.  The true 0 V point is 1-based index **3** in the array
   `[-0.5, -0.475, 0.0, 0.025, ...]` (index 2 is -0.475 V).

## Validation of the reconstructed baseline

| Metric (0 V) | Reconstructed B000 | Recorded baseline |
|---|---:|---:|
| loss | **498.23 dB/m** | 498.22 dB/m |
| neff | 2.567082 | 2.567082 |
| ng | 3.936389 | 3.936389 |
| Gamma_core | 0.354 | 0.354 |
| Cj | 0.2100 fF/um | 0.2100 fF/um |
| VpiL | 2.908 V.cm | 2.90 V.cm |

The reconstructed layout **reproduces the recorded baseline**: loss agrees to
0.01 dB/m (0.002 %), and the other metrics agree to the reported precision.
There is **no mesh-regeneration offset**.

An earlier check quoted 535.95 dB/m at "0 V"; that number is the **-0.475 V**
point (`V_cathode_index = 2`), i.e. the low-bias twin immediately below 0 V.
The final extraction uses index 3.  The -0.475 V geometry re-run is retained
only as a diagnostic in
`07_Results/diagnostics/geometry_b000_at_minus0p475V.csv`.

The charge mesh count differs slightly (25,253 vs the original 25,271) and the
solver reports the auto-refinement limit, but this does not change the
extracted loss, Cj, neff or VpiL beyond 0.01 dB/m / 0.1 %.

Consequences for the study:

* **All new CHARGE+MODE experiments are compared to the validated B000 0 V
  baseline (loss 498.23 dB/m, Cj 0.2100 fF/um, VpiL 2.908 V.cm).**
* The geometry screening (MODE-only) also uses the 0 V point; its G000 case
  reproduces the B000 baseline (498.2 dB/m), so geometry and CHARGE+MODE
  results are directly comparable.

## Prevention (implemented)

* `09_Automation/baseline_utils.py` defines the pristine master and a
  disposable session copy:
  * `DEVICE_PRISTINE = 00_Original_Baseline/tw_modulator_DEVICE_pristine.ldev`
  * `prepare_session()` copies the master to
    `00_Original_Baseline/tw_modulator_DEVICE_session.ldev` before every run.
* Every runner (`run_experiment.py`, `run_combined.py`, `run_ac.py`,
  `save_finalist.py`) now:
  1. copies the pristine master to the session file,
  2. loads the **session** file (never `D:\lumerical\tw_modulator_DEVICE.ldev`),
  3. calls `reset_baseline(d)` after `switchtolayout` and before applying the
     experiment's own changes.
* The pristine master is verified after each batch (size 3,384,401 bytes,
  mtime unchanged).
* The original path `D:\lumerical\tw_modulator_DEVICE.ldev` now holds the
  contaminated 183 MB file.  It is preserved as evidence and must not be used
  as an input again.  A copy is kept at
  `00_Original_Baseline/tw_modulator_DEVICE_current.ldev` and is published as the
  `data-v1.0` GitHub Release asset (175 MB; too large for a normal Git blob).

## Impact on the conclusions

* The geometry ranking (best: slab 70 nm, G004, Γcore 0.435, loss 450.5 dB/m vs
  baseline 498.2) is based on a fixed baseline charge.
* The doping/junction/vertical results from the contaminated runs are discarded
  and re-run from the pristine layout.
* Cj, the real-index optical metrics and the optical loss all reproduce the
  recorded baseline; the final recommendations therefore use the validated
  B000 baseline for absolute and relative improvements.
