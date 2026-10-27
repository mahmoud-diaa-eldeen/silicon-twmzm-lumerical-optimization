"""Save a finalist as a runnable layout-only .ldev variant + geometry-matched .lms.

The original files are never modified. The saved .ldev contains the modified
geometry/doping in layout mode (no stale solver results), which keeps it small
and reproducible. Usage:
    python save_finalist.py 05_Combined_Optimization C001
"""
import os, sys, json
import lumapi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from baseline_utils import prepare_session, prepare_mode_session, reset_baseline

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"

fam, exp = sys.argv[1], sys.argv[2]
ed = os.path.join(ROOT, fam, exp)
j = json.load(open(os.path.join(ed, "experiment.json"), encoding="utf-8"))
outdir = os.path.join(ROOT, "06_Final_Validation", exp)
os.makedirs(outdir, exist_ok=True)

W = j.get("W_nm", 500) * 1e-9
ts = j.get("slab_nm", 90) * 1e-9
p = j.get("params", {}) or {}
geo = j.get("geom", {}) or {}

# --- device variant ---
d = lumapi.DEVICE(hide=True)
try:
    ldev = prepare_session()
    d.eval('load("%s");' % ldev)
    d.eval('switchtolayout;')
    reset_baseline(d)
    d.eval('setnamed("::model::geometry::rib","x span",%g);' % W)
    d.eval('setnamed("::model::geometry::rib","z min",%g);' % ts)
    d.eval('setnamed("::model::geometry::slab","z max",%g);' % ts)
    for k, obj in [("p_wg", "p wg implant"), ("n_wg", "n wg implant"),
                   ("p_imp", "p implant"), ("n_imp", "n implant")]:
        if k in p:
            d.eval('setnamed("::model::CHARGE::%s","concentration",%g);' % (obj, p[k]))
    for nm in ("p implant", "n implant"):
        d.eval('setnamed("::model::CHARGE::%s","z max",%g);' % (nm, ts))
    if geo.get("dx"):
        for nm, b in [("p wg implant", -1.2e-7), ("n wg implant", 1.05e-7),
                      ("p implant", -3.075e-6), ("n implant", 3.075e-6)]:
            d.eval('setnamed("::model::CHARGE::%s","x",%g);' % (nm, b + geo["dx"]))
    for side in ("p", "n"):
        if geo.get("zmin_"+side) is not None:
            d.eval('setnamed("::model::CHARGE::%s wg implant","z min",%g);' % (side, geo["zmin_"+side]))
            d.eval('setnamed("::model::CHARGE::%s wg implant","z max",%g);' % (side, geo["zmax_"+side]))
    out = os.path.join(outdir, exp + "_device.ldev")
    d.eval('save("%s");' % out.replace('\\', '/'))
    print("saved", out, os.path.getsize(out))
finally:
    try: d.close()
    except Exception: pass

# --- optical variant ---
m = lumapi.MODE(hide=True)
try:
    lms = prepare_mode_session().replace("\\", "/")
    m.eval('load("%s");' % lms)
    m.eval('switchtolayout;')
    m.eval('setnamed("wg","x span",%g);' % W)
    m.eval('setnamed("wg","z min",%g);' % ts)
    m.eval('setnamed("wg","z max",220e-9);')
    m.eval('setnamed("pad","z min",0);')
    m.eval('setnamed("pad","z max",%g);' % ts)
    m.eval('setnamed("mesh","x span",%g);' % W)
    m.eval('setnamed("mesh","z min",0);')
    m.eval('setnamed("mesh","z max",220e-9);')
    out = os.path.join(outdir, exp + "_optical.lms")
    m.eval('save("%s");' % out.replace('\\', '/'))
    print("saved", out, os.path.getsize(out))
finally:
    try: m.close()
    except Exception: pass
print("FINALIST SAVED")
