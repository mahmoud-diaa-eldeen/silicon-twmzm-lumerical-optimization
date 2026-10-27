"""MODE (FDE) pass over every valid CHARGE experiment.

For each experiment:
  import charge.mat into the np grid attribute, sweep V_cathode_index,
  run findmodes, extract neff/ng/loss/Aeff/TE fraction and the field-overlap
  metrics Gamma_core / Gamma_slab (screening definition, see EQUATIONS doc).
Writes:
  07_Results/all_metrics.csv      (one row per experiment x bias)
  07_Results/summary_0V.csv       (one row per experiment)
"""
import os, json, glob, csv, sys
import numpy as np
import h5py
import lumapi

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
LMS = "D:/lumerical/tw_modulator_optical_MODE.lms"
FAMS = ["00_Original_Baseline", "02_Doping_Sweeps", "03_Junction_Position",
        "04_Vertical_Doping_Profiles", "05_Combined_Optimization", "06_Final_Validation"]
# Optional: process only the named experiments (e.g. C001 C002 C003) and merge
# their rows into the existing CSVs instead of recomputing everything.
ONLY = set(sys.argv[1:])

def read_v(path):
    try:
        with h5py.File(path, "r") as f:
            return np.array(f["#refs#/#v#"]).ravel()
    except Exception:
        return np.array([])

def trapz2(f, x, z):
    return float(np.trapz(np.trapz(f, x=z, axis=1), x=x, axis=0))

def metrics(m, W, ts):
    x = np.array(m.getdata("mode1", "x")).ravel()
    z = np.array(m.getdata("mode1", "z")).ravel()
    Ex = np.array(m.getdata("mode1", "Ex"))[:, 0, :, 0]
    Ey = np.array(m.getdata("mode1", "Ey"))[:, 0, :, 0]
    Ez = np.array(m.getdata("mode1", "Ez"))[:, 0, :, 0]
    E2 = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    X, Z = np.meshgrid(x, z, indexing="ij")
    tot = trapz2(E2, x, z)
    core = (np.abs(X) <= W/2) & (Z >= ts) & (Z <= 220e-9)
    slab = (np.abs(X) <= 2.5e-6) & (Z >= 0) & (Z < ts)
    return dict(
        neff_re=float(np.array(m.getdata("mode1", "neff")).ravel()[0].real),
        neff_im=float(np.array(m.getdata("mode1", "neff")).ravel()[0].imag),
        ng=float(np.array(m.getdata("mode1", "ng")).ravel()[0].real),
        loss=float(np.array(m.getdata("mode1", "loss")).ravel()[0]),
        Aeff=float(np.array(m.getdata("mode1", "mode effective area")).ravel()[0]),
        TE=float(np.array(m.getdata("mode1", "TE polarization fraction")).ravel()[0]),
        Gcore=trapz2(E2*core, x, z)/tot,
        Gslab=trapz2(E2*slab, x, z)/tot)

rows, summ = [], []
m = lumapi.MODE(hide=True)
try:
    m.eval('load("%s");' % LMS)
    m.eval('setanalysis("store mode profiles while tracking",1);')
    for fam in FAMS:
        for ed in sorted(glob.glob(os.path.join(ROOT, fam, "*"))):
            cf = os.path.join(ed, "charge.mat")
            if not (os.path.isdir(ed) and os.path.exists(cf)):
                continue
            exp = os.path.basename(ed)
            if ONLY and exp not in ONLY:
                continue
            j = {}
            ej = os.path.join(ed, "experiment.json")
            if os.path.exists(ej):
                try: j = json.load(open(ej, encoding="utf-8"))
                except Exception: pass
            W = j.get("W_nm", 500) * 1e-9
            ts = j.get("slab_nm", 90) * 1e-9
            Vc = read_v(cf)
            if len(Vc) == 0:
                print("no V:", exp); continue
            status = j.get("status", "UNKNOWN")
            try:
                m.eval('switchtolayout;')
                m.eval('setnamed("wg","x span",%g);' % W)
                m.eval('setnamed("wg","z min",%g);' % ts)
                m.eval('setnamed("wg","z max",220e-9);')
                m.eval('setnamed("pad","z min",0);')
                m.eval('setnamed("pad","z max",%g);' % ts)
                m.eval('setnamed("mesh","x span",%g);' % W)
                m.eval('setnamed("mesh","z min",0);')
                m.eval('setnamed("mesh","z max",220e-9);')
                m.eval('select("np"); importdataset("%s");' % cf.replace("\\", "/"))
                res = []
                for i, V in enumerate(Vc, start=1):
                    # after findmodes the session is in results mode; changing a
                    # layout parameter (V_cathode_index) requires layout mode.
                    m.eval('switchtolayout;')
                    m.eval('setnamed("np","V_cathode_index",%d);' % i)
                    m.eval('findmodes;')
                    mm = metrics(m, W, ts)
                    mm.update(V=float(V), index=i)
                    res.append(mm)
                ref = min(range(len(res)), key=lambda k: abs(res[k]["V"]))
                for k in range(len(res)):
                    res[k]["dneff"] = res[k]["neff_re"] - res[ref]["neff_re"]
                    res[k]["dloss"] = res[k]["loss"] - res[ref]["loss"]
                # use the 0 -> 4.0 V principal points (the +0.025 V twin is only
                # for the finite-difference Cj, not for the VpiL slope)
                last = min(range(len(res)), key=lambda k: abs(res[k]["V"] - 4.0))
                dV = res[last]["V"] - res[ref]["V"]
                slope = (res[last]["dneff"] - res[ref]["dneff"]) / dV if abs(dV) > 1e-9 else float("nan")
                vpil = 1.55e-6 / (2 * abs(slope)) * 100 if abs(slope) > 1e-12 else float("inf")
                for mm in res:
                    mm.update(exp=exp, status=status, W_nm=W*1e9, slab_nm=ts*1e9,
                              VpiL_Vcm=vpil)
                rows += res
                r0 = res[ref]; r4 = res[last]
                cj = j.get("Cj_fF_um")
                summ.append(dict(
                    exp=exp, family=fam, status=status,
                    n_bias=len(res), V_ref=r0["V"], V_max=r4["V"],
                    neff_0V=r0["neff_re"], ng_0V=r0["ng"], loss_0V=r0["loss"],
                    Gamma_core=r0["Gcore"], Gamma_slab=r0["Gslab"], Aeff=r0["Aeff"],
                    TE_frac=r0["TE"], dneff_0_4V=r4["dneff"], dloss_0_4V=r4["dloss"],
                    VpiL_Vcm=vpil,
                    Cj_0V_fF_um=(cj[1] if cj and len(cj) > 1 else ""),
                    Cj_4V_fF_um=(cj[-1] if cj else ""),
                    W_nm=W*1e9, slab_nm=ts*1e9))
                json.dump({"exp": exp, "V": res, "VpiL_Vcm": vpil,
                           "provenance": {"charge": cf, "mode": LMS,
                                          "Gamma": "|E|^2 overlap, trapezoid on FDE grid"}},
                          open(os.path.join(ed, "optical_metrics.json"), "w"), indent=1)
                print("%-6s VpiL=%.3f neff0=%.5f loss0=%.1f Gcore=%.3f"
                      % (exp, vpil, r0["neff_re"], r0["loss"], r0["Gcore"]), flush=True)
            except Exception as e:
                print("FAIL", exp, str(e)[:200], flush=True)
finally:
    try: m.close()
    except Exception: pass

if rows:
    keys = ["exp", "family", "status", "W_nm", "slab_nm", "V", "index",
            "neff_re", "neff_im", "ng", "loss", "dneff", "dloss", "Aeff", "TE",
            "Gcore", "Gslab", "VpiL_Vcm"]
    ap = os.path.join(ROOT, "07_Results", "all_metrics.csv")
    old = []
    if ONLY and os.path.exists(ap):
        with open(ap, newline="", encoding="utf-8") as f:
            old = [r for r in csv.DictReader(f) if r.get("exp") not in ONLY]
    with open(ap, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in old:
            w.writerow(r)
        for r in rows:
            w.writerow(r)
if summ:
    sp = os.path.join(ROOT, "07_Results", "summary_0V.csv")
    old = []
    skeys = list(summ[0].keys())
    if ONLY and os.path.exists(sp):
        with open(sp, newline="", encoding="utf-8") as f:
            old = [r for r in csv.DictReader(f) if r.get("exp") not in ONLY]
            if old:
                skeys = list(old[0].keys())
                for k in summ[0].keys():
                    if k not in skeys:
                        skeys.append(k)
    with open(sp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=skeys, extrasaction="ignore")
        w.writeheader()
        for r in old:
            w.writerow(r)
        for r in summ:
            w.writerow(r)
print("MODE PASS DONE")
