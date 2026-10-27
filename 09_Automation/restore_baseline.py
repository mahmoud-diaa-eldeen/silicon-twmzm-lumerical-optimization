"""One-off recovery: rebuild a pristine baseline layout from the contaminated
copy, using baseline_manifest.json values. Writes
00_Original_Baseline/tw_modulator_DEVICE_pristine.ldev (the working copy used by
all subsequent runs). The contaminated copy is kept as evidence.
"""
import os, sys
import lumapi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from baseline_utils import ROOT, reset_baseline

SRC = os.path.join(ROOT, "00_Original_Baseline", "tw_modulator_DEVICE_current.ldev")
DST = os.path.join(ROOT, "00_Original_Baseline", "tw_modulator_DEVICE_pristine.ldev")

d = lumapi.DEVICE(hide=True)
try:
    d.eval('load("%s");' % SRC.replace("\\", "/"))
    d.eval('switchtolayout;')
    reset_baseline(d)
    d.eval("setnamed('CHARGE','solver mode','steady state');")
    d.eval("setnamed('CHARGE::boundary conditions::cathode','sweep type','value');")
    d.eval('save("%s");' % DST.replace("\\", "/"))
    print("saved pristine working copy:", DST, os.path.getsize(DST) if os.path.exists(DST) else 0)
finally:
    try:
        d.close()
    except Exception as e:
        print("close:", e)
print("RESTORE DONE")
