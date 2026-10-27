"""Combined-candidate CHARGE runner (fine bias grid, robust Cj).

Reads a JSON list. Each entry:
  {"exp":"C001","W_nm":500,"slab_nm":70,
   "p_wg":5e23,"n_wg":7e23,"p_imp":7e23,"n_imp":5e23,
   "dx":0,"zmin_p":null,"zmax_p":null,"zmin_n":null,"zmax_n":null,
   "description":"..."}
Geometry is applied to ::model::geometry::rib / slab; slab implants are clipped
to the new slab top so no doping is left floating above the slab.
"""
import os, sys, json, time, csv
import numpy as np
import h5py
import lumapi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from baseline_utils import prepare_session, reset_baseline

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
V0 = np.array([-0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
DV = 0.025
vt = np.empty(2 * len(V0)); vt[0::2] = V0; vt[1::2] = V0 + DV
NEXP = 2 * len(V0)


def complete(ed):
    cf = os.path.join(ed, "charge.mat")
    if not os.path.exists(cf):
        return False
    try:
        with h5py.File(cf, "r") as f:
            v = np.array(f["#refs#/#v#"]).ravel()
        return len(v) == NEXP and abs(v[-1] - (V0[-1] + DV)) < 1e-6
    except Exception:
        return False


cfg = json.load(open(sys.argv[1], encoding="utf-8"))
for c in cfg:
    exp = c["exp"]
    ed = os.path.join(ROOT, "05_Combined_Optimization", exp)
    os.makedirs(ed, exist_ok=True)
    if complete(ed):
        print("SKIP complete:", exp, flush=True); continue
    cf = os.path.join(ed, "charge.mat")
    if os.path.exists(cf):
        import shutil
        shutil.copy2(cf, cf + ".partial_%d" % int(time.time()))
        os.remove(cf)
    W = c.get("W_nm", 500) * 1e-9
    ts = c.get("slab_nm", 90) * 1e-9
    p = {k: c.get(k, BASE) for k, BASE in
         [("p_wg", 5e23), ("n_wg", 7e23), ("p_imp", 7e23), ("n_imp", 5e23)]}
    rec = {"exp": exp, "description": c.get("description", "combined"),
           "W_nm": c.get("W_nm", 500), "slab_nm": c.get("slab_nm", 90),
           "params": p, "geom": {k: c.get(k) for k in
                                 ("dx", "zmin_p", "zmax_p", "zmin_n", "zmax_n")},
           "bias_grid_V": V0.tolist(), "dv_V": DV, "requested_points": NEXP,
           "solver": "CHARGE steady state",
           "software": "Ansys Lumerical 2024 R1 (v241)", "status": "running"}
    d = lumapi.DEVICE(hide=True)
    t0 = time.time()
    try:
        ldev = prepare_session()
        d.eval('load("%s");' % ldev); d.eval('switchtolayout;')
        reset_baseline(d)
        d.eval('setnamed("::model::geometry::rib","x span",%g);' % W)
        d.eval('setnamed("::model::geometry::rib","z min",%g);' % ts)
        d.eval('setnamed("::model::geometry::slab","z max",%g);' % ts)
        d.eval('setnamed("::model::CHARGE::p wg implant","concentration",%g);' % p["p_wg"])
        d.eval('setnamed("::model::CHARGE::n wg implant","concentration",%g);' % p["n_wg"])
        d.eval('setnamed("::model::CHARGE::p implant","concentration",%g);' % p["p_imp"])
        d.eval('setnamed("::model::CHARGE::n implant","concentration",%g);' % p["n_imp"])
        # clip slab implants to the new slab top
        for nm in ("p implant", "n implant"):
            d.eval('setnamed("::model::CHARGE::%s","z max",%g);' % (nm, ts))
        dx = c.get("dx")
        if dx:
            for nm, b in [("p wg implant", -1.2e-7), ("n wg implant", 1.05e-7),
                          ("p implant", -3.075e-6), ("n implant", 3.075e-6)]:
                d.eval('setnamed("::model::CHARGE::%s","x",%g);' % (nm, b + dx))
        for side in ("p", "n"):
            zmin = c.get("zmin_" + side); zmax = c.get("zmax_" + side)
            if zmin is not None:
                d.eval('setnamed("::model::CHARGE::%s wg implant","z min",%g);' % (side, zmin))
            if zmax is not None:
                d.eval('setnamed("::model::CHARGE::%s wg implant","z max",%g);' % (side, zmax))
        d.eval("setnamed('CHARGE','solver mode','steady state');")
        d.eval("setnamed('CHARGE::boundary conditions::cathode','sweep type','value');")
        d.putv("vdv", vt.reshape(-1, 1))
        d.eval("setnamed('CHARGE::boundary conditions::cathode','value table',vdv);")
        d.eval("setnamed('CHARGE::monitor_charge','save data',1);")
        d.eval("setnamed('CHARGE::monitor_charge','filename','%s');" % cf.replace('\\', '/'))
        print("RUN", exp, rec["description"], flush=True)
        d.eval('run("CHARGE");')
        d.eval("tc=getresult('CHARGE::monitor','total_charge');")
        d.eval('Qn=e*pinch(tc.n); Qp=e*pinch(tc.p);')
        Qn = np.array(d.getv("Qn")).ravel().astype(float)
        Qp = np.array(d.getv("Qp")).ravel().astype(float)
        rec["n_charge_points"] = int(len(Qn))
        rec["Qn_C_per_m"] = Qn.tolist(); rec["Qp_C_per_m"] = Qp.tolist()
        nprin = min(len(Qn), len(Qp)) // 2
        Cn = np.abs(Qn[1:2*nprin:2] - Qn[0:2*nprin:2]) / DV
        Cp = np.abs(Qp[1:2*nprin:2] - Qp[0:2*nprin:2]) / DV
        Cj = 0.5 * (Cn + Cp) * 1e15 * 1e-6
        rec["Cj_fF_um"] = Cj.tolist(); rec["n_Cj"] = int(len(Cj))
        rec["V_Cj"] = V0[:len(Cj)].tolist()
        with open(os.path.join(ed, "cj_derived.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["V_principal_V", "Qn_C_per_m", "Qp_C_per_m", "dQn_C_per_m",
                        "dQp_C_per_m", "dV_V", "Cj_F_per_m", "Cj_fF_per_um"])
            for i in range(len(Cj)):
                w.writerow([V0[i], Qn[2*i], Qp[2*i], Cn[i], Cp[i], DV, Cj[i]*1e-9, Cj[i]])
        ok = (rec["n_charge_points"] == NEXP and rec["n_Cj"] == len(V0))
        rec["status"] = "SUCCESS" if ok else "INCOMPLETE"
        rec["runtime_s"] = time.time() - t0
        rec["charge_size"] = os.path.getsize(cf) if os.path.exists(cf) else 0
        print(("OK " if ok else "INCOMPLETE "), exp,
              "points=%d/%d" % (rec["n_charge_points"], NEXP),
              "Cj0=%.4f" % Cj[1], "%.0fs" % (time.time()-t0), flush=True)
    except Exception as e:
        rec["status"] = "FAILED"; rec["error"] = str(e)[:500]
        print("FAIL", exp, str(e)[:300], flush=True)
    finally:
        try: d.close()
        except Exception: pass
    with open(os.path.join(ed, "experiment.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
print("COMBINED DONE")
