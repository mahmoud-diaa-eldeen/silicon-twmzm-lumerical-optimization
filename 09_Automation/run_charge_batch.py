import os, time, json, csv, sys
import numpy as np
import lumapi

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
LDEV = "D:/lumerical/tw_modulator_DEVICE.ldev"
V0 = np.array([-0.5, 0.0, 1.0, 2.0, 3.0, 4.0])
DV = 0.025
vt = np.empty(2*len(V0)); vt[0::2] = V0; vt[1::2] = V0 + DV

BASE = dict(
    p_wg=5e23, n_wg=7e23, p_imp=7e23, n_imp=5e23,
)

def mods_for(exp):
    """return dict of object->props, and description"""
    p = dict(BASE)
    if exp == "D001":
        p.update(p_wg=2.5e23, n_wg=3.5e23, p_imp=3.5e23, n_imp=2.5e23)
        return p, {}, "scale channel+slab doping x0.5"
    if exp == "D002":
        p.update(p_wg=1.5e23, n_wg=2.1e23, p_imp=2.1e23, n_imp=1.5e23)
        return p, {}, "scale channel+slab doping x0.3"
    if exp == "D003":
        p.update(p_wg=1.0e24, n_wg=1.4e24, p_imp=1.4e24, n_imp=1.0e24)
        return p, {}, "scale channel+slab doping x2.0"
    if exp in ("J001", "J002"):
        dx = -40e-9 if exp == "J001" else 40e-9
        return p, {"dx": dx}, "shift junction dx=%+dnm" % (dx*1e9)
    if exp == "Z001":
        return p, {"zmin": 0.0, "zmax": 120e-9}, "wg implants buried z=0..120nm"
    if exp == "Z002":
        return p, {"zmin": 100e-9, "zmax": 220e-9}, "wg implants upper z=100..220nm"
    return p, {}, "baseline"

EXPS = sys.argv[1:] if len(sys.argv) > 1 else ["D001","D002","D003","J001","J002","Z001","Z002"]

def expdir(exp):
    fam = {"D":"02_Doping_Sweeps","J":"03_Junction_Position","Z":"04_Vertical_Doping_Profiles"}[exp[0]]
    return os.path.join(ROOT, fam, exp)

for exp in EXPS:
    ed = expdir(exp); os.makedirs(ed, exist_ok=True)
    chargefile = os.path.join(ed, "charge.mat")
    if os.path.exists(chargefile) and os.path.getsize(chargefile) > 1e6:
        print("SKIP (exists):", exp, flush=True); continue
    p, geo, desc = mods_for(exp)
    t0 = time.time()
    d = lumapi.DEVICE(hide=True)
    rec = {"exp": exp, "description": desc, "params": p, "geom": geo, "status": "running"}
    try:
        d.eval('load("%s");' % LDEV)
        d.eval('switchtolayout;')
        # concentrations
        d.eval('setnamed("::model::CHARGE::p wg implant","concentration",%g);' % p["p_wg"])
        d.eval('setnamed("::model::CHARGE::n wg implant","concentration",%g);' % p["n_wg"])
        d.eval('setnamed("::model::CHARGE::p implant","concentration",%g);' % p["p_imp"])
        d.eval('setnamed("::model::CHARGE::n implant","concentration",%g);' % p["n_imp"])
        if "dx" in geo:
            dx = geo["dx"]
            for nm, base in [("p wg implant",-1.2e-7),("n wg implant",1.05e-7),
                             ("p implant",-3.075e-6),("n implant",3.075e-6)]:
                d.eval('setnamed("::model::CHARGE::%s","x",%g);' % (nm, base+dx))
        if "zmin" in geo:
            for nm in ["n wg implant","p wg implant"]:
                d.eval('setnamed("::model::CHARGE::%s","z min",%g);' % (nm, geo["zmin"]))
                d.eval('setnamed("::model::CHARGE::%s","z max",%g);' % (nm, geo["zmax"]))
        # sweep
        d.eval("setnamed('CHARGE','solver mode','steady state');")
        d.eval("setnamed('CHARGE::boundary conditions::cathode','sweep type','value');")
        d.putv("vdv", vt.reshape(-1,1))
        d.eval("setnamed('CHARGE::boundary conditions::cathode','value table',vdv);")
        d.eval("setnamed('CHARGE::monitor_charge','save data',1);")
        d.eval("setnamed('CHARGE::monitor_charge','filename','%s');" % chargefile.replace('\\','/'))
        print("RUN", exp, desc, flush=True)
        d.eval('run("CHARGE");')
        d.eval("tc=getresult('CHARGE::monitor','total_charge');")
        d.eval('Qn=e*pinch(tc.n); Qp=e*pinch(tc.p);')
        d.eval('Cn=abs(Qn(2:2:12)-Qn(1:2:12))/%g; Cp=abs(Qp(2:2:12)-Qp(1:2:12))/%g;' % (DV,DV))
        d.eval('Cj=0.5*(Cn+Cp)*1e15*1e-6;')
        Cj = np.array(d.getv("Cj")).ravel()
        rec["Cj_fF_um"] = Cj.tolist()
        rec["V"] = V0.tolist()
        rec["runtime_s"] = time.time()-t0
        rec["charge_size"] = os.path.getsize(chargefile) if os.path.exists(chargefile) else 0
        rec["status"] = "ok"
        print("OK", exp, "Cj(0V)=%.4f" % Cj[1], "%.0fs" % (time.time()-t0), flush=True)
    except Exception as e:
        rec["status"] = "failed"; rec["error"] = str(e)[:400]
        print("FAIL", exp, str(e)[:300], flush=True)
    finally:
        try: d.close()
        except Exception: pass
    with open(os.path.join(ed,"experiment.json"),"w") as f: json.dump(rec,f,indent=1)
    # registry append
    with open(ROOT + r"\07_Results\experiment_registry.csv","a",newline="") as f:
        w = csv.writer(f)
        w.writerow([rec["exp"], desc, rec["status"], rec.get("runtime_s",""), rec.get("charge_size","")])
print("BATCH DONE")
