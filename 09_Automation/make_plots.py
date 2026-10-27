import os, json, glob, csv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
PL = os.path.join(ROOT, "07_Results", "plots")
os.makedirs(PL, exist_ok=True)

def savefig(name):
    p = os.path.join(PL, name)
    plt.tight_layout(); plt.savefig(p, dpi=160); plt.close()
    print("saved", p)

# ---------------- geometry plots ----------------
gp = os.path.join(ROOT, "01_Geometry_Sweeps", "geometry_metrics.csv")
if os.path.exists(gp):
    g = pd.read_csv(gp)
    g0 = g[g["exp"] == "G000"].iloc[0]
    # width sweep (slab=90)
    gw = g[np.isclose(g["slab_nm"], 90)].sort_values("W_nm")
    gs = g[np.isclose(g["W_nm"], 500)].sort_values("slab_nm")

    plt.figure()
    plt.plot(gw["W_nm"], gw["Gamma_core"], "o-", label="Gamma_core")
    plt.plot(gw["W_nm"], gw["Gamma_slab"], "s--", label="Gamma_slab")
    plt.xlabel("Rib width (nm)"); plt.ylabel("Field overlap")
    plt.title("Confinement vs rib width (slab=90 nm)"); plt.grid(True, alpha=.3); plt.legend()
    savefig("optical_confinement_vs_rib_width.png")

    plt.figure()
    plt.plot(gs["slab_nm"], gs["Gamma_core"], "o-", label="Gamma_core")
    plt.plot(gs["slab_nm"], gs["Gamma_slab"], "s--", label="Gamma_slab")
    plt.xlabel("Slab thickness (nm)"); plt.ylabel("Field overlap")
    plt.title("Confinement vs slab thickness (W=500 nm)"); plt.grid(True, alpha=.3); plt.legend()
    savefig("optical_confinement_vs_slab.png")

    plt.figure()
    plt.plot(gw["W_nm"], gw["neff_re"], "o-", label="neff (W sweep)")
    plt.plot(gs["slab_nm"], gs["neff_re"], "s--", label="neff (slab sweep)")
    plt.xlabel("Parameter value (nm)"); plt.ylabel("Effective index")
    plt.title("Effective index vs geometry"); plt.grid(True, alpha=.3); plt.legend()
    savefig("effective_index.png")

    plt.figure()
    plt.plot(gw["W_nm"], gw["loss_dB_m"], "o-", label="loss (W sweep)")
    plt.plot(gs["slab_nm"], gs["loss_dB_m"], "s--", label="loss (slab sweep)")
    plt.xlabel("Parameter value (nm)"); plt.ylabel("Optical loss (dB/m)")
    plt.title("Optical loss vs geometry (0 V)"); plt.grid(True, alpha=.3); plt.legend()
    savefig("optical_loss_vs_geometry.png")

    plt.figure()
    plt.scatter(g["Gamma_core"], g["loss_dB_m"])
    for _, r in g.iterrows():
        plt.annotate(r["exp"], (r["Gamma_core"], r["loss_dB_m"]), fontsize=7)
    plt.xlabel("Gamma_core"); plt.ylabel("Loss (dB/m)")
    plt.title("Confinement vs optical loss (geometry sweep)"); plt.grid(True, alpha=.3)
    savefig("confinement_vs_loss.png")

    # geometry comparison bar
    fig, ax = plt.subplots()
    x = np.arange(len(g)); ax.bar(x-0.2, g["loss_dB_m"], 0.4, label="loss (dB/m)")
    ax2 = ax.twinx(); ax2.bar(x+0.2, g["Gamma_core"], 0.4, color="orange", label="Gamma_core")
    ax.set_xticks(x); ax.set_xticklabels(g["exp"], rotation=45)
    ax.set_ylabel("Loss (dB/m)"); ax2.set_ylabel("Gamma_core"); ax.set_title("Geometry comparison")
    savefig("geometry_comparison.png")

# ---------------- experiment (doping/junction/vertical) ----------------
sp = os.path.join(ROOT, "07_Results", "all_metrics.csv")
if os.path.exists(sp):
    df = pd.read_csv(sp)
    # 0V slice
    z = df.copy()
    z["dV"] = z["V"].abs()
    z0 = z.loc[z.groupby("exp")["dV"].idxmin()].copy()

    # merge Cj from experiment.json
    cj = {}
    for ed in glob.glob(os.path.join(ROOT, "0[2-6]_*", "*")):
        ej = os.path.join(ed, "experiment.json")
        if os.path.exists(ej):
            try:
                j = json.load(open(ej)); e = j["exp"]
                if "Cj_fF_um" in j:
                    cj[e] = j["Cj_fF_um"][1]
            except Exception: pass
    z0["Cj_fF_um"] = z0["exp"].map(cj)

    # doping concentration knob (avg channel)
    conc = {}
    for ed in glob.glob(os.path.join(ROOT, "02_Doping_Sweeps", "*")):
        ej = os.path.join(ed, "experiment.json")
        if os.path.exists(ej):
            try:
                j = json.load(open(ej)); conc[j["exp"]] = 0.5*(j["params"]["p_wg"]+j["params"]["n_wg"])/1e6
            except Exception: pass

    d = z0[z0["exp"].str.startswith("D")].copy()
    if len(d):
        d["conc_cm3"] = d["exp"].map(conc)
        d = d.dropna(subset=["conc_cm3"]).sort_values("conc_cm3")
        plt.figure(); plt.semilogx(d["conc_cm3"], d["loss"], "o-")
        plt.xlabel("Channel doping (cm^-3)"); plt.ylabel("Loss (dB/m)")
        plt.title("Optical loss vs doping"); plt.grid(True, which="both", alpha=.3)
        savefig("optical_loss_vs_doping.png")

        plt.figure(); plt.semilogx(d["conc_cm3"], d["VpiL_Vcm"], "o-")
        plt.xlabel("Channel doping (cm^-3)"); plt.ylabel("VpiL (V.cm)")
        plt.title("Modulation efficiency vs doping"); plt.grid(True, which="both", alpha=.3)
        savefig("modulation_efficiency.png")

        if d["Cj_fF_um"].notna().any():
            plt.figure(); plt.semilogx(d["conc_cm3"], d["Cj_fF_um"], "o-")
            plt.xlabel("Channel doping (cm^-3)"); plt.ylabel("Cj at 0 V (fF/um)")
            plt.title("Junction capacitance vs doping"); plt.grid(True, which="both", alpha=.3)
            savefig("junction_capacitance.png")

    j = z0[z0["exp"].str.startswith("J")].copy()
    if len(j):
        j = j.sort_values("exp")
        plt.figure(); plt.plot(j["exp"], j["loss"], "o-")
        plt.xlabel("Junction shift case"); plt.ylabel("Loss (dB/m)")
        plt.title("Optical loss vs junction position"); plt.grid(True, alpha=.3)
        savefig("optical_loss_vs_junction.png")

    # doping comparison bars
    if len(d):
        fig, ax = plt.subplots()
        x = np.arange(len(d)); ax.bar(x, d["loss"], color="tab:red")
        ax.set_xticks(x); ax.set_xticklabels(d["exp"])
        ax.set_ylabel("Loss (dB/m)"); ax.set_title("Doping comparison")
        savefig("doping_comparison.png")

    # loss vs VpiL
    plt.figure(); plt.scatter(z0["VpiL_Vcm"], z0["loss"])
    for _, r in z0.iterrows():
        plt.annotate(r["exp"], (r["VpiL_Vcm"], r["loss"]), fontsize=7)
    plt.xlabel("VpiL (V.cm)"); plt.ylabel("Loss (dB/m)")
    plt.title("Loss vs modulation efficiency (all experiments)"); plt.grid(True, alpha=.3)
    savefig("loss_vs_vpil.png")

    # Pareto (minimize loss & VpiL, among feasible)
    pts = z0.dropna(subset=["VpiL_Vcm"]).copy()
    pts = pts[np.isfinite(pts["VpiL_Vcm"])]
    front = []
    for i, r in pts.iterrows():
        dominated = False
        for jx, r2 in pts.iterrows():
            if (r2["loss"] <= r["loss"] and r2["VpiL_Vcm"] <= r["VpiL_Vcm"] and
                (r2["loss"] < r["loss"] or r2["VpiL_Vcm"] < r["VpiL_Vcm"])):
                dominated = True; break
        if not dominated: front.append(i)
    pf = pts.loc[front].sort_values("VpiL_Vcm")
    plt.figure()
    plt.scatter(pts["VpiL_Vcm"], pts["loss"], c="grey", label="all")
    plt.plot(pf["VpiL_Vcm"], pf["loss"], "o-", c="tab:red", label="Pareto")
    for _, r in pts.iterrows():
        plt.annotate(r["exp"], (r["VpiL_Vcm"], r["loss"]), fontsize=7)
    plt.xlabel("VpiL (V.cm)"); plt.ylabel("Loss (dB/m)")
    plt.title("Pareto front: loss vs VpiL"); plt.grid(True, alpha=.3); plt.legend()
    savefig("pareto_front.png")
    pf.to_csv(os.path.join(ROOT, "07_Results", "pareto_front.csv"), index=False)
    z0.to_csv(os.path.join(ROOT, "07_Results", "best_designs.csv"), index=False)
    print("pareto:", list(pf["exp"]))

# ---------------- cross-section schematic ----------------
fig, ax = plt.subplots(figsize=(8,4))
ax.add_patch(Rectangle((-2500,0),5000,90,fc="lightsteelblue",ec="k",label="Si slab 90nm"))
ax.add_patch(Rectangle((-250,90),500,130,fc="royalblue",ec="k",label="Si rib 500x130nm"))
ax.add_patch(Rectangle((-2500,220),5000,300,fc="wheat",alpha=.3,ec="none",label="SiO2 cladding"))
ax.axvline(0,color="r",ls="--",lw=1,label="junction (x=0)")
ax.set_xlim(-1500,1500); ax.set_ylim(-50,520)
ax.set_xlabel("x (nm)"); ax.set_ylabel("z (nm)"); ax.set_title("TWMZM cross-section (baseline)")
ax.legend(fontsize=7,loc="upper right")
savefig("cross_section_geometry.png")

# ---------------- doping profile schematic ----------------
fig, ax = plt.subplots(figsize=(8,4))
ax.add_patch(Rectangle((-600,0),1200,220,fc="none",ec="k"))
ax.add_patch(Rectangle((-600,0),300,255,fc="red",alpha=.25,label="p wg (5e17)"))
ax.add_patch(Rectangle((60,0),250,237,fc="blue",alpha=.25,label="n wg (7e17)"))
ax.add_patch(Rectangle((-600,0),600,90,fc="green",alpha=.2,label="p slab (7e17)"))
ax.add_patch(Rectangle((150,0),450,90,fc="purple",alpha=.2,label="n slab (5e17)"))
ax.axvline(0,color="k",ls="--"); ax.set_xlim(-700,700); ax.set_ylim(-20,280)
ax.set_xlabel("x (nm)"); ax.set_ylabel("z (nm)"); ax.set_title("Baseline lateral doping boundaries")
ax.legend(fontsize=7)
savefig("doping_profile_boundaries.png")
print("PLOTS DONE")
