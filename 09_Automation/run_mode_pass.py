import os, csv, json, glob, time
import numpy as np
import h5py
import lumapi

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
LMS = "D:/lumerical/tw_modulator_optical_MODE.lms"
logf = open(ROOT + r"\07_Results\mode_pass_log.txt", "w", encoding="utf-8")
def L(*a):
    s = " ".join(str(x) for x in a); logf.write(s+"\n"); logf.flush(); print(s, flush=True)

def read_vcathode(matpath):
    try:
        with h5py.File(matpath, "r") as f:
            if "#refs#" in f and "#v#" in f["#refs#"]:
                return np.array(f["#refs#/#v#"]).ravel()
    except Exception as e:
        L("read_vcathode fail", matpath, e)
    return np.array([])

def trapz2(f, x, z):
    return float(np.trapz(np.trapz(f, x=z, axis=1), x=x, axis=0))

def mode_metrics(m, W, ts):
    x = np.array(m.getdata("mode1","x")).ravel()
    z = np.array(m.getdata("mode1","z")).ravel()
    Ex = np.array(m.getdata("mode1","Ex"))[:,0,:,0]
    Ey = np.array(m.getdata("mode1","Ey"))[:,0,:,0]
    Ez = np.array(m.getdata("mode1","Ez"))[:,0,:,0]
    E2 = np.abs(Ex)**2+np.abs(Ey)**2+np.abs(Ez)**2
    X, Z = np.meshgrid(x, z, indexing="ij")
    tot = trapz2(E2, x, z)
    core = (np.abs(X) <= W/2) & (Z >= ts) & (Z <= 220e-9)
    slab = (np.abs(X) <= 2.5e-6) & (Z >= 0) & (Z < ts)
    return dict(
        neff_re=float(np.array(m.getdata("mode1","neff")).ravel()[0].real),
        neff_im=float(np.array(m.getdata("mode1","neff")).ravel()[0].imag),
        ng=float(np.array(m.getdata("mode1","ng")).ravel()[0].real),
        loss=float(np.array(m.getdata("mode1","loss")).ravel()[0]),
        Aeff=float(np.array(m.getdata("mode1","mode effective area")).ravel()[0]),
        TE=float(np.array(m.getdata("mode1","TE polarization fraction")).ravel()[0]),
        Gcore=trapz2(E2*core, x, z)/tot,
        Gslab=trapz2(E2*slab, x, z)/tot,
    )

def find_exps():
    exps = []
    for fam in ["01_Geometry_Sweeps","02_Doping_Sweeps","03_Junction_Position",
                "04_Vertical_Doping_Profiles","05_Combined_Optimization","06_Final_Validation"]:
        for d in sorted(glob.glob(os.path.join(ROOT, fam, "*"))):
            cf = os.path.join(d, "charge.mat")
            if os.path.exists(cf) and os.path.getsize(cf) > 1e6:
                exps.append(d)
    return exps

rows = []
m = lumapi.MODE(hide=True)
try:
    m.eval('load("%s");' % LMS)
    m.eval('setanalysis("store mode profiles while tracking",1);')
    for ed in find_exps():
        exp = os.path.basename(ed)
        # geometry
        W, ts = 500e-9, 90e-9
        ein = os.path.join(ed, "experiment.json")
        if os.path.exists(ein):
            try:
                j = json.load(open(ein))
                W = j.get("W_nm", 500)*1e-9
                ts = j.get("slab_nm", 90)*1e-9
            except Exception: pass
        cf = os.path.join(ed, "charge.mat")
        Vc = read_vcathode(cf)
        if len(Vc) == 0:
            L("no Vcathode", exp); continue
        try:
            m.eval('switchtolayout;')
            # reset geometry to experiment geometry
            m.eval('setnamed("wg","x span",%g);' % W)
            m.eval('setnamed("wg","z min",%g);' % ts)
            m.eval('setnamed("wg","z max",220e-9);')
            m.eval('setnamed("pad","z min",0);')
            m.eval('setnamed("pad","z max",%g);' % ts)
            m.eval('setnamed("mesh","x span",%g);' % W)
            m.eval('setnamed("mesh","z min",0);')
            m.eval('setnamed("mesh","z max",220e-9);')
            m.eval('select("np"); importdataset("%s");' % cf.replace("\\","/"))
            res = []
            for i, V in enumerate(Vc, start=1):
                m.eval('setnamed("np","V_cathode_index",%d);' % i)
                m.eval('findmodes;')
                mm = mode_metrics(m, W, ts)
                mm["V"] = float(V); mm["index"] = i
                res.append(mm)
            # reference at V closest to 0
            ref = min(range(len(res)), key=lambda k: abs(res[k]["V"]-0.0))
            for k in range(len(res)):
                res[k]["dneff"] = res[k]["neff_re"] - res[ref]["neff_re"]
                res[k]["dloss"] = res[k]["loss"] - res[ref]["loss"]
            # VpiL from 0 -> max V
            last = max(range(len(res)), key=lambda k: res[k]["V"])
            dV = res[last]["V"] - res[ref]["V"]
            slope = (res[last]["dneff"] - res[ref]["dneff"])/dV if abs(dV) > 1e-9 else float("nan")
            vpil = (1.55e-6/(2*abs(slope))*100) if abs(slope) > 1e-12 else float("inf")
            for mm in res:
                mm["VpiL_Vcm"] = vpil
            # write
            with open(os.path.join(ed, "optical_metrics.json"), "w") as f:
                json.dump({"exp": exp, "V": res, "VpiL_Vcm": vpil}, f, indent=1)
            for mm in res:
                mm.update(dict(exp=exp, W_nm=W*1e9, slab_nm=ts*1e9))
                rows.append(mm)
            L(exp, "VpiL=%.3f V.cm" % vpil,
              "neff0=%.5f" % res[ref]["neff_re"],
              "loss0=%.1f" % res[ref]["loss"],
              "Gcore=%.3f" % res[ref]["Gcore"])
        except Exception as e:
            L(exp, "FAILED", str(e)[:200])
finally:
    try: m.close()
    except Exception: pass

if rows:
    keys = ["exp","W_nm","slab_nm","V","index","neff_re","neff_im","ng","loss","dneff","dloss",
            "Aeff","TE","Gcore","Gslab","VpiL_Vcm"]
    with open(ROOT + r"\07_Results\all_metrics.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows: w.writerow(r)
L("DONE")
logf.close()
