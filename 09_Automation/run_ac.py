"""Small-signal AC (ssac) for a finalist: R and C_ac vs bias/frequency.

Replicates the original tw_modulator_DEVICE_ac_RC.lsf:
  ssac, cathode range -0.4..4 V, 12 points, R = real(Z) at 0 V and ~20 GHz,
  C_ac = Im(1/Z)/(2*pi*f).
Also applies the finalist geometry/doping from its experiment.json.
"""
import os, sys, json, time
import numpy as np
import lumapi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from baseline_utils import prepare_session, reset_baseline

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
BASE = dict(p_wg=5e23, n_wg=7e23, p_imp=7e23, n_imp=5e23)

fam, exp = sys.argv[1], sys.argv[2]
ed = os.path.join(ROOT, fam, exp)
j = json.load(open(os.path.join(ed, "experiment.json"), encoding="utf-8"))
p = j.get("params", BASE); geo = j.get("geom", {}) or {}
W = j.get("W_nm", 500) * 1e-9
ts = j.get("slab_nm", 90) * 1e-9

out = {"exp": exp, "geometry": {"W_nm": W*1e9, "slab_nm": ts*1e9},
       "params": p, "method": "ssac range -0.4..4 V, 12 points; "
                              "C=Im(1/Z)/(2*pi*f)/norm_length; R=real(Z) at 0 V/20 GHz"}
d = lumapi.DEVICE(hide=True)
t0 = time.time()
try:
    ldev = prepare_session()
    d.eval('load("%s");' % ldev); d.eval('switchtolayout;')
    reset_baseline(d)
    d.eval('setnamed("::model::geometry::rib","x span",%g);' % W)
    d.eval('setnamed("::model::geometry::rib","z min",%g);' % ts)
    d.eval('setnamed("::model::geometry::slab","z max",%g);' % ts)
    for k, obj in [("p_wg", "p wg implant"), ("n_wg", "n wg implant"),
                   ("p_imp", "p implant"), ("n_imp", "n implant")]:
        d.eval('setnamed("::model::CHARGE::%s","concentration",%g);' % (obj, p.get(k, BASE[k])))
    for nm in ("p implant", "n implant"):
        d.eval('setnamed("::model::CHARGE::%s","z max",%g);' % (nm, ts))
    dx = geo.get("dx")
    if dx:
        for nm, b in [("p wg implant", -1.2e-7), ("n wg implant", 1.05e-7),
                      ("p implant", -3.075e-6), ("n implant", 3.075e-6)]:
            d.eval('setnamed("::model::CHARGE::%s","x",%g);' % (nm, b + dx))
    for side in ("p", "n"):
        if geo.get("zmin_"+side) is not None:
            d.eval('setnamed("::model::CHARGE::%s wg implant","z min",%g);' % (side, geo["zmin_"+side]))
            d.eval('setnamed("::model::CHARGE::%s wg implant","z max",%g);' % (side, geo["zmax_"+side]))
    d.eval("setnamed('CHARGE','solver mode','ssac');")
    d.eval("setnamed('CHARGE::boundary conditions::cathode','sweep type','range');")
    d.eval("setnamed('CHARGE::boundary conditions::cathode','range start',-0.4);")
    d.eval("setnamed('CHARGE::boundary conditions::cathode','range stop',4);")
    d.eval("setnamed('CHARGE::boundary conditions::cathode','range num points',12);")
    d.eval("setnamed('CHARGE::monitor_charge','save data',0);")
    print("RUN AC", exp, flush=True)
    d.eval('run("CHARGE");')
    d.eval("R=getresult('CHARGE','ac_cathode');")
    d.eval('Z=0.001/pinch(R.dI);')
    Z = np.array(d.getv("Z"))
    d.eval('Vc=R.V_cathode; f=R.f;')
    Vc = np.array(d.getv("Vc")).ravel()
    f = np.array(d.getv("f")).ravel()
    d.eval("leng=get('norm length');")
    leng = float(np.array(d.getv("leng")).ravel()[0])
    if Z.ndim == 3:
        Z = Z[:, 0, :]
    out["V_cathode"] = Vc.tolist()
    out["f_Hz"] = f.tolist()
    out["Z_shape"] = list(Z.shape)
    out["norm_length_m"] = leng
    omega = 2*np.pi*f
    # Z is the impedance of the norm-length device; divide C by the norm length
    # to obtain F/m (same convention as the original ac_RC.lsf).
    Cac = (1/Z).imag / omega[None, :] / leng
    i0 = int(np.argmin(np.abs(Vc)))
    i20 = int(np.argmin(np.abs(f - 20e9)))
    out["i0"] = i0; out["i20"] = i20
    out["f_at_R_Hz"] = float(f[i20])
    out["R_0V_20GHz_ohm"] = float(Z[i0, i20].real)
    out["C_0V_20GHz_F_per_m"] = float(Cac[i0, i20])
    out["C_0V_1MHz_F_per_m"] = float(Cac[i0, 0])
    out["R_all"] = Z.real.tolist()
    out["C_all"] = Cac.tolist()
    out["status"] = "SUCCESS"
    out["runtime_s"] = time.time()-t0
    print("AC OK", exp, "R(0V,%.1fGHz)=%.4f ohm" % (out["f_at_R_Hz"]/1e9, out["R_0V_20GHz_ohm"]),
          "C(0V,20GHz)=%.4e F/m" % out["C_0V_20GHz_F_per_m"],
          "%.0fs" % out["runtime_s"], flush=True)
except Exception as e:
    out["status"] = "FAILED"; out["error"] = str(e)[:500]
    print("AC FAIL", exp, str(e)[:300], flush=True)
finally:
    try: d.close()
    except Exception: pass
json.dump(out, open(os.path.join(ed, "ac_metrics.json"), "w"), indent=1)
print("DONE")
