"""Baseline reset helpers and the single working copy of the DEVICE project.

IMPORTANT INCIDENT (2026-10-27): the first batch loaded the original
`D:/lumerical/tw_modulator_DEVICE.ldev`, and Lumerical saved the modified
project back to that path when the session closed. As a result the original
file no longer contains the pristine layout, and later runs inherited the
previous run's geometry (junction shift + vertical stacking).

Fix: a pristine master layout was reconstructed from baseline_manifest.json as
`00_Original_Baseline/tw_modulator_DEVICE_pristine.ldev` (3.4 MB, layout only).
Every run MUST:
  1. copy the pristine master to a disposable session file,
  2. load the session file (never the master, never D:/lumerical),
  3. call reset_baseline() before applying the experiment's own changes.
The session file is allowed to be overwritten by Lumerical's save-on-run.
See 07_Results/diagnostics/PROJECT_FILE_INCIDENT.md.
"""
import os
import shutil

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
DEVICE_PRISTINE = os.path.join(ROOT, "00_Original_Baseline",
                               "tw_modulator_DEVICE_pristine.ldev")
DEVICE_SESSION = os.path.join(ROOT, "00_Original_Baseline",
                              "tw_modulator_DEVICE_session.ldev")
MODE_LMS = "D:/lumerical/tw_modulator_optical_MODE.lms"
MODE_SESSION = os.path.join(ROOT, "00_Original_Baseline",
                            "tw_modulator_optical_MODE_session.lms")


def prepare_mode_session():
    """Copy the original MODE project to a disposable session file.

    The original .lms is only read; any in-memory geometry change and the final
    save go through this copy (same policy as the DEVICE .ldev).
    """
    shutil.copy2(MODE_LMS, MODE_SESSION)
    return MODE_SESSION

# Baseline values read from 00_Original_Baseline/baseline_manifest.json.
# "x" is the object centre (rectangle centre) used by the Lumerical API.
BASELINE_DOPING = {
    "p wg implant": dict(x=-1.2e-7, zmin=0.0, zmax=2.55e-7, c=5e23, jw=1.2e-7),
    "n wg implant": dict(x=1.05e-7, zmin=2.5e-9, zmax=2.375e-7, c=7e23, jw=1.1e-7),
    "p implant": dict(x=-3.075e-6, zmin=-3e-7, zmax=9e-8, c=7e23, jw=1e-7),
    "n implant": dict(x=3.075e-6, zmin=-3e-7, zmax=9e-8, c=5e23, jw=1e-7),
}

BASELINE_GEOMETRY = dict(rib_w=5e-7, rib_zmin=9e-8, rib_zmax=2.2e-7,
                         slab_zmax=9e-8)


def prepare_session():
    """Copy the pristine master to a disposable session file; return its path."""
    if not os.path.exists(DEVICE_PRISTINE):
        raise RuntimeError("pristine master missing: " + DEVICE_PRISTINE)
    shutil.copy2(DEVICE_PRISTINE, DEVICE_SESSION)
    return DEVICE_SESSION.replace("\\", "/")


def reset_baseline(d):
    """Reset every object this study can modify to its baseline value."""
    g = BASELINE_GEOMETRY
    d.eval('setnamed("::model::geometry::rib","x span",%g);' % g["rib_w"])
    d.eval('setnamed("::model::geometry::rib","z min",%g);' % g["rib_zmin"])
    d.eval('setnamed("::model::geometry::rib","z max",%g);' % g["rib_zmax"])
    d.eval('setnamed("::model::geometry::slab","z max",%g);' % g["slab_zmax"])
    for obj, v in BASELINE_DOPING.items():
        d.eval('setnamed("::model::CHARGE::%s","x",%g);' % (obj, v["x"]))
        d.eval('setnamed("::model::CHARGE::%s","z min",%g);' % (obj, v["zmin"]))
        d.eval('setnamed("::model::CHARGE::%s","z max",%g);' % (obj, v["zmax"]))
        d.eval('setnamed("::model::CHARGE::%s","concentration",%g);' % (obj, v["c"]))
        d.eval('setnamed("::model::CHARGE::%s","junction width",%g);' % (obj, v["jw"]))
