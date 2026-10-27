# Executive Summary

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
