# Experiment B000

**Status: SUCCESS**

## Research question
Reference run: reproduce the baseline on the validated fine bias grid.

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

**Unit source:** values written through the Lumerical script API are in /m^3. The GUI displays the same concentrations in /cm^3 (1e21 /m^3 = 1e15 /cm^3).

## Physical rationale
The earlier baseline charge file started at V=0.4 V and therefore had no true 0 V point; its Cj was mislabelled. This run re-establishes the baseline with the same 0.5 V grid used by the optimization experiments.

## Objective
Provide a like-for-like baseline for every comparison.

## Prediction (hypothesis, not a result)
The 0 V Cj should be slightly higher than the 0.4 V value. (hypothesis)

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
- `charge.mat` (10690536 bytes)
- `cj_derived.csv` (1519 bytes)
- `optical_metrics.json` (10737 bytes)

## Equations used
- VpiL = lambda/(2|d(dNeff)/dV|), slope over 0->4 V.
- Cj = 0.5(|dQn|+|dQp|)/dV, dV = 0.025 V; F/m converted to fF/um by x1e9.
- Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening overlap).

## Actual results
| Metric | Value |
|---|---:|
| neff (0 V) | 2.567082 |
| ng (0 V) | 3.9364 |
| loss (0 V) | 498.23 dB/m |
| loss (4 V) | 312.42 dB/m |
| d neff (0->4 V) | 1.070e-04 |
| VpiL | 2.908 V.cm |
| Gamma_core (0 V) | 0.354 |
| Gamma_slab (0 V) | 0.362 |
| Aeff (0 V) | 2.056e-13 m^2 |
| TE fraction | 0.9866 |
| Cj (0 V) | 0.2100 fF/um |
| Cj (4 V) | 0.1398 fF/um |

### Bias dependence

| V (V) | neff | loss (dB/m) | d neff | Gamma_core |
|---:|---:|---:|---:|---:|
| -0.500 | 2.567056 | 538.33 | -2.606e-05 | 0.354 |
| -0.475 | 2.567058 | 535.95 | -2.440e-05 | 0.354 |
| 0.000 | 2.567082 | 498.23 | 0.000e+00 | 0.354 |
| 0.025 | 2.567084 | 496.47 | 1.089e-06 | 0.354 |
| 0.500 | 2.567102 | 465.35 | 1.990e-05 | 0.354 |
| 0.525 | 2.567103 | 463.82 | 2.081e-05 | 0.354 |
| 1.000 | 2.567119 | 436.41 | 3.695e-05 | 0.354 |
| 1.025 | 2.567120 | 435.05 | 3.774e-05 | 0.354 |
| 1.500 | 2.567134 | 410.51 | 5.196e-05 | 0.354 |
| 1.525 | 2.567135 | 409.29 | 5.266e-05 | 0.354 |
| 2.000 | 2.567148 | 387.21 | 6.530e-05 | 0.354 |
| 2.025 | 2.567148 | 386.10 | 6.593e-05 | 0.354 |
| 2.500 | 2.567160 | 366.07 | 7.727e-05 | 0.354 |
| 2.525 | 2.567160 | 365.07 | 7.783e-05 | 0.354 |
| 3.000 | 2.567170 | 346.82 | 8.805e-05 | 0.354 |
| 3.025 | 2.567171 | 345.91 | 8.856e-05 | 0.354 |
| 3.500 | 2.567180 | 329.26 | 9.778e-05 | 0.354 |
| 3.525 | 2.567181 | 328.43 | 9.824e-05 | 0.354 |
| 4.000 | 2.567189 | 313.19 | 1.066e-04 | 0.354 |
| 4.025 | 2.567189 | 312.42 | 1.070e-04 | 0.354 |

## Difference from baseline
| Metric | Baseline | This experiment | Change |
|---|---:|---:|---:|
| loss (0 V) | 498.23 dB/m | 498.23 dB/m | +0.0 % |
| VpiL | 2.91 V.cm | 2.908 V.cm | +0.0 % |
| Gamma_core | 0.354 | 0.354 | -0.0 % |
| Cj (0 V) | 0.2100 fF/um | 0.2100 fF/um | -0.0 % |

## Trade-offs and Pareto impact
See `07_Results/pareto_front.csv` and `07_Results/best_designs.csv`; this experiment is included in the multi-objective comparison when all of loss, VpiL, Cj and Gamma_core are available.

## Decision
REJECT on loss+VpiL; it can still appear on the multi-objective Pareto front through Cj or Gamma_core.

## Limitations / reproduction
- Gamma_core is a field-overlap screening metric on the FDE output grid, not the exact energy confinement factor.
- Cj is a per-unit-length small-signal value at dv = 0.025 V; it is not the total device capacitance.
- Reproduce with `09_Automation/run_experiment.py B000` then `09_Automation/extract_metrics.py`.
