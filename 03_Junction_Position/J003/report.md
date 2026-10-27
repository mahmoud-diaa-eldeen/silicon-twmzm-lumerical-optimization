# Experiment J003

**Status: SUCCESS**

## Research question
How does the lateral junction position relative to the optical-mode maximum change loss and modulation efficiency?

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
| p/n wg + slab implants | x position | 0 | +80 nm | m (script) | junction shift |

**Unit source:** values written through the Lumerical script API are in /m^3. The GUI displays the same concentrations in /cm^3 (1e21 /m^3 = 1e15 /cm^3).

## Physical rationale
dNeff(V)=integral dN(x,z,V)|E|^2 dA. Shifting the junction changes the overlap of the depletion region (useful index change) and of the neutral doped regions (absorption) with |E|^2.

## Objective
Test both shift directions and look for a loss/efficiency optimum near the mode peak.

## Prediction (hypothesis, not a result)
Moving the junction away from the mode peak lowers loss but also lowers dNeff; a trade-off is expected. (hypothesis)

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
- `charge.mat` (10646784 bytes)
- `cj_derived.csv` (1517 bytes)
- `optical_metrics.json` (10726 bytes)

## Equations used
- VpiL = lambda/(2|d(dNeff)/dV|), slope over 0->4 V.
- Cj = 0.5(|dQn|+|dQp|)/dV, dV = 0.025 V; F/m converted to fF/um by x1e9.
- Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening overlap).

## Actual results
| Metric | Value |
|---|---:|
| neff (0 V) | 2.566976 |
| ng (0 V) | 3.9362 |
| loss (0 V) | 479.58 dB/m |
| loss (4 V) | 314.51 dB/m |
| d neff (0->4 V) | 1.202e-04 |
| VpiL | 2.591 V.cm |
| Gamma_core (0 V) | 0.354 |
| Gamma_slab (0 V) | 0.362 |
| Aeff (0 V) | 2.056e-13 m^2 |
| TE fraction | 0.9866 |
| Cj (0 V) | 0.2095 fF/um |
| Cj (4 V) | 0.1380 fF/um |

### Bias dependence

| V (V) | neff | loss (dB/m) | d neff | Gamma_core |
|---:|---:|---:|---:|---:|
| -0.500 | 2.566949 | 514.42 | -2.660e-05 | 0.354 |
| -0.475 | 2.566951 | 512.36 | -2.495e-05 | 0.354 |
| 0.000 | 2.566976 | 479.58 | 0.000e+00 | 0.354 |
| 0.025 | 2.566977 | 478.04 | 1.139e-06 | 0.354 |
| 0.500 | 2.566997 | 450.77 | 2.107e-05 | 0.354 |
| 0.525 | 2.566998 | 449.43 | 2.205e-05 | 0.354 |
| 1.000 | 2.567015 | 425.29 | 3.951e-05 | 0.354 |
| 1.025 | 2.567016 | 424.08 | 4.038e-05 | 0.354 |
| 1.500 | 2.567032 | 402.36 | 5.607e-05 | 0.354 |
| 1.525 | 2.567033 | 401.28 | 5.686e-05 | 0.354 |
| 2.000 | 2.567047 | 381.59 | 7.112e-05 | 0.354 |
| 2.025 | 2.567048 | 380.60 | 7.183e-05 | 0.354 |
| 2.500 | 2.567061 | 362.68 | 8.485e-05 | 0.354 |
| 2.525 | 2.567061 | 361.78 | 8.551e-05 | 0.354 |
| 3.000 | 2.567073 | 345.43 | 9.744e-05 | 0.354 |
| 3.025 | 2.567074 | 344.60 | 9.804e-05 | 0.354 |
| 3.500 | 2.567085 | 329.65 | 1.090e-04 | 0.354 |
| 3.525 | 2.567086 | 328.89 | 1.096e-04 | 0.354 |
| 4.000 | 2.567096 | 315.20 | 1.196e-04 | 0.354 |
| 4.025 | 2.567096 | 314.51 | 1.202e-04 | 0.354 |

## Difference from baseline
| Metric | Baseline | This experiment | Change |
|---|---:|---:|---:|
| loss (0 V) | 498.23 dB/m | 479.58 dB/m | -3.7 % |
| VpiL | 2.91 V.cm | 2.591 V.cm | -10.9 % |
| Gamma_core | 0.354 | 0.354 | -0.0 % |
| Cj (0 V) | 0.2100 fF/um | 0.2095 fF/um | -0.3 % |

## Trade-offs and Pareto impact
See `07_Results/pareto_front.csv` and `07_Results/best_designs.csv`; this experiment is included in the multi-objective comparison when all of loss, VpiL, Cj and Gamma_core are available.

## Decision
KEEP — improves both loss and VpiL vs baseline.

## Limitations / reproduction
- Gamma_core is a field-overlap screening metric on the FDE output grid, not the exact energy confinement factor.
- Cj is a per-unit-length small-signal value at dv = 0.025 V; it is not the total device capacitance.
- Reproduce with `09_Automation/run_experiment.py J003` then `09_Automation/extract_metrics.py`.
