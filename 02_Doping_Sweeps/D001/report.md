# Experiment D001

**Status: SUCCESS**

## Research question
How does the channel/slab doping concentration change optical loss, modulation efficiency and junction capacitance at fixed geometry?

## Baseline configuration
- Rib 500 x 130 nm on 90 nm slab (total Si 220 nm), SiO2 cladding.
- Doping: p wg 5e23 /m3 (5e17 cm-3), n wg 7e23 /m3 (7e17 cm-3), p slab 7e23, n slab 5e23, p++/n++ 1e25 /m3 (1e19 cm-3).
- Baseline metrics: neff 2.5671, loss 498.2 dB/m, VpiL 2.908 V.cm, Cj 0.2100 fF/um.

## Modified parameters
| Object | Property | Original | New | Unit (script API) | Region |
|---|---|---:|---:|---|---|
| p wg implant | concentration | 5e+23 | 2.5e+23 | /m3 (2.5e+17 /cm3) | rib x -300..+60 nm, z 0..255 nm |
| n wg implant | concentration | 7e+23 | 3.5e+23 | /m3 (3.5e+17 /cm3) | rib x -40..+250 nm, z 2.5..237.5 nm |
| p implant | concentration | 7e+23 | 3.5e+23 | /m3 (3.5e+17 /cm3) | slab x -6..-0.15 um, z -300..90 nm |
| n implant | concentration | 5e+23 | 2.5e+23 | /m3 (2.5e+17 /cm3) | slab x +0.15..6 um, z -300..90 nm |

**Unit source:** values written through the Lumerical script API are in /m^3. The GUI displays the same concentrations in /cm^3 (1e21 /m^3 = 1e15 /cm^3).

## Physical rationale
Free-carrier absorption scales with carrier density (Delta alpha = 8.5e-18 dNe + 6.0e-18 dNh cm^-1), while the depletion charge and dNeff/dV also depend on doping. Lower doping lowers neutral-region absorption but raises series resistance and can lower dNeff/dV.

## Objective
Find a doping level that lowers propagation loss without an unacceptable VpiL penalty.

## Prediction (hypothesis, not a result)
Lower doping -> lower loss and lower Cj, but higher VpiL and higher Rs. (hypothesis)

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
- `charge.mat` (10547280 bytes)
- `cj_derived.csv` (1522 bytes)
- `optical_metrics.json` (10708 bytes)

## Equations used
- VpiL = lambda/(2|d(dNeff)/dV|), slope over 0->4 V.
- Cj = 0.5(|dQn|+|dQp|)/dV, dV = 0.025 V; F/m converted to fF/um by x1e9.
- Gamma_core = integral_core|E|^2 / integral_all|E|^2 (screening overlap).

## Actual results
| Metric | Value |
|---|---:|
| neff (0 V) | 2.567217 |
| ng (0 V) | 3.9365 |
| loss (0 V) | 225.97 dB/m |
| loss (4 V) | 104.88 dB/m |
| d neff (0->4 V) | 7.595e-05 |
| VpiL | 4.094 V.cm |
| Gamma_core (0 V) | 0.354 |
| Gamma_slab (0 V) | 0.362 |
| Aeff (0 V) | 2.056e-13 m^2 |
| TE fraction | 0.9866 |
| Cj (0 V) | 0.1873 fF/um |
| Cj (4 V) | 0.1140 fF/um |

### Bias dependence

| V (V) | neff | loss (dB/m) | d neff | Gamma_core |
|---:|---:|---:|---:|---:|
| -0.500 | 2.567193 | 259.87 | -2.377e-05 | 0.354 |
| -0.475 | 2.567195 | 257.78 | -2.221e-05 | 0.354 |
| 0.000 | 2.567217 | 225.97 | 0.000e+00 | 0.354 |
| 0.025 | 2.567218 | 224.54 | 9.636e-07 | 0.354 |
| 0.500 | 2.567234 | 200.12 | 1.712e-05 | 0.354 |
| 0.525 | 2.567235 | 198.96 | 1.787e-05 | 0.354 |
| 1.000 | 2.567247 | 179.01 | 3.077e-05 | 0.354 |
| 1.025 | 2.567248 | 178.06 | 3.138e-05 | 0.354 |
| 1.500 | 2.567259 | 161.45 | 4.191e-05 | 0.354 |
| 1.525 | 2.567259 | 160.65 | 4.241e-05 | 0.354 |
| 2.000 | 2.567268 | 146.63 | 5.112e-05 | 0.354 |
| 2.025 | 2.567268 | 145.95 | 5.154e-05 | 0.354 |
| 2.500 | 2.567276 | 133.99 | 5.882e-05 | 0.354 |
| 2.525 | 2.567276 | 133.41 | 5.917e-05 | 0.354 |
| 3.000 | 2.567282 | 123.10 | 6.533e-05 | 0.354 |
| 3.025 | 2.567282 | 122.60 | 6.563e-05 | 0.354 |
| 3.500 | 2.567288 | 113.62 | 7.090e-05 | 0.354 |
| 3.525 | 2.567288 | 113.18 | 7.115e-05 | 0.354 |
| 4.000 | 2.567292 | 105.27 | 7.572e-05 | 0.354 |
| 4.025 | 2.567293 | 104.88 | 7.595e-05 | 0.354 |

## Difference from baseline
| Metric | Baseline | This experiment | Change |
|---|---:|---:|---:|
| loss (0 V) | 498.23 dB/m | 225.97 dB/m | -54.6 % |
| VpiL | 2.91 V.cm | 4.094 V.cm | +40.8 % |
| Gamma_core | 0.354 | 0.354 | +0.0 % |
| Cj (0 V) | 0.2100 fF/um | 0.1873 fF/um | -10.8 % |

## Trade-offs and Pareto impact
See `07_Results/pareto_front.csv` and `07_Results/best_designs.csv`; this experiment is included in the multi-objective comparison when all of loss, VpiL, Cj and Gamma_core are available.

## Decision
TRADE-OFF — lower loss but higher VpiL; keep only as a Pareto alternative, not as the balanced finalist.

## Limitations / reproduction
- Gamma_core is a field-overlap screening metric on the FDE output grid, not the exact energy confinement factor.
- Cj is a per-unit-length small-signal value at dv = 0.025 V; it is not the total device capacitance.
- Reproduce with `09_Automation/run_experiment.py D001` then `09_Automation/extract_metrics.py`.
