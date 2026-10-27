# CHARGE Incomplete-Result Diagnostic (D001 / J001 / Z001)

Date: 2026-10-27
Software: Ansys Lumerical 2024 R1 (v241)
Solver: CHARGE, steady state (DC), Newton

## 1. Evidence collected before changing anything

Partial files were archived to `07_Results/diagnostics/partial/` with SHA-256
hashes (`partial_hashes.txt`). Timestamps and sizes:

| Experiment | charge.mat size | V_cathode entries | Last V saved | Next requested V |
|---|---:|---:|---:|---:|
| D001 | 4,964,904 B | 6 | 1.025 V | 2.0 V |
| J001 | 5,024,456 B | 6 | 1.025 V | 2.0 V |
| Z001 | 4,094,056 B | 4 | 0.025 V | 1.0 V |
| D002 | 7,287,872 B | 12 | 4.025 V | - |
| D003 | 7,568,472 B | 12 | 4.025 V | - |
| J002 | 7,432,024 B | 12 | 4.025 V | - |
| Z002 | 7,422,400 B | 12 | 4.025 V | - |

Key observations:
- The requested table was always the same 12-point table
  `[-0.5,-0.475, 0,0.025, 1,1.025, 2,2.025, 3,3.025, 4,4.025]`.
- The saved `V_cathode` arrays are **prefixes** of that table, not a scrambled
  or reordered sequence. No point was overwritten: the missing entries are
  simply absent.
- `run("CHARGE")` returned **without raising an exception** for all three.
- The Python `Cj` line then failed only because it indexed 12 entries.

## 2. What this proves / does not prove

Proved:
- The voltage sequence was constructed correctly (prefix of the intended table).
- Saving is not overwriting previous points.
- The failure is not a Python/API syntax error in the solver call.

Not yet proved at this stage:
- Whether the stopping point was a solver convergence failure, a step-size
  issue, or a result-sizing issue.

## 3. Controlled tests (D001 only)

### Test A — single principal point at 2.0 V, fresh start
- Requested table: `[2.0, 2.025]`.
- Result: **no exception**, 2 charge points saved.
- `Cj(2.0 V) = 0.1259 fF/um`.
- Runtime 282.8 s (includes fresh Poisson/Drift-Diffusion initialisation).

Conclusion: the 2.0 V operating point is solvable. The point itself is not the
problem.

### Test B — full sweep with 0.5 V principal steps
- Requested table: 10 principal points `[-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4]`
  each followed by +0.025 V -> 20 solves.
- Result: **20/20 points saved**, no exception, runtime 340.5 s.
- Derived Cj: 0.2272 fF/um (-0.5 V) -> 0.1744 (0 V) -> 0.0991 (4 V),
  monotonic and physically consistent.

## 4. Root cause

The 0.9 V principal step used in the first batch is too large for the Newton
sweep on some designs. When a bias point fails to converge, CHARGE stops the
sweep and returns the points already solved, **without raising an exception**.
With 0.5 V steps the sweep converges every point. This is consistent with the
original example script, which used ~0.41 V principal steps.

The lumapi interface used here does not expose an explicit per-point
convergence flag. The evidence used is therefore: (i) result availability per
requested point, (ii) the last saved voltage, and (iii) successful completion
of the same points with a finer sweep. This limitation is recorded.

## 5. Fix applied (no tolerance was loosened)

- Principal bias grid: 0.5 V steps, 10 points, each +0.025 V -> 20 solves.
- Cj extracted in Python with explicit length/nan checks, from
  `total_charge` (`Qn=e*pinch(tc.n)`, `Qp=e*pinch(tc.p)`).
- Completion is judged by `n_charge_points == 20` **and** `n_Cj == 10` **and**
  the final saved voltage; never by file size.
- Partial files are archived before any overwrite.

Applied only to D001, J001, Z001 (the failing cases). D002/D003/J002/Z002
already contain the full 12-point table ending at 4.025 V and are retained;
their bias grid is coarser but includes 0 V and 4 V, which are the points used
for VpiL and for the 0 V comparison.
