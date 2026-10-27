# Final Recommendations

## Recommended design: `J002`

lowest 0 V loss among all individual and combined experiments that satisfy VpiL <= 1.25x baseline and Cj <= 1.25x baseline

| Parameter | Value |
|---|---:|
| Rib width | 500 nm |
| Rib height | 130 nm |
| Slab thickness | 90 nm |
| Total Si thickness | 220 nm |
| Junction shift | 40 nm |
| p wg concentration | 5e+23 /m3 (5e+17 /cm3) |
| n wg concentration | 7e+23 /m3 (7e+17 /cm3) |
| p slab concentration | 7e+23 /m3 (7e+17 /cm3) |
| n slab concentration | 5e+23 /m3 (5e+17 /cm3) |
| Gamma_core (field overlap) | 0.354 |
| neff (0 V) | 2.567032 |
| Optical loss (0 V) | 478.57 dB/m |
| VpiL | 2.692 V.cm |
| Cj (0 V) | 0.2100 fF/um |
| Rs (0 V, 20.0 GHz; 10 mm norm length) | 1.6033 ohm |
| C_ac (0 V, 1 MHz; per um) | 0.2158 fF/um |
| f3dB | NA (distributed RF not simulated) |
| Mesh | conformal, 12 PML, 10 nm core override |
| Convergence | CHARGE 20/20 points; MODE converged |
| vs baseline loss | -3.9 % |
| vs baseline VpiL | -7.4 % |
| vs baseline Cj | +0.0 % |
| vs baseline Gamma_core | -0.0 % |

## Alternatives

| ID | loss (dB/m) | VpiL (V.cm) | Cj (fF/um) | Gamma_core |
|---|---|---|---|---|
| D002 | 120.7 | 5.749 | 0.1689 | 0.3536 |
| C004 | 196.7 | 3.966 | 0.1876 | 0.4352 |
| D001 | 226 | 4.094 | 0.1873 | 0.3536 |
| Z002 | 362.4 | 3.924 | 0.1955 | 0.3536 |
| Z003 | 378.5 | 3.842 | 0.1886 | 0.3536 |

All five lowest-loss alternatives above exceed the 1.25x VpiL screening limit; they are Pareto trade-offs, not balanced picks. These are the same five shown in the full report.

**Near-tie:** J003 (+80 nm) gives loss 479.6 dB/m, VpiL 2.591 V.cm and Cj 0.2095 fF/um. Prefer it only if VpiL/Cj dominate.

## Caveats
- f3dB was not simulated; no bandwidth claim is made.
- Gamma_core is a screening overlap metric.
- Cj is per unit length.
