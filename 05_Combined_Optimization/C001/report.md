# Experiment C001

**Status: SUCCESS**

## Research question
Do the individually best geometry, doping and junction choices combine without breaking the physical constraints or the performance ranking?

## Baseline configuration
- Rib 500 x 130 nm on 90 nm slab (total Si 220 nm), SiO2 cladding.
- Doping: p wg 5e23 /m3 (5e17 cm-3), n wg 7e23 /m3 (7e17 cm-3), p slab 7e23, n slab 5e23, p++/n++ 1e25 /m3 (1e19 cm-3).
- Baseline metrics: neff 2.5671, loss 498.2 dB/m, VpiL 2.908 V.cm, Cj 0.2100 fF/um.

## Modified parameters
| Object | Property | Original | New | Unit (script API) | Region |
|---|---|---:|---:|---|---|
| p wg implant | concentration | 5e+23 | 1e+24 | /m3 (1e+18 /cm3) | rib x -300..+60 nm, z 0..255 nm |
| n wg implant | concentration | 7e+23 | 1.4e+24 | /m3 (1.4e+18 /cm3) | rib x -40..+250 nm, z 2.5..237.5 nm |
| p implant | concentration | 7e+23 | 1.4e+24 | /m3 (1.4e+18 /cm3) | slab x -6..-0.15 um, z -300..90 nm |
| n implant | concentration | 5e+23 | 1e+24 | /m3 (1e+18 /cm3) | slab x +0.15..6 um, z -300..90 nm |
| rib/slab | slab_nm | baseline | 70.0 nm | geometry | waveguide |

**Unit source:** values written through the Lumerical script API are in /m^3. The GUI displays the same concentrations in /cm^3 (1e21 /m^3 = 1e15 /cm^3).

## Physical rationale
The objective vector is multi-dimensional; the combined candidate tests additivity and interactions of the individual improvements.

## Objective
Produce a combined candidate for finalist validation.

## Prediction (hypothesis, not a result)
Combined changes should preserve the individual loss reduction if the mechanisms are independent. (hypothesis)

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
- `charge.mat` (10783816 bytes)
- `cj_derived.csv` (1507 bytes)
- `optical_metrics.json` (10473 bytes)

## Equations used
- VpiL = lambda/(2|d(dNeff)/dV|), slope over 0->4 V.
- Cj = 0.5(|dQn|+|dQp|)/dV, dV = 0.025 V; F/m converted to fF/um by x1e9.
- Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening overlap).

## Actual results
| Metric | Value |
|---|---:|
| neff (0 V) | 2.532506 |
| ng (0 V) | 3.9976 |
| loss (0 V) | 941.89 dB/m |
| loss (4 V) | 682.89 dB/m |
| d neff (0->4 V) | 1.380e-04 |
| VpiL | 2.257 V.cm |
| Gamma_core (0 V) | 0.435 |
| Gamma_slab (0 V) | 0.266 |
| Aeff (0 V) | 1.998e-13 m^2 |
| TE fraction | 0.9856 |
| Cj (0 V) | 0.2313 fF/um |
| Cj (4 V) | 0.1673 fF/um |

### Bias dependence

| V (V) | neff | loss (dB/m) | d neff | Gamma_core |
|---:|---:|---:|---:|---:|
| -0.500 | 2.532476 | 990.53 | -2.981e-05 | 0.435 |
| -0.475 | 2.532478 | 987.70 | -2.794e-05 | 0.435 |
| 0.000 | 2.532506 | 941.89 | 0.000e+00 | 0.435 |
| 0.025 | 2.532507 | 939.71 | 1.264e-06 | 0.435 |
| 0.500 | 2.532529 | 900.70 | 2.332e-05 | 0.435 |
| 0.525 | 2.532530 | 898.76 | 2.440e-05 | 0.435 |
| 1.000 | 2.532550 | 863.32 | 4.377e-05 | 0.435 |
| 1.025 | 2.532551 | 861.53 | 4.474e-05 | 0.435 |
| 1.500 | 2.532568 | 828.58 | 6.234e-05 | 0.435 |
| 1.525 | 2.532569 | 826.91 | 6.323e-05 | 0.435 |
| 2.000 | 2.532585 | 796.28 | 7.942e-05 | 0.435 |
| 2.025 | 2.532586 | 794.72 | 8.024e-05 | 0.435 |
| 2.500 | 2.532601 | 765.89 | 9.534e-05 | 0.435 |
| 2.525 | 2.532602 | 764.41 | 9.611e-05 | 0.435 |
| 3.000 | 2.532616 | 736.99 | 1.103e-04 | 0.435 |
| 3.025 | 2.532617 | 735.58 | 1.110e-04 | 0.435 |
| 3.500 | 2.532630 | 709.79 | 1.243e-04 | 0.435 |
| 3.525 | 2.532631 | 708.47 | 1.249e-04 | 0.435 |
| 4.000 | 2.532643 | 684.14 | 1.374e-04 | 0.435 |
| 4.025 | 2.532644 | 682.89 | 1.380e-04 | 0.435 |

## Difference from baseline
| Metric | Baseline | This experiment | Change |
|---|---:|---:|---:|
| loss (0 V) | 498.23 dB/m | 941.89 dB/m | +89.0 % |
| VpiL | 2.91 V.cm | 2.257 V.cm | -22.4 % |
| Gamma_core | 0.354 | 0.435 | +23.1 % |
| Cj (0 V) | 0.2100 fF/um | 0.2313 fF/um | +10.2 % |

## Trade-offs and Pareto impact
See `07_Results/pareto_front.csv` and `07_Results/best_designs.csv`; this experiment is included in the multi-objective comparison when all of loss, VpiL, Cj and Gamma_core are available.

## Decision
TRADE-OFF — lower VpiL but higher loss; keep only as a Pareto alternative, not as the balanced finalist.

## Limitations / reproduction
- Gamma_core is a field-overlap screening metric on the FDE output grid, not the exact energy confinement factor.
- Cj is a per-unit-length small-signal value at dv = 0.025 V; it is not the total device capacitance.
- Reproduce with `09_Automation/run_experiment.py C001` then `09_Automation/extract_metrics.py`.
