# Experiment J002

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
| p/n wg + slab implants | x position | 0 | +40 nm | m (script) | junction shift |

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
- `charge.mat` (10653968 bytes)
- `cj_derived.csv` (1512 bytes)
- `optical_metrics.json` (10706 bytes)

## Equations used
- VpiL = lambda/(2|d(dNeff)/dV|), slope over 0->4 V.
- Cj = 0.5(|dQn|+|dQp|)/dV, dV = 0.025 V; F/m converted to fF/um by x1e9.
- Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening overlap).

## Actual results
| Metric | Value |
|---|---:|
| neff (0 V) | 2.567032 |
| ng (0 V) | 3.9363 |
| loss (0 V) | 478.57 dB/m |
| loss (4 V) | 300.93 dB/m |
| d neff (0->4 V) | 1.156e-04 |
| VpiL | 2.692 V.cm |
| Gamma_core (0 V) | 0.354 |
| Gamma_slab (0 V) | 0.362 |
| Aeff (0 V) | 2.056e-13 m^2 |
| TE fraction | 0.9866 |
| Cj (0 V) | 0.2100 fF/um |
| Cj (4 V) | 0.1398 fF/um |

### Bias dependence

| V (V) | neff | loss (dB/m) | d neff | Gamma_core |
|---:|---:|---:|---:|---:|
| -0.500 | 2.567005 | 516.79 | -2.698e-05 | 0.354 |
| -0.475 | 2.567007 | 514.52 | -2.528e-05 | 0.354 |
| 0.000 | 2.567032 | 478.57 | 0.000e+00 | 0.354 |
| 0.025 | 2.567033 | 476.88 | 1.140e-06 | 0.354 |
| 0.500 | 2.567053 | 447.17 | 2.095e-05 | 0.354 |
| 0.525 | 2.567054 | 445.71 | 2.192e-05 | 0.354 |
| 1.000 | 2.567071 | 419.55 | 3.907e-05 | 0.354 |
| 1.025 | 2.567072 | 418.25 | 3.992e-05 | 0.354 |
| 1.500 | 2.567087 | 394.80 | 5.516e-05 | 0.354 |
| 1.525 | 2.567088 | 393.63 | 5.592e-05 | 0.354 |
| 2.000 | 2.567102 | 372.48 | 6.961e-05 | 0.354 |
| 2.025 | 2.567102 | 371.42 | 7.030e-05 | 0.354 |
| 2.500 | 2.567115 | 352.26 | 8.266e-05 | 0.354 |
| 2.525 | 2.567115 | 351.30 | 8.328e-05 | 0.354 |
| 3.000 | 2.567127 | 333.85 | 9.451e-05 | 0.354 |
| 3.025 | 2.567127 | 332.98 | 9.508e-05 | 0.354 |
| 3.500 | 2.567137 | 317.05 | 1.053e-04 | 0.354 |
| 3.525 | 2.567138 | 316.25 | 1.058e-04 | 0.354 |
| 4.000 | 2.567147 | 301.66 | 1.152e-04 | 0.354 |
| 4.025 | 2.567148 | 300.93 | 1.156e-04 | 0.354 |

## Difference from baseline
| Metric | Baseline | This experiment | Change |
|---|---:|---:|---:|
| loss (0 V) | 498.23 dB/m | 478.57 dB/m | -3.9 % |
| VpiL | 2.91 V.cm | 2.692 V.cm | -7.4 % |
| Gamma_core | 0.354 | 0.354 | -0.0 % |
| Cj (0 V) | 0.2100 fF/um | 0.2100 fF/um | +0.0 % |

## Trade-offs and Pareto impact
See `07_Results/pareto_front.csv` and `07_Results/best_designs.csv`; this experiment is included in the multi-objective comparison when all of loss, VpiL, Cj and Gamma_core are available.

## Decision
KEEP — improves both loss and VpiL vs baseline.

## Limitations / reproduction
- Gamma_core is a field-overlap screening metric on the FDE output grid, not the exact energy confinement factor.
- Cj is a per-unit-length small-signal value at dv = 0.025 V; it is not the total device capacitance.
- Reproduce with `09_Automation/run_experiment.py J002` then `09_Automation/extract_metrics.py`.
