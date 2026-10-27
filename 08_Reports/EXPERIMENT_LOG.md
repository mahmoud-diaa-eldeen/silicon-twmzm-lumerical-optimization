# Experiment Log

Chronological record of the optimization study. Every entry is produced from an
actual run; failed/skipped runs are recorded explicitly.

## Environment
- Ansys Lumerical 2024 R1 (v241)
- Python API: C:\Program Files\Lumerical\v241\python\python.exe
- **2026-10-27 incident:** the original `D:\lumerical\tw_modulator_DEVICE.ldev`
  was overwritten by Lumerical's save-on-run.  A pristine layout was rebuilt
  from `baseline_manifest.json`; all runs now use a disposable session copy and
  an explicit baseline reset.  See
  `07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`.

## Baseline
- Verified object tree and properties from the `.ldev` via `getobjectlist` / `getObjectBySelection`.
- Confirmed doping concentrations in /m^3 and converted to /cm^3 (1e21 /m^3 = 1e15 /cm^3).
- Baseline CHARGE run: 6 bias points x (V, V+0.025 V) = 12 solves, 270 s.
- Baseline MODE metrics reproduced (neff, ng, loss, d neff).

## Family 1 — Geometry (MODE-only, baseline charge)
- G000 baseline W=500 nm, slab=90 nm
- G001 W=450 nm
- G002 W=550 nm
- G003 W=600 nm
- G004 slab=70 nm
- G005 slab=110 nm
Status: completed (see 01_Geometry_Sweeps/geometry_metrics.csv).  The G000 case
reproduces the B000 0 V baseline (498.2 dB/m), so the ranking is directly
comparable with the CHARGE+MODE experiments.

## Family 2 — Doping (CHARGE + MODE)
- D001 channel+slab x0.5
- D002 channel+slab x0.3
- D003 channel+slab x2.0
Status: re-running from the pristine layout on the validated 0.5 V grid after
the project-file incident (earlier results archived under
`07_Results/diagnostics/contaminated/`).

## Family 3 — Junction position (CHARGE + MODE)
- J001 shift -40 nm
- J002 shift +40 nm
- J003 shift +80 nm
Status: re-running from the pristine layout (earlier results contaminated).

## Family 4 — Vertical profiles (CHARGE + MODE)
- Z001 wg implants buried (z 0..120 nm)
- Z002 wg implants upper (z 100..220 nm)
- Z003 vertically stacked p (0..110 nm) / n (110..237.5 nm)
Status: re-running from the pristine layout (earlier results contaminated).

## Family 5 — Combined (CHARGE complete, MODE running)
- C001 best geometry (W 500, slab 70) + D003 (x2 doping)
- C002 C001 + J002 junction shift (+40 nm)
- C003 C001 + Z002 vertical profile (wg implants 100..220 nm)
- C004 best geometry + D001 (x0.5 doping, Pareto low-loss end)
- All four: 20/20 points, last bias 4.025 V, status SUCCESS.
- Cj(0 V), fF/um: C001 0.2313; C002 0.2309; C003 0.2148; C004 0.1876.
- Optical metrics are being extracted by the combined MODE pass.

## Family 6 — Finalist validation
- pending.

## CHARGE incomplete-result incident (D001 / J001 / Z001)
- First batch used a 0.9 V principal step (6 points x2). D001/J001 stopped at
  1.025 V, Z001 at 0.025 V; no exception was raised and the solver returned.
- Partial files archived with SHA-256 to `07_Results/diagnostics/partial/`.
- Diagnostic A: 2.0 V solved alone from a fresh start (Cj=0.1259 fF/um).
- Diagnostic B: 0.5 V-step sweep completed 20/20 points (Cj: 0.2272 -> 0.0991).
- Root cause: 0.9 V step too large for the Newton sweep; CHARGE stops the
  sweep on a failed point without raising. Fix: 0.5 V steps + Python-side Cj
  extraction + explicit completion checks. Tolerances unchanged.
- Full evidence: `07_Results/diagnostics/CHARGE_DIAGNOSTIC.md`.

## Notes / incidents
- `toscript` on the 443 MB .ldev hangs; object inspection uses `getobjectlist` recursion instead.
- `getnumberofobjects` / `?` are not usable through `lumapi.eval`; use `getobjectlist(path)`.
- Concentration units verified against Ansys docs.

## Clean batch results (2026-10-27, after the incident recovery)
- B000 / D001–D003 / J001–J003 / Z001–Z003 re-run from the pristine layout on the
  validated 0.5 V grid; all 10 experiments: 20/20 points, last bias 4.025 V,
  status SUCCESS, spec match PASS (`07_Results/diagnostics/CLEAN_BATCH_VALIDATION.md`).
- Cj(0 V), fF/um: B000 0.2100; D001 0.1873; D002 0.1689; D003 0.2311;
  J001 0.2101; J002 0.2100; J003 0.2095; Z001 0.1913; Z002 0.1955; Z003 0.1886.
- The Cj trend is monotonic with doping (lower doping -> lower Cj); the junction
  shift changes Cj by <0.3 %, as expected for a fixed doping profile.
- Optical metrics (loss, VpiL, Gamma_core) are being extracted by the MODE pass;
  they are written to `07_Results/all_metrics.csv` and `summary_0V.csv`.

### Optical metrics (MODE, 0 V / 0-4 V slope)
| Exp | loss 0 V (dB/m) | VpiL (V.cm) | Gamma_core | neff 0 V | Cj 0 V (fF/um) |
|---|---:|---:|---:|---:|---:|
| B000 | 498.2 | 2.908 | 0.354 | 2.567082 | 0.2100 |
| D001 | 226.0 | 4.094 | 0.354 | 2.567217 | 0.1873 |
| D002 | 120.7 | 5.749 | 0.354 | 2.567274 | 0.1689 |
| D003 | 1050.6 | 2.374 | 0.354 | 2.566837 | 0.2311 |
| J001 | 513.2 | 3.249 | 0.354 | 2.567128 | 0.2101 |
| J002 | 478.6 | 2.692 | 0.354 | 2.567032 | 0.2100 |
| J003 | 479.6 | 2.591 | 0.354 | 2.566976 | 0.2095 |
| Z001 | 414.6 | 3.658 | 0.354 | 2.567123 | 0.1913 |
| Z002 | 362.4 | 3.924 | 0.354 | 2.567149 | 0.1955 |
| Z003 | 378.5 | 3.842 | 0.354 | 2.567132 | 0.1886 |
| C001 | 941.9 | 2.257 | 0.435 | 2.532510 | 0.2313 |
| C002 | 892.1 | 2.139 | 0.435 | 2.532430 | 0.2309 |
| C003 | 658.5 | 2.942 | 0.435 | 2.532630 | 0.2148 |
| C004 | 196.7 | 3.966 | 0.435 | 2.532850 | 0.1876 |

**Interpretation.**
- Doping is the dominant loss lever: lowering it by x0.5/x0.3 cuts loss to 226/121 dB/m
  but raises VpiL to 4.09/5.75 V.cm. Raising it x2 lowers VpiL to 2.37 but raises loss
  to 1051 dB/m. Cj follows the doping monotonic trend.
- Junction shift: J002 (+40 nm) is the best balanced design found so far -
  loss 478.6 (-3.9 % vs baseline), VpiL 2.692 (-7.4 %), Cj 0.2100 (unchanged),
  Gamma_core unchanged. J001 (-40 nm) worsens both loss and VpiL.
- Vertical profiles: Z001/Z002/Z003 all reduce loss (363-415 dB/m) but raise VpiL
  above the 1.25x screening limit (3.658-3.924 vs 3.635 V.cm), i.e. a clear
  loss/efficiency trade-off rather than a free improvement.
- Gamma_core stays ~0.354 for B/D/J/Z because the optical mode is essentially
  unchanged by doping/junction/vertical variants at fixed rib geometry. The combined
  designs use the 70 nm slab, so their Gamma_core is 0.435.
- Combined: C001/C002 (x2 doping + thin slab) cut VpiL to 2.26/2.14 V.cm but raise
  loss to 942/892 dB/m; C003 (adds the Z002 vertical profile) gives 658.5 dB/m and
  2.942 V.cm; C004 (x0.5 doping + thin slab) gives the lowest loss in the study,
  196.7 dB/m, at VpiL 3.966 V.cm. The thin slab alone does not rescue the loss once
  the doping is doubled.
- Pareto front (0.1 % relative dominance tolerance, objectives: min loss, min VpiL,
  min Cj, max Gamma_core): D002, C004, D001, Z002, Z003, Z001, J002, J003, C003,
  C002. B000 and J001 are dominated by J002.
- Recommendation: **J002** (+40 nm) - loss 478.6 dB/m, VpiL 2.692 V.cm,
  Cj 0.2100 fF/um, Gamma_core 0.354; within the screening limits and better than
  B000 on both loss and VpiL. J003 (+80 nm) is a near-tie (479.6 / 2.591 / 0.2095).

## Project-file contamination incident (2026-10-27)
- Each CHARGE run finalises by saving the loaded project back to its path.  The
  first batch loaded `D:\lumerical\tw_modulator_DEVICE.ldev`, so modifications
  accumulated across runs (D003 doping -> J shifts -> Z vertical windows ->
  B000).  The original file was overwritten (443 MB -> 183 MB, mtime 22:15:37).
- Invalid raw results (B000, D001 retry, J001-J003, Z001-Z003) were archived to
  `07_Results/diagnostics/contaminated/` and are not used.
- Recovery: pristine layout rebuilt from `baseline_manifest.json` as
  `00_Original_Baseline/tw_modulator_DEVICE_pristine.ldev`; B000 re-run on the
  20-point grid gives, at the true 0 V point (`V_cathode_index = 3`):
  loss 498.23 dB/m (recorded 498.22), Cj 0.2100 fF/um, neff 2.567082,
  Gamma_core 0.354, VpiL 2.908 V.cm.  The reconstruction therefore reproduces
  the recorded baseline; there is no residual mesh offset.
- Note: an earlier check quoted 535.95 dB/m at "0 V"; that is the -0.475 V
  point (`V_cathode_index = 2`), retained only as a diagnostic in
  `07_Results/diagnostics/geometry_b000_at_minus0p475V.csv`.
- Prevention: `baseline_utils.prepare_session()` + `reset_baseline()` in every
  runner; the pristine master is never loaded directly.
- Full evidence: `07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`.

