# Equations and Assumptions

All quantities are evaluated in SI unless stated. Lumerical-native results are
preferred; analytical expressions are used for screening and cross-checks only.

## 1. Propagation constant
beta = k0 * neff,  k0 = 2*pi/lambda
- beta [rad/m], lambda [m], neff complex.
- Used to convert the complex modal index to loss.

## 2. Loss convention (verified against solver output)
Lumerical MODE reports `loss` in dB/m directly. For cross-check:
  alpha_power = 2*|Im(beta)|      [1/m]
  alpha_dBm   = 4.343 * alpha_power = 8.686*|Im(beta)|
- We use the native `loss` result as primary and this expression as a check.
- Assumption: exp(-alpha_power z) power decay. Confirmed: loss_0V =
  8.686*|Im(beta)| with Im(beta)=1.415e-5 -> 8.686*1.415e-5*1e6? No:
  Im(neff)=1.415e-5, k0=4.05e6 /m, Im(beta)=k0*Im(neff)=57.3 /m,
  loss=8.686*57.3=498 dB/m. Matches native 498.2 dB/m. Convention verified.

## 3. Field-overlap (confinement) metric
Gamma_region = integral_region |E|^2 dA / integral_all |E|^2 dA
with |E|^2 = |Ex|^2+|Ey|^2+|Ez|^2 on the FDE output grid.
- This is a field-overlap metric, not the exact electromagnetic energy
  confinement factor (which would use epsilon-weighted energy density).
- Integration uses trapezoidal rule on the actual (possibly non-uniform) x,z grid.
- Regions: core = |x| <= W/2 and z_slab <= z <= 220 nm;
  slab = |x| <= 2.5 um and 0 <= z < z_slab.
- Used for screening only. Final ranking uses native loss and d neff.

## 4. Effective mode area
Native `mode effective area` from Lumerical is reported. The scalar
approximation Aeff = (integral |E|^2)^2 / integral |E|^4 is not used as a
primary metric because the mode is strongly vectorial.

## 5. Free-carrier plasma dispersion (screening context)
Soref-Bennett at 1.55 um, carrier densities in cm^-3:
  d n = -[8.8e-22 dNe + 8.5e-18 (dNh)^0.8]
  d alpha = 8.5e-18 dNe + 6.0e-18 dNh   [1/cm]
- Empirical; used to interpret trends, NOT to replace the native
  Lumerical silicon_np material model (which is used for all reported neff/loss).

## 6. Effective-index modulation
d neff(V) = neff(V) - neff(Vref), Vref = 0 V.
Both real (phase) and imaginary (loss) parts are tracked.

## 7. Phase shift and VpiL
d phi = (2*pi/lambda) * d neff * L
VpiL = lambda / (2 * |d(d neff)/dV|)        [V*m]
- Single-arm convention, as used in the original example.
- Slope evaluated over 0 -> 4 V from the simulated curve (not a single bias).
- Reported in V.cm (x100).

## 8. Junction capacitance
Cj = |dQ/dV|, evaluated as a centred finite difference on adjacent samples:
  Cj(V_i) = 0.5*(|Qn(V_i+dv)-Qn(V_i)| + |Qp(V_i+dv)-Qp(V_i)|)/dv,  dv = 0.025 V.
- Q from the integrated terminal charge (`CHARGE::monitor`, integrate total
  charge = 1). The monitor is a 2D y-normal monitor, so the result is charge
  per unit length along the waveguide: Q' [C/m].
- Cn = |dQn/dV| therefore has units F/m. Conversion used:
  1 F/m = 1e15 fF / 1e6 um = 1e9 fF/um, hence Cj[fF/um] = Cj[F/m]*1e9,
  implemented as `0.5*(Cn+Cp)*1e15*1e-6`.
- 1 fF/um = 1 pF/mm. The baseline 0.21 fF/um = 0.21 pF/mm is the
  capacitance per unit length, not the total device capacitance.
- Order-of-magnitude check: for a lateral junction, C' ~ eps_Si*H/Wdep.
  With H ~ 220 nm, Wdep ~ 60 nm, eps_Si = 1.04e-10 F/m -> ~0.38 pF/mm,
  same order as the extracted 0.21 pF/mm (the difference is the graded
  transition and the finite rib height).
- The normalization is per unit length. Total capacitance for a phase-shifter
  length L is C_total = Cj * L; it is not reported as a single device value
  because the RF model uses distributed (per-length) quantities.

## 8b. Bias grid and convergence
- Screening grid: V = [-0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4] V, each
  followed by V + 0.025 V (20 solves).
- A coarser 0.9 V principal step made the Newton sweep stop silently for some
  designs (D001/J001/Z001); the point itself was solvable (verified at 2.0 V).
  See `07_Results/diagnostics/CHARGE_DIAGNOSTIC.md`.
- No convergence tolerance was loosened; only the sweep step was refined.

## 8c. Baseline reconstruction and validation
- The recorded baseline loss (498.22 dB/m) was computed from the original
  25,271-point charge mesh shipped with the project.
- Re-running the reconstructed pristine layout on the validated 20-point grid
  gives **498.23 dB/m at 0 V** (1-based `V_cathode_index = 3`), i.e. it
  reproduces the recorded baseline to 0.01 dB/m.
- neff (2.567082 vs 2.567082), ng (3.936389 vs 3.936389), Gamma_core (0.354 vs
  0.354), Aeff (2.056e-13 m^2) and Cj(0 V) (0.2100 vs 0.2100 fF/um) also match.
  There is **no mesh-regeneration offset** beyond 0.01 dB/m.
- The value 535.95 dB/m that appeared in an earlier check is the **-0.475 V**
  point (`V_cathode_index = 2`), not 0 V.  The final extraction uses index 3.
- All new CHARGE+MODE experiments are compared to the validated **B000 0 V
  baseline** (loss 498.23 dB/m, same mesh and pipeline).
- The geometry screening is MODE-only at 0 V; its G000 case reproduces the B000
  baseline (498.2 dB/m), so it is directly comparable with the CHARGE+MODE
  experiments.

## 8d. f3dB
- f3dB is **NA** in this study: the distributed travelling-wave RF model was
  not re-run. The ssac result gives Rs and C_ac per unit length at 0 V /
  20 GHz for the finalists.
- A lumped 1/(2*pi*Rs*C) number is deliberately **not** presented as f3dB,
  because it ignores the distributed electrode/waveguide interaction and the
  velocity mismatch.


## 9. Series resistance
Extracted by the original ac_RC workflow: R = real(Z) from the small-signal
admittance, written as `Rslab_total` and split equally between the two sides in
the RF model. No constant-resistivity approximation is assumed.

## 10. RC bandwidth (screening only)
f_RC = 1/(2*pi*R*C)
- Screening only; the real bandwidth is set by the traveling-wave response
  (RF loss, velocity mismatch, impedance). Not used as a final result.

## 11. Objective vector and Pareto rule
Minimize: alpha_opt, VpiL, Cj, Rs.
Maximize: Gamma_core, f3dB (f3dB only when validly simulated).
- In the sweep, Rs is **NA** (ssac is run only for the finalists) and f3dB is
  **NA** (the distributed RF model is not re-run). The reported Pareto front is
  therefore computed on (loss, VpiL, Cj, Gamma_core); Rs is discussed only for
  the finalist where it is actually extracted.
- Pareto dominance: candidate A dominates B if A is at least as good in every
  objective and strictly better in at least one.
- No invented pass/fail thresholds. Relative improvement vs baseline:
  improvement_min = 100*(base - cand)/|base|
  improvement_max = 100*(cand - base)/|base|
