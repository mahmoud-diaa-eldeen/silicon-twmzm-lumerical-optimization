"""Canonical experiment runner (CHARGE, DC) for the TWMZM study.

Validated settings:
  * bias grid: 0.5 V principal steps, each followed by V+0.025 V (20 solves).
    0.9 V steps were shown to make the Newton sweep stop silently at some
    designs (D001/J001/Z001); 0.5 V steps converge all points.
  * Cj extracted in numpy from total_charge with explicit length checks.
  * completion is judged by result count + final bias, never by file size.
"""
import os, time, json, csv, sys
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

BASE = dict(p_wg=5e23, n_wg=7e23, p_imp=7e23, n_imp=5e23)

EXPS = {
    "D001": dict(params=dict(p_wg=2.5e23, n_wg=3.5e23, p_imp=3.5e23, n_imp=2.5e23),
                 geom={}, desc="channel+slab doping x0.5",
                 family="02_Doping_Sweeps"),
    "D002": dict(params=dict(p_wg=1.5e23, n_wg=2.1e23, p_imp=2.1e23, n_imp=1.5e23),
                 geom={}, desc="channel+slab doping x0.3",
                 family="02_Doping_Sweeps"),
    "D003": dict(params=dict(p_wg=1.0e24, n_wg=1.4e24, p_imp=1.4e24, n_imp=1.0e24),
                 geom={}, desc="channel+slab doping x2.0",
                 family="02_Doping_Sweeps"),
    "J001": dict(params=dict(BASE), geom=dict(dx=-40e-9),
                 desc="junction shift -40 nm", family="03_Junction_Position"),
    "J002": dict(params=dict(BASE), geom=dict(dx=+40e-9),
                 desc="junction shift +40 nm", family="03_Junction_Position"),
    "J003": dict(params=dict(BASE), geom=dict(dx=+80e-9),
                 desc="junction shift +80 nm", family="03_Junction_Position"),
    "Z001": dict(params=dict(BASE), geom=dict(zmin_p=0.0, zmax_p=120e-9,
                                              zmin_n=0.0, zmax_n=120e-9),
                 desc="buried wg implants z=0..120 nm", family="04_Vertical_Doping_Profiles"),
    "Z002": dict(params=dict(BASE), geom=dict(zmin_p=100e-9, zmax_p=220e-9,
                                              zmin_n=100e-9, zmax_n=220e-9),
                 desc="upper wg implants z=100..220 nm", family="04_Vertical_Doping_Profiles"),
    "Z003": dict(params=dict(BASE), geom=dict(zmin_p=0.0, zmax_p=110e-9,
                                              zmin_n=110e-9, zmax_n=237.5e-9),
                 desc="vertically stacked p (0-110 nm) / n (110-237 nm)",
                 family="04_Vertical_Doping_Profiles"),
    # Baseline re-run on the validated fine grid: the earlier baseline charge
    # file started at V=0.4 V (no 0 V point), so its "Cj(0V)" was mislabelled.
    "B000": dict(params=dict(BASE), geom={}, desc="baseline (fine bias grid)",
                 family="00_Original_Baseline"),
}


def charge_meta(path):
    """Return (n_points, V list) from a charge.mat, or (0, [])."""
    try:
        with h5py.File(path, "r") as f:
            if "#refs#" in f and "#v#" in f["#refs#"]:
                v = np.array(f["#refs#/#v#"]).ravel()
                return len(v), v.tolist()
    except Exception:
        pass
    return 0, []


def is_complete(ed):
    cf = os.path.join(ed, "charge.mat")
    if not os.path.exists(cf):
        return False
    n, v = charge_meta(cf)
    if n == 0 or abs(v[-1] - (V0[-1] + DV)) > 1e-6:
        return False
    ej = os.path.join(ed, "experiment.json")
    if os.path.exists(ej):
        try:
            j = json.load(open(ej, encoding="utf-8"))
            if j.get("status") == "SUCCESS":
                return True
        except Exception:
            pass
    # raw data complete even if manifest is old -> accept
    return n >= 2 * len(V0)


def apply_geometry(d, geom):
    dx = geom.get("dx", 0.0)
    if dx:
        for nm, b in [("p wg implant", -1.2e-7), ("n wg implant", 1.05e-7),
                      ("p implant", -3.075e-6), ("n implant", 3.075e-6)]:
            d.eval('setnamed("::model::CHARGE::%s","x",%g);' % (nm, b + dx))
    for side in ("p", "n"):
        zmin = geom.get("zmin_" + side)
        zmax = geom.get("zmax_" + side)
        if zmin is not None:
            d.eval('setnamed("::model::CHARGE::%s wg implant","z min",%g);' % (side, zmin))
        if zmax is not None:
            d.eval('setnamed("::model::CHARGE::%s wg implant","z max",%g);' % (side, zmax))


def run(exp):
    ed = os.path.join(ROOT, EXPS[exp]["family"], exp)
    os.makedirs(ed, exist_ok=True)
    if is_complete(ed):
        print("SKIP complete:", exp, flush=True)
        return
    cf = os.path.join(ed, "charge.mat")
    if os.path.exists(cf):
        import shutil
        shutil.copy2(cf, cf + ".partial_%d" % int(time.time()))
        os.remove(cf)
    spec = EXPS[exp]
    rec = {"exp": exp, "description": spec["desc"], "params": spec["params"],
           "geom": spec["geom"], "bias_grid_V": V0.tolist(), "dv_V": DV,
           "requested_points": NEXP, "solver": "CHARGE steady state",
           "software": "Ansys Lumerical 2024 R1 (v241)", "status": "running"}
    d = lumapi.DEVICE(hide=True)
    t0 = time.time()
    try:
        ldev = prepare_session()
        d.eval('load("%s");' % ldev)
        d.eval('switchtolayout;')
        # hard reset: the session file may carry the previous run's layout
        reset_baseline(d)
        for k, obj in [("p_wg", "p wg implant"), ("n_wg", "n wg implant"),
                       ("p_imp", "p implant"), ("n_imp", "n implant")]:
            d.eval('setnamed("::model::CHARGE::%s","concentration",%g);'
                   % (obj, spec["params"][k]))
        apply_geometry(d, spec["geom"])
        d.eval("setnamed('CHARGE','solver mode','steady state');")
        d.eval("setnamed('CHARGE::boundary conditions::cathode','sweep type','value');")
        d.putv("vdv", vt.reshape(-1, 1))
        d.eval("setnamed('CHARGE::boundary conditions::cathode','value table',vdv);")
        d.eval("setnamed('CHARGE::monitor_charge','save data',1);")
        d.eval("setnamed('CHARGE::monitor_charge','filename','%s');" % cf.replace('\\', '/'))
        print("RUN", exp, spec["desc"], flush=True)
        d.eval('run("CHARGE");')
        d.eval("tc=getresult('CHARGE::monitor','total_charge');")
        d.eval('Qn=e*pinch(tc.n); Qp=e*pinch(tc.p);')
        Qn = np.array(d.getv("Qn")).ravel().astype(float)
        Qp = np.array(d.getv("Qp")).ravel().astype(float)
        rec["n_charge_points"] = int(len(Qn))
        rec["Qn_C_per_m"] = Qn.tolist()
        rec["Qp_C_per_m"] = Qp.tolist()
        nprin = min(len(Qn), len(Qp)) // 2
        Cn = np.abs(Qn[1:2*nprin:2] - Qn[0:2*nprin:2]) / DV
        Cp = np.abs(Qp[1:2*nprin:2] - Qp[0:2*nprin:2]) / DV
        Cj = 0.5 * (Cn + Cp) * 1e15 * 1e-6   # F/m -> fF/um
        rec["Cj_fF_um"] = Cj.tolist()
        rec["n_Cj"] = int(len(Cj))
        rec["V_Cj"] = V0[:len(Cj)].tolist()
        with open(os.path.join(ed, "cj_derived.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["V_principal_V", "Qn_C_per_m", "Qp_C_per_m", "dQn_C_per_m",
                        "dQp_C_per_m", "dV_V", "Cj_F_per_m", "Cj_fF_per_um"])
            for i in range(len(Cj)):
                w.writerow([V0[i], Qn[2*i], Qp[2*i], Cn[i], Cp[i], DV, Cj[i]*1e-9, Cj[i]])
        complete = (rec["n_charge_points"] == NEXP and rec["n_Cj"] == len(V0))
        rec["status"] = "SUCCESS" if complete else "INCOMPLETE"
        rec["runtime_s"] = time.time() - t0
        rec["charge_size"] = os.path.getsize(cf) if os.path.exists(cf) else 0
        print(("OK " if complete else "INCOMPLETE "), exp,
              "points=%d/%d" % (rec["n_charge_points"], NEXP),
              "Cj(0V)=%.4f" % Cj[1], "%.0fs" % (time.time()-t0), flush=True)
    except Exception as e:
        rec["status"] = "FAILED"; rec["error"] = str(e)[:500]
        print("FAIL", exp, str(e)[:300], flush=True)
    finally:
        try: d.close()
        except Exception: pass
    with open(os.path.join(ed, "experiment.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    with open(os.path.join(ROOT, "07_Results", "experiment_registry.csv"), "a", newline="") as f:
        csv.writer(f).writerow([exp, spec["desc"], rec["status"],
                                rec.get("runtime_s", ""), rec.get("charge_size", ""),
                                rec.get("n_charge_points", "")])


if __name__ == "__main__":
    for e in (sys.argv[1:] or list(EXPS)):
        run(e)
    print("RUNNER DONE")
