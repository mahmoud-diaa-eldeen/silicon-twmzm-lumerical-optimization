import os, time, json
import numpy as np
import lumapi

os.chdir(r"D:\lumerical")
OUT = r"D:\lumerical\TW_Modulator_Optimization_Study\00_Original_Baseline"
os.makedirs(OUT, exist_ok=True)
chargefile = OUT + r"\charge_baseline.mat"

d = lumapi.DEVICE(hide=True)
res = {}
try:
    t0=time.time()
    d.eval('load("D:/lumerical/tw_modulator_DEVICE.ldev");')
    d.eval('switchtolayout;')
    # 6 bias points, +/- dv table for Cj
    d.eval('vmin=-0.5; vmax=4; N=6; dv=0.025;')
    d.eval('vdv=matrix(2*N,1); vdv(1:2:(2*N))=linspace(vmin,vmax,N); vdv(2:2:(2*N))=vdv(1:2:(2*N))+sign(vmax)*dv;')
    d.eval("setnamed('CHARGE::boundary conditions::cathode','sweep type','value');")
    d.eval("setnamed('CHARGE::boundary conditions::cathode','value table',vdv);")
    d.eval("setnamed('CHARGE','solver mode','steady state');")
    # save charge maps
    d.eval("setnamed('CHARGE::monitor_charge','save data',1);")
    d.eval("setnamed('CHARGE::monitor_charge','filename','%s');" % chargefile.replace('\\','/'))
    print(">>> running CHARGE...", flush=True)
    t1=time.time()
    d.eval('run("CHARGE");')
    print(">>> CHARGE done in %.1fs" % (time.time()-t1), flush=True)
    # Cj
    d.eval("tc=getresult('CHARGE::monitor','total_charge');")
    d.eval('Qn=e*pinch(tc.n); Qp=e*pinch(tc.p);')
    d.eval('Cn=abs(Qn(2:2:(2*N))-Qn(1:2:(2*N)))/dv; Cp=abs(Qp(2:2:(2*N))-Qp(1:2:(2*N)))/dv;')
    d.eval('V=vdv(1:2:(2*N));')
    d.eval('Cj=0.5*(Cn+Cp)*1e15*1e-6;')  # fF/um
    V = np.array(d.getv("V")).ravel()
    Cj = np.array(d.getv("Cj")).ravel()
    res["V"] = V.tolist(); res["Cj_fF_um"] = Cj.tolist()
    print("V:", V)
    print("Cj(fF/um):", Cj)
    print("charge file exists:", os.path.exists(chargefile), os.path.getsize(chargefile) if os.path.exists(chargefile) else 0)
    res["chargefile"] = chargefile
    res["charge_size"] = os.path.getsize(chargefile) if os.path.exists(chargefile) else 0
    res["runtime_s"] = time.time()-t0
finally:
    try: d.close()
    except Exception: pass
with open(OUT + r"\baseline_charge_test.json","w") as f: json.dump(res,f,indent=1)
print("DONE", res.get("runtime_s"))
