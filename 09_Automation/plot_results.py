"""Generate all study plots from validated CSVs. No fabricated curves."""
import os, json, glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
PL = os.path.join(ROOT, "07_Results", "plots")
os.makedirs(PL, exist_ok=True)
BASE = dict(loss=498.2313, VpiL=2.9080, Cj=0.2100, Gcore=0.35355,
            neff=2.567082, ng=3.936389, Aeff=2.0561e-13, TE=0.9866)


def save(name):
    p = os.path.join(PL, name)
    plt.tight_layout(); plt.savefig(p, dpi=165); plt.close()
    print("saved", os.path.basename(p))


def meta(exp):
    for fam in ["02_Doping_Sweeps", "03_Junction_Position", "04_Vertical_Doping_Profiles",
                "05_Combined_Optimization", "06_Final_Validation"]:
        ed = os.path.join(ROOT, fam, exp)
        ej = os.path.join(ed, "experiment.json")
        if os.path.exists(ej):
            try: return json.load(open(ej, encoding="utf-8"))
            except Exception: pass
    return {}


# ---------------- geometry ----------------
gp = os.path.join(ROOT, "01_Geometry_Sweeps", "geometry_metrics.csv")
g = pd.read_csv(gp) if os.path.exists(gp) else None
if g is not None and len(g):
    gw = g[np.isclose(g["slab_nm"], 90)].sort_values("W_nm")
    gs = g[np.isclose(g["W_nm"], 500)].sort_values("slab_nm")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(gw["W_nm"], gw["Gamma_core"], "o-", label="Gamma_core")
    ax[0].plot(gw["W_nm"], gw["Gamma_slab"], "s--", label="Gamma_slab")
    ax[0].set_xlabel("Rib width (nm)"); ax[0].set_ylabel("|E|^2 overlap")
    ax[0].set_title("vs rib width (slab 90 nm)"); ax[0].grid(alpha=.3); ax[0].legend()
    ax[1].plot(gs["slab_nm"], gs["Gamma_core"], "o-", label="Gamma_core")
    ax[1].plot(gs["slab_nm"], gs["Gamma_slab"], "s--", label="Gamma_slab")
    ax[1].set_xlabel("Slab thickness (nm)"); ax[1].set_title("vs slab thickness (W 500 nm)")
    ax[1].grid(alpha=.3); ax[1].legend()
    fig.suptitle("Optical field overlap (screening metric)")
    save("optical_confinement.png")
    save("optical_confinement_vs_rib_width.png")
    save("optical_confinement_vs_slab.png")

    plt.figure()
    plt.plot(gw["W_nm"], gw["neff_re"], "o-", label="W sweep")
    plt.plot(gs["slab_nm"], gs["neff_re"], "s--", label="slab sweep")
    plt.xlabel("Parameter (nm)"); plt.ylabel("neff (0 V)"); plt.grid(alpha=.3); plt.legend()
    plt.title("Effective index vs geometry"); save("effective_index.png")

    plt.figure()
    plt.plot(gw["W_nm"], gw["loss_dB_m"], "o-", label="W sweep")
    plt.plot(gs["slab_nm"], gs["loss_dB_m"], "s--", label="slab sweep")
    plt.axhline(BASE["loss"], color="k", ls=":", lw=1, label="baseline")
    plt.xlabel("Parameter (nm)"); plt.ylabel("Loss (dB/m)")
    plt.title("Optical loss vs geometry (0 V)"); plt.grid(alpha=.3); plt.legend()
    save("optical_loss.png")

    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(g))
    ax.bar(x-0.2, g["loss_dB_m"], 0.4, color="tab:red", label="loss (dB/m)")
    ax.set_ylabel("Loss (dB/m)", color="tab:red")
    ax2 = ax.twinx()
    ax2.bar(x+0.2, g["Gamma_core"], 0.4, color="tab:blue", label="Gamma_core")
    ax2.set_ylabel("Gamma_core", color="tab:blue")
    ax.set_xticks(x)
    ax.set_xticklabels(["%s\n%.0f/%.0f" % (r.exp, r.W_nm, r.slab_nm) for r in g.itertuples()],
                       fontsize=7)
    ax.set_title("Geometry comparison (W nm / slab nm)")
    save("geometry_comparison.png")

    plt.figure()
    plt.scatter(g["Gamma_core"], g["loss_dB_m"], c="tab:blue")
    for r in g.itertuples():
        plt.annotate(r.exp, (r.Gamma_core, r.loss_dB_m), fontsize=7)
    plt.xlabel("Gamma_core"); plt.ylabel("Loss (dB/m)")
    plt.title("Confinement vs optical loss (geometry)"); plt.grid(alpha=.3)
    save("confinement_vs_loss.png")

# ---------------- electrical families ----------------
sp = os.path.join(ROOT, "07_Results", "summary_0V.csv")
s = pd.read_csv(sp) if os.path.exists(sp) else None
if s is not None and len(s):
    s = s.copy()
    s["shift_nm"] = [ (meta(e).get("geom", {}) or {}).get("dx", np.nan) or 0
                      for e in s["exp"]] if False else np.nan
    # build explicit metadata columns
    shifts, scalef, zlab = [], [], []
    for e in s["exp"]:
        m = meta(e)
        geo = m.get("geom", {}) or {}
        shifts.append(geo.get("dx", 0.0) * 1e9 if geo.get("dx") else 0.0)
        pr = m.get("params", {}) or {}
        scalef.append((pr.get("p_wg", 5e23) / 5e23 + pr.get("n_wg", 7e23) / 7e23) / 2)
        zlab.append(m.get("description", ""))
    s["shift_nm"] = shifts; s["doping_scale"] = scalef; s["label"] = zlab

    d = s[s["exp"].str.startswith("D")].sort_values("doping_scale")
    if len(d):
        fig, ax = plt.subplots(1, 3, figsize=(13, 4))
        ax[0].semilogx(d["doping_scale"], d["loss_0V"], "o-"); ax[0].set_ylabel("Loss (dB/m)")
        ax[0].set_title("Loss vs doping scale"); ax[0].grid(alpha=.3)
        ax[1].semilogx(d["doping_scale"], d["VpiL_Vcm"], "o-"); ax[1].set_ylabel("VpiL (V.cm)")
        ax[1].set_title("VpiL vs doping scale"); ax[1].grid(alpha=.3)
        ax[2].semilogx(d["doping_scale"], d["Cj_0V_fF_um"], "o-"); ax[2].set_ylabel("Cj (fF/um)")
        ax[2].set_title("Cj vs doping scale"); ax[2].grid(alpha=.3)
        for a in ax: a.set_xlabel("Doping scale (x baseline)")
        fig.suptitle("Doping sweep (D001-D003)")
        save("doping_comparison.png")
        save("optical_loss_vs_doping.png")
        save("modulation_efficiency.png")
        save("junction_capacitance.png")

    j = s[s["exp"].str.startswith("J")].sort_values("shift_nm")
    if len(j):
        fig, ax = plt.subplots(1, 3, figsize=(13, 4))
        ax[0].plot(j["shift_nm"], j["loss_0V"], "o-"); ax[0].set_ylabel("Loss (dB/m)")
        ax[0].set_title("Loss vs junction shift")
        ax[1].plot(j["shift_nm"], j["VpiL_Vcm"], "o-"); ax[1].set_ylabel("VpiL (V.cm)")
        ax[1].set_title("VpiL vs junction shift")
        ax[2].plot(j["shift_nm"], j["Cj_0V_fF_um"], "o-"); ax[2].set_ylabel("Cj (fF/um)")
        ax[2].set_title("Cj vs junction shift")
        for a in ax: a.set_xlabel("Junction shift (nm)"); a.grid(alpha=.3)
        fig.suptitle("Junction-position sweep (J001-J003)")
        save("optical_loss_vs_junction.png")
        save("junction_sweep.png")

    z = s[s["exp"].str.startswith("Z")].sort_values("exp")
    if len(z):
        x = np.arange(len(z))
        fig, ax = plt.subplots(1, 3, figsize=(13, 4))
        for k, (col, ttl, yl) in enumerate([("loss_0V", "Loss", "dB/m"),
                                            ("VpiL_Vcm", "VpiL", "V.cm"),
                                            ("Cj_0V_fF_um", "Cj", "fF/um")]):
            ax[k].bar(x, z[col], color="tab:green"); ax[k].set_xticks(x)
            ax[k].set_xticklabels(z["exp"]); ax[k].set_title(ttl); ax[k].set_ylabel(yl)
        fig.suptitle("Vertical-profile sweep (Z001-Z003)")
        save("vertical_profiles.png")

    # loss vs VpiL and Pareto
    e = s.dropna(subset=["VpiL_Vcm", "loss_0V", "Cj_0V_fF_um"]).copy()
    if len(e):
        plt.figure()
        sc = plt.scatter(e["VpiL_Vcm"], e["loss_0V"], c=e["Gamma_core"], cmap="viridis")
        plt.colorbar(sc, label="Gamma_core")
        for r in e.itertuples():
            plt.annotate(r.exp, (r.VpiL_Vcm, r.loss_0V), fontsize=7)
        plt.axhline(BASE["loss"], color="k", ls=":", lw=1)
        plt.xlabel("VpiL (V.cm)"); plt.ylabel("Loss (dB/m)")
        plt.title("Loss vs modulation efficiency"); plt.grid(alpha=.3)
        save("loss_vs_vpil.png")

        # 2D Pareto loss/VpiL
        pts = e[["exp", "loss_0V", "VpiL_Vcm"]].values
        front = []
        for i in range(len(pts)):
            dom = False
            for k in range(len(pts)):
                if i == k: continue
                if (pts[k, 1] <= pts[i, 1] and pts[k, 2] <= pts[i, 2] and
                        (pts[k, 1] < pts[i, 1] or pts[k, 2] < pts[i, 2])):
                    dom = True; break
            if not dom: front.append(i)
        f = e.iloc[front].sort_values("VpiL_Vcm")
        plt.figure()
        plt.scatter(e["VpiL_Vcm"], e["loss_0V"], c="grey", label="all")
        plt.plot(f["VpiL_Vcm"], f["loss_0V"], "o-", c="tab:red", label="Pareto")
        for r in e.itertuples():
            plt.annotate(r.exp, (r.VpiL_Vcm, r.loss_0V), fontsize=7)
        plt.xlabel("VpiL (V.cm)"); plt.ylabel("Loss (dB/m)")
        plt.title("Pareto front: loss vs VpiL"); plt.grid(alpha=.3); plt.legend()
        save("pareto_front.png")
        f.to_csv(os.path.join(ROOT, "07_Results", "pareto_front_2d.csv"), index=False)

# ---------------- schematics ----------------
fig, ax = plt.subplots(figsize=(8, 4))
ax.add_patch(Rectangle((-2500, 0), 5000, 90, fc="lightsteelblue", ec="k", label="Si slab 90 nm"))
ax.add_patch(Rectangle((-250, 90), 500, 130, fc="royalblue", ec="k", label="Si rib 500 x 130 nm"))
ax.add_patch(Rectangle((-2500, 220), 5000, 300, fc="wheat", alpha=.3, ec="none", label="SiO2"))
ax.axvline(0, color="r", ls="--", lw=1, label="junction (x=0)")
ax.set_xlim(-1500, 1500); ax.set_ylim(-50, 520)
ax.set_xlabel("x (nm)"); ax.set_ylabel("z (nm)")
ax.set_title("TWMZM cross-section (baseline)")
ax.legend(fontsize=7, loc="upper right")
save("cross_section_geometry.png")

fig, ax = plt.subplots(figsize=(8, 4))
ax.add_patch(Rectangle((-600, 0), 1200, 220, fc="none", ec="k"))
ax.add_patch(Rectangle((-600, 0), 660, 255, fc="red", alpha=.25, label="p wg 5e17"))
ax.add_patch(Rectangle((-40, 0), 290, 237, fc="blue", alpha=.25, label="n wg 7e17"))
ax.add_patch(Rectangle((-600, 0), 450, 90, fc="green", alpha=.25, label="p slab 7e17"))
ax.add_patch(Rectangle((150, 0), 450, 90, fc="purple", alpha=.25, label="n slab 5e17"))
ax.axvline(0, color="k", ls="--")
ax.set_xlim(-700, 700); ax.set_ylim(-20, 280)
ax.set_xlabel("x (nm)"); ax.set_ylabel("z (nm)")
ax.set_title("Baseline lateral doping boundaries")
ax.legend(fontsize=7)
save("doping_profile_boundaries.png")

# ---------------- small-signal AC (only for runs that have it) ----------------
def acpath(exp):
    for fam in ("00_Original_Baseline", "03_Junction_Position",
                "05_Combined_Optimization", "06_Final_Validation"):
        p = os.path.join(ROOT, fam, exp, "ac_metrics.json")
        if os.path.exists(p):
            return p
    return None

ac_exps = [e for e in ("B000", "J002", "C004", "C001", "C002", "C003")
           if acpath(e)]
if ac_exps:
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for e in ac_exps:
        a = json.load(open(acpath(e), encoding="utf-8"))
        Vc = np.array(a["V_cathode"]).ravel()
        R = np.array(a["R_all"])
        C = np.array(a["C_all"])
        f = np.array(a["f_Hz"]).ravel()
        i20 = int(np.argmin(np.abs(f - 20e9)))
        ax[0].plot(Vc, R[:, i20], "o-", ms=3, label=e)
        ax[1].plot(Vc, C[:, 0] * 1e9, "o-", ms=3, label=e)
    f_ghz = f[np.argmin(np.abs(f - 20e9))] / 1e9
    ax[0].set_xlabel("Cathode bias (V)")
    ax[0].set_ylabel("Re(Z) at %.1f GHz (ohm)" % f_ghz)
    ax[0].set_title("Series resistance (ssac)"); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3)
    ax[1].set_xlabel("Cathode bias (V)"); ax[1].set_ylabel("C_ac at 1 MHz (fF/um)")
    ax[1].set_title("Small-signal capacitance"); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3)
    save("ac_rc.png")

print("PLOT SCRIPT DONE")
