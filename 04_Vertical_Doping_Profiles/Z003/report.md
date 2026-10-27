# Experiment Z003

**Status: SUCCESS**

## Research question
How does the vertical placement/extent of the waveguide implants change confinement-weighted loss and modulation?

## Baseline configuration
- Rib 500 x 130 nm on 90 nm slab (total Si 220 nm), SiO2 cladding.
- Doping: p wg 5e23 /m3 (5e17 cm-3), n wg 7e23 /m3 (7e17 cm-3), p slab 7e23, n slab 5e23, p++/n++ 1e25 /m3 (1e19 cm-3).
- Baseline metrics: neff 2.5671, loss 498.2 dB/m, VpiL 2.908 V.cm, Cj 0.2100 fF/um.

## Modified parameters
| Object | Property | Original | New | Unit (script API) | Region |
|---|---|---:|---:|---|---|
| p wg implant | concentration | 5e+23 | 5e+23 | /m3 (5e+17 /cm3) | rib x -300..+60 nm, z 0..255 nm |
| n wg implant | concentration | 7e+23 | 7e+23 | /m3 (7e+17 /cm3) | rib x -40..+250 nm, z 2.5..237.5 nm |
| p implant | concentration | 7e+23 | 7e+23 | /m3 (7e+17 /cm3) | slab x -6..-0.15 um, z -300..90 nm |
| n implant | concentration | 5e+23 | 5e+23 | /m3 (5e+17 /cm3) | slab x +0.15..6 um, z -300..90 nm |
| p wg implant | z range | baseline | 0.0..110.0 nm | m (script) | vertical profile |
| n wg implant | z range | baseline | 110.0..237.5 nm | m (script) | vertical profile |

**Unit source:** values written through the Lumerical script API are in /m^3. The GUI displays the same concentrations in /cm^3 (1e21 /m^3 = 1e15 /cm^3).

## Physical rationale
The vertical overlap integral weights doping by |E(x,z)|^2. Restricting an implant to a low-field region reduces absorption, at the cost of available depletion charge.

## Objective
Screen vertical-placement variants for a better loss/efficiency point.

## Prediction (hypothesis, not a result)
Pushing doping away from the field maximum lowers loss but weakens modulation. (hypothesis)

## Simulation settings
- Software: Ansys Lumerical 2024 R1 (v241).
- CHARGE: steady state DC, Newton, Fermi statistics, T=300 K, norm length 10 mm.
- Bias grid: [-0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0] V principal, each +0.025 V.
- MODE: FDE 2D Y-normal, 1550 nm, 10 trial modes, conformal mesh, 12 PML, 10 nm core override.
- Requested CHARGE points: 20; completed: 20.

## Convergence evidence
- The sweep is accepted only if all requested points are saved and the final bias is 4.025 V.
- This experiment: **SUCCESS** (20 points).
- Detailed incident analysis: `07_Results/diagnostics/CHARGE_DIAGNOSTIC.md`.

## Raw result files
- `charge.mat` (10413776 bytes)
- `cj_derived.csv` (1522 bytes)
- `optical_metrics.json` (10709 bytes)

## Equations used
- VpiL = lambda/(2|d(dNeff)/dV|), slope over 0->4 V.
- Cj = 0.5(|dQn|+|dQp|)/dV, dV = 0.025 V; F/m converted to fF/um by x1e9.
- Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening overlap).

## Actual results
| Metric | Value |
|---|---:|
| neff (0 V) | 2.567132 |
| ng (0 V) | 3.9365 |
| loss (0 V) | 378.47 dB/m |
| loss (4 V) | 249.27 dB/m |
| d neff (0->4 V) | 8.100e-05 |
| VpiL | 3.842 V.cm |
| Gamma_core (0 V) | 0.354 |
| Gamma_slab (0 V) | 0.362 |
| Aeff (0 V) | 2.056e-13 m^2 |
| TE fraction | 0.9866 |
| Cj (0 V) | 0.1886 fF/um |
| Cj (4 V) | 0.1268 fF/um |

### Bias dependence

| V (V) | neff | loss (dB/m) | d neff | Gamma_core |
|---:|---:|---:|---:|---:|
| -0.500 | 2.567111 | 407.74 | -2.109e-05 | 0.354 |
| -0.475 | 2.567112 | 405.92 | -1.964e-05 | 0.354 |
| 0.000 | 2.567132 | 378.47 | 0.000e+00 | 0.354 |
| 0.025 | 2.567133 | 377.21 | 8.488e-07 | 0.354 |
| 0.500 | 2.567147 | 355.08 | 1.538e-05 | 0.354 |
| 0.525 | 2.567148 | 353.99 | 1.607e-05 | 0.354 |
| 1.000 | 2.567161 | 334.65 | 2.841e-05 | 0.354 |
| 1.025 | 2.567161 | 333.69 | 2.902e-05 | 0.354 |
| 1.500 | 2.567172 | 316.49 | 3.983e-05 | 0.354 |
| 1.525 | 2.567172 | 315.63 | 4.036e-05 | 0.354 |
| 2.000 | 2.567182 | 300.25 | 4.994e-05 | 0.354 |
| 2.025 | 2.567183 | 299.49 | 5.041e-05 | 0.354 |
| 2.500 | 2.567191 | 285.67 | 5.894e-05 | 0.354 |
| 2.525 | 2.567191 | 284.98 | 5.936e-05 | 0.354 |
| 3.000 | 2.567199 | 272.51 | 6.699e-05 | 0.354 |
| 3.025 | 2.567199 | 271.89 | 6.737e-05 | 0.354 |
| 3.500 | 2.567206 | 260.60 | 7.420e-05 | 0.354 |
| 3.525 | 2.567207 | 260.04 | 7.455e-05 | 0.354 |
| 4.000 | 2.567213 | 249.78 | 8.069e-05 | 0.354 |
| 4.025 | 2.567213 | 249.27 | 8.100e-05 | 0.354 |

## Difference from baseline
| Metric | Baseline | This experiment | Change |
|---|---:|---:|---:|
| loss (0 V) | 498.23 dB/m | 378.47 dB/m | -24.0 % |
| VpiL | 2.91 V.cm | 3.842 V.cm | +32.1 % |
| Gamma_core | 0.354 | 0.354 | +0.0 % |
| Cj (0 V) | 0.2100 fF/um | 0.1886 fF/um | -10.2 % |

## Trade-offs and Pareto impact
See `07_Results/pareto_front.csv` and `07_Results/best_designs.csv`; this experiment is included in the multi-objective comparison when all of loss, VpiL, Cj and Gamma_core are available.

## Decision
TRADE-OFF — lower loss but higher VpiL; keep only as a Pareto alternative, not as the balanced finalist.

## Limitations / reproduction
- Gamma_core is a field-overlap screening metric on the FDE output grid, not the exact energy confinement factor.
- Cj is a per-unit-length small-signal value at dv = 0.025 V; it is not the total device capacitance.
- Reproduce with `09_Automation/run_experiment.py Z003` then `09_Automation/extract_metrics.py`.
