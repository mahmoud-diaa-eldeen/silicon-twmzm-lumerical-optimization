"""Geometry screening re-run on the B000 charge file (same mesh as the clean
CHARGE+MODE experiments).  Writes a separate CSV so the original screening
(recorded baseline charge) is preserved for provenance.

MODE-only: the charge distribution is held at the baseline 0 V map; only the
rib width / slab thickness change.  This is a screening ranking, not a full
CHARGE-coupled result.
"""
import os, csv, json
import numpy as np
import lumapi

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
OUT = os.path.join(ROOT, "01_Geometry_Sweeps")
os.makedirs(OUT, exist_ok=True)
CHARGE = os.path.join(ROOT, "00_Original_Baseline", "B000", "charge.mat").replace("\\", "/")
logf = open(os.path.join(OUT, "geometry_b000_log.txt"), "w", encoding="utf-8")


def L(*a):
    s = " ".join(str(x) for x in a)
    logf.write(s + "\n"); logf.flush(); print(s, flush=True)


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
    neff = complex(np.array(m.getdata("mode1", "neff")).ravel()[0])
    ng = complex(np.array(m.getdata("mode1", "ng")).ravel()[0])
    loss = float(np.array(m.getdata("mode1", "loss")).ravel()[0])
    Aeff = float(np.array(m.getdata("mode1", "mode effective area")).ravel()[0])
    tef = float(np.array(m.getdata("mode1", "TE polarization fraction")).ravel()[0])
    return dict(neff_re=neff.real, neff_im=neff.imag, ng=ng.real, loss_dB_m=loss,
                Aeff_m2=Aeff, TE_frac=tef,
                Gamma_core=trapz2(E2*core, x, z)/tot,
                Gamma_slab=trapz2(E2*slab, x, z)/tot), x, z


cases = [
    ("G000", 500e-9, 90e-9),
    ("G001", 450e-9, 90e-9),
    ("G002", 550e-9, 90e-9),
    ("G003", 600e-9, 90e-9),
    ("G004", 500e-9, 70e-9),
    ("G005", 500e-9, 110e-9),
]

rows = []
m = lumapi.MODE(hide=True)
try:
    m.eval('load("D:/lumerical/tw_modulator_optical_MODE.lms");')
    m.eval('select("np"); importdataset("%s");' % CHARGE)
    # 0 V is 1-based index 3 in the 20-point grid [-0.5, -0.475, 0.0, ...]
    m.eval('setnamed("np","V_cathode_index",3);')
    m.eval('setanalysis("store mode profiles while tracking",1);')
    for cid, W, ts in cases:
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
            m.eval('findmodes;')
            mt, x, z = metrics(m, W, ts)
            try:
                m.eval('v2 = getdata("mode2","neff");')
                mt["mode2_neff"] = complex(np.array(m.getv("v2")).ravel()[0]).real
            except Exception:
                mt["mode2_neff"] = float("nan")
            mt.update(dict(exp=cid, W_nm=W*1e9, slab_nm=ts*1e9))
            rows.append(mt)
            L(cid, "W=%.0fnm slab=%.0fnm neff=%.5f loss=%.1f Gcore=%.3f Gslab=%.3f" %
              (W*1e9, ts*1e9, mt["neff_re"], mt["loss_dB_m"],
               mt["Gamma_core"], mt["Gamma_slab"]))
            d = os.path.join(OUT, cid)
            os.makedirs(d, exist_ok=True)
            json.dump(mt, open(os.path.join(d, "metrics_b000.json"), "w"), indent=1)
        except Exception as e:
            L(cid, "FAILED", str(e)[:200])
finally:
    try:
        m.close()
    except Exception:
        pass

if rows:
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, "geometry_metrics_b000.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
L("DONE")
logf.close()
