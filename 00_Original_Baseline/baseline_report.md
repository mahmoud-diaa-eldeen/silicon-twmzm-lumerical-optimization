# Baseline Report — Original TWMZM Device

## 1. Scope
This report documents the verified state of the original Ansys TWMZM example
(`tw_modulator_DEVICE.ldev` + `tw_modulator_optical_MODE.lms`) before any
optimization. The original files were not modified.

## 2. Architecture
- Lateral PN-junction silicon rib modulator.
- Rib: 500 nm wide x 130 nm high, on a 90 nm Si slab (total Si thickness 220 nm).
- Cladding/BOX: SiO2.
- Al contacts at x = -5..-3.8 um (anode) and +3.8..+5 um (cathode).
- Phase shifter length 5 mm, effective doped length 4.5 mm.

## 3. Doping (verified from the .ldev)
Concentrations are listed in both /m^3 (script/API) and /cm^3 (physical).

| Object | Type | Polarity | /m^3 | /cm^3 | x-range | z-range |
|---|---|---|---|---|---|---|
| pepi | Constant Doping | p | 1e21 | 1e15 | -5..5 um | -50..250 nm |
| p implant | Diffusion | p | 7e23 | 7e17 | -6..-0.15 um | -300..90 nm |
| n implant | Diffusion | n | 5e23 | 5e17 | +0.15..6 um | -300..90 nm |
| p wg implant | Diffusion | p | 5e23 | 5e17 | -300..+60 nm | 0..255 nm |
| n wg implant | Diffusion | n | 7e23 | 7e17 | -40..+250 nm | 2.5..237.5 nm |
| p++ | Diffusion | p | 1e25 | 1e19 | -6..-2 um | -300..220 nm |
| n++ | Diffusion | n | 1e25 | 1e19 | +2..6 um | -300..220 nm |

Junction: lateral, approximately at x = 0 (p on x<0, n on x>0).

## 4. Solver configuration
- CHARGE: steady-state DC + small-signal AC (ssac), Fermi statistics, T=300 K,
  norm length 10 mm, mesh min edge 4 nm / max edge 600 nm.
- MODE: FDE 2D-Y-normal, lambda = 1550 nm, 10 trial modes, conformal mesh,
  12 PML layers, 10 nm core mesh override.

## 5. Baseline metrics (simulated)

| Metric | Value | Solver |
|---|---|---|
| neff(0 V) | 2.5671 | MODE |
| ng(0 V) | 3.9364 | MODE |
| loss(0 V) | 498.2 dB/m (4.98 dB/cm) | MODE |
| loss(4 V) | 313.2 dB/m | MODE |
| d neff (0->4 V) | 1.07e-4 | MODE |
| VpiL | 2.90 V.cm | MODE |
| Gamma_core | 0.354 | MODE (screening metric) |
| Gamma_slab | 0.362 | MODE |
| Aeff | 2.056e-13 m^2 | MODE |
| TE fraction | 0.987 | MODE |
| Cj(0 V) | 0.210 fF/um | CHARGE |
| Cj(4 V) | 0.140 fF/um | CHARGE |
| Rslab_total | 0.0159194 (normalized) | CHARGE AC |

Reference targets (project brief): f3dB ~ 15 GHz, ER ~ 4.25 dB at 20 Gb/s / 1 Vpp.

## 6. Validation notes
- The baseline optical results reproduce the previously regenerated
  `tw_modulator_optical_data.mat` to within ~1% in `dneff` and loss.
- A constant ~2.7e-5 offset in absolute `neff` was observed between runs; it does
  not affect `d neff` or loss and is attributed to solver/mesh bookkeeping.
- The second mode (neff ~ 2.115) is a wide-slab mode; the rib is single-mode in
  the vertical direction. The large `Gamma_slab` (0.36) is physical for this
  wide-slab geometry and is the main driver of free-carrier loss.

## 7. Files
- manifest: `baseline_manifest.json`
- metrics: `baseline_metrics.csv`
- charge map: `charge_baseline.mat`
- original project reference: `baseline_project_reference.txt`
