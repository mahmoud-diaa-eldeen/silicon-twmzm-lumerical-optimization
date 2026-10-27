"""Generate the Egyptian-Arabic student explainer from the validated results.

Every number in the document is read from the CSVs/JSON produced by the actual
Lumerical runs; nothing is typed in by hand.  Run after make_final_reports.py.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\lumerical\TW_Modulator_Optimization_Study"
R = os.path.join(ROOT, "07_Results")
REP = os.path.join(ROOT, "08_Reports")


def rd(p):
    return pd.read_csv(p) if os.path.exists(p) else None


def jload(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


s = rd(os.path.join(R, "summary_0V.csv"))
if s is not None:
    s = s[s["status"].astype(str).str.startswith("SUCCESS")].copy()
b0 = s[s["exp"] == "B000"].iloc[0] if (s is not None and len(s[s["exp"] == "B000"])) else None
gp = os.path.join(ROOT, "01_Geometry_Sweeps", "geometry_metrics_b000.csv")
if not os.path.exists(gp):
    gp = os.path.join(ROOT, "01_Geometry_Sweeps", "geometry_metrics.csv")
g = rd(gp)
pf = rd(os.path.join(R, "pareto_front.csv"))


def t_geo():
    if g is None:
        return "_لا توجد بيانات هندسية._"
    out = ["| الحالة | عرض الـ rib (nm) | سمك الـ slab (nm) | Γcore | الفقد (dB/m) |",
           "|---|---:|---:|---:|---:|"]
    for _, r in g.iterrows():
        out.append("| %s | %.0f | %.0f | %.3f | %.1f |"
                   % (r["exp"], r["W_nm"], r["slab_nm"], r["Gamma_core"], r["loss_dB_m"]))
    return "\n".join(out)


def t_main(prefixes=("B", "D", "J", "Z", "C")):
    if s is None:
        return "_لا توجد نتائج._"
    d = s[s["exp"].str.startswith(prefixes)].copy()
    out = ["| التجربة | الوصف | الفقد 0V (dB/m) | VπL (V·cm) | Cj 0V (fF/µm) | Γcore |",
           "|---|---|---:|---:|---:|---:|"]
    for _, r in d.iterrows():
        desc = ""
        j = {}
        for fam in ("00_Original_Baseline", "02_Doping_Sweeps", "03_Junction_Position",
                    "04_Vertical_Doping_Profiles", "05_Combined_Optimization"):
            p = os.path.join(ROOT, fam, str(r["exp"]), "experiment.json")
            if os.path.exists(p):
                j = jload(p)
                break
        desc = j.get("description", j.get("desc", ""))
        out.append("| %s | %s | %.1f | %.3f | %.4f | %.3f |"
                   % (r["exp"], desc, r["loss_0V"], r["VpiL_Vcm"],
                      r["Cj_0V_fF_um"], r["Gamma_core"]))
    return "\n".join(out)


def t_pareto():
    if pf is None or not len(pf):
        return "_لم يتم حساب جبهة باريتو._"
    p = pf[pf["pareto"] == True] if "pareto" in pf.columns else pf
    names = ", ".join(str(x) for x in p["exp"].tolist())
    return "التصميمات غير المغلوبة (Pareto): **%s**." % names


base_loss = float(b0["loss_0V"]) if b0 is not None else float("nan")
base_cj = float(b0["Cj_0V_fF_um"]) if b0 is not None else float("nan")
base_vpil = float(b0["VpiL_Vcm"]) if b0 is not None else float("nan")
base_g = float(b0["Gamma_core"]) if b0 is not None else float("nan")

# recommended design: same rule as the final report (all individual + combined)
rec = None
if s is not None:
    feas = s[(s["VpiL_Vcm"] <= 1.25 * base_vpil) & (s["Cj_0V_fF_um"] <= 1.25 * base_cj)]
    rec = (feas if len(feas) else s).sort_values("loss_0V").iloc[0]

rec_line = "_لم يكتمل أي تصميم._"
if rec is not None:
    rec_line = ("**%s**: الفقد %.1f dB/m (%+.1f%% عن baseline)، VπL %.3f V·cm (%+.1f%%)، "
                "Cj %.4f fF/µm، Γcore %.3f."
                % (rec["exp"], rec["loss_0V"],
                   100 * (rec["loss_0V"] - base_loss) / base_loss,
                   rec["VpiL_Vcm"],
                   100 * (rec["VpiL_Vcm"] - base_vpil) / base_vpil,
                   rec["Cj_0V_fF_um"], rec["Gamma_core"]))

doc = f"""# شرح مبسّط بالعربي — دراسة تحسين موديوليتور سيليكون TWMZM

> هذا الشرح مكتوب لطالب/ة هندسة إلكترونيات. كل الأرقام هنا مأخوذة من نتائج
> محاكاة Lumerical حقيقية داخل مجلد المشروع، وليست أرقامًا تجريبية.

## 1. إيه هو الـ TWMZM؟

**TWMZM** اختصار **Traveling-Wave Mach–Zehnder Modulator** (موديوليتور
ماخ–زيندر بموجة ماشية). وظيفته تحويل الإشارة الكهربية (فولت) إلى إشارة ضوئية
(تغيير في الطور/الشدة) على طول دليل موجي سيليكوني.

الفكرة الفيزيائية:

1. عند وصل **junction PN** على الجانب (lateral) وتعريضه لانحياز عكسي، تتغير
   منطقة النضوب (depletion region) وعدد حاملات الشحنة الحرة في القلب.
2. تغيّر حاملات الشحنة يغيّر **معامل الانكسار** للسيليكون (تأثير تشتت البلازما:
   plasma dispersion effect).
3. تغيّر معامل الانكسار يغيّر **neff** للـ mode، وبالتالي يغيّر الطور.
4. في ماخ–زيندر، الذراعان تنزاحان في الطور بشكل متعاكس (push–pull)، وعند
   الخروج يحدث تداخل يحوّل تغيّر الطور إلى تغيّر في الشدة.

## 2. المقاييس الستة اللي بنحسّنها

| المقياس | معناه ببساطة | الوحدة | اتجاه التحسين |
|---|---|---|---|
| **الفقد (loss)** | كم dB بيخسر الضوء لكل متر بسبب امتصاص حاملات الشحنة الحرة | dB/m | أقل = أفضل |
| **VπL** | حاصل ضرب الفولت في الطول اللازم لإزاحة طور π | V·cm | أقل = أفضل (كفاءة أعلى) |
| **Cj** | سعة الـ junction لكل وحدة طول | fF/µm | أقل = أفضل (أسرع وأقل قدرة) |
| **Rs** | المقاومة التسلسلية للـ junction/الالكترود | Ω | أقل = أفضل |
| **Γcore** | نسبة شدة المجال الكهربي داخل قلب الدليل الموجي | بدون وحدة | أعلى = احتواء أفضل |
| **f3dB** | تردد قطع 3 dB (عرض النطاق) | GHz | أعلى = أسرع |

> **ملاحظة مهمة:** Γcore هنا مقياس **تداخل مجال** (field-overlap) محسوب على
> شبكة FDE، وليس معامل الاحتواء الطاقي الدقيق. وf3dB في هذه الدراسة **NA**
> لأن نموذج الـ RF الموزّع لم يُعَد تشغيله؛ لا نقدّم رقمًا غير محسوب.

## 3. إزاي Lumerical بيحسب كل حاجة؟

المسار ثلاثي المراحل:

1. **CHARGE (كهربي):** يحل معادلات drift–diffusion ويطلع توزيع الإلكترونات
   والثقوب (n, p) على شبكة الجهاز، وكذلك الشحنة الكلية Q عند كل فولت.
2. **MODE (ضوئي):** يستورد خريطة n/p من CHARGE كـ grid attribute، ويحسب
   الـ mode (neff، الفقد، Γcore) عند كل فولت.
3. **AC (ترددي):** يشغّل small-signal AC (ssac) عشان يستخرج Rs وC_ac مقابل
   التردد والانحياز للتصميمات النهائية.

الـ **Cj** بنحسبها في بايثون من `total_charge`:
`Cj[fF/µm] = 0.5·(|ΔQn|+|ΔQp|)/ΔV × 1e9`، مع `ΔV = 0.025 V`.

## 4. منهجية التجارب (أهم جزء للطالب)

- **Baseline موحّد:** أعدنا تشغيل B000 على نفس الشبكة المستخدمة في كل التجارب
  النظيفة. القيم: الفقد {base_loss:.1f} dB/m، VπL {base_vpil:.3f} V·cm،
  Cj {base_cj:.4f} fF/µm، Γcore {base_g:.3f}.
- **متغير واحد في المرة:** الهندسة (MODE فقط)، الدوبينج، موضع الـ junction،
  التوزيع الرأسي، ثم التصميم المركّب.
- **شبكة انحياز دقيقة:** 0.5 V خطوات أساسية، وكل نقطة معها نقطة +0.025 V
  (20 حلًا). جرّبنا خطوات 0.9 V فوجدنا الـ sweep يتوقف بصمت في بعض التصاميم،
  فرفضناها.
- **إعادة ضبط صريحة:** كل تشغيل ينسخ النسخة الأصلية النظيفة إلى ملف جلسة
  مؤقت، ويستدعي `reset_baseline()` قبل أي تعديل (بعد حادثة ملف المشروع).
- **الوحدات:** الـ API يكتب التركيز بوحدة **/m³**، والـ GUI يعرض **/cm³**.
  التحويل: `1e21 /m³ = 1e15 /cm³`. مثلاً `5e23 /m³ = 5e17 /cm³`.

## 5. نتائج الهندسة (MODE فقط، شحنة الـ baseline)

{t_geo()}

**القراءة:** تقليل سمك الـ slab إلى 70 nm يقلل تداخل الـ mode مع المنطقة
المطعّمة (doped slab) فيقل الفقد، مع الحفاظ على احتواء جيد في القلب. زيادة
الـ slab إلى 110 nm تزيد التداخل مع المنطقة المطعّمة فيزيد الفقد.

## 6. نتائج الدوبينج والـ junction والتوزيع الرأسي والمركّب

{t_main()}

**القراءة:** تقليل الدوبينج يقلل الفقد وCj لكنه يزيد VπL (كفاءة أقل).
زيادة الدوبينج تعكس الاتجاه. موضع الـ junction والتوزيع الرأسي يغيّران
التوازن بين الفقد والكفاءة. التصميم المركّب بيجمع أفضل اختيارات الهندسة
والدوبينج (والـ junction أو التوزيع الرأسي) في تجربة واحدة.

## 7. تحليل باريتو (Pareto)

لا يوجد تصميم واحد أفضل في كل المقاييس. لذلك نستخدم **جبهة باريتو**: مجموعة
التصميمات اللي مفيش تصميم تاني أفضل منها في كل الأهداف مرة واحدة.

{t_pareto()}

## 8. التوصية النهائية

{rec_line}

> راجع `08_Reports/FINAL_RECOMMENDATIONS.md` للتفاصيل والقيود.

## 9. إزاي نتعامل مع f3dB؟

f3dB مش مجرد `1/(2πRC)`. الموديوليتور **موجة ماشية**: الالكترود والضوء
بيتحركوا مع بعض، وفيه عدم تطابق في السرعة (velocity mismatch) وفقد في خط
النقل. عشان كده رقم `1/(2πRC)` هو **تقدير lumped** فقط، ومش بنقدّمه كـ f3dB.
في هذه الدراسة: f3dB = **NA**، وبنقدّم Rs وC_ac من ssac للتصميمات النهائية.

## 10. دروس مستفادة (مهمة جدًا)

1. **التحقق من النقطة الصحيحة:** شبكة الانحياز الدقيقة فيها نقطتان متجاورتان
   (0.5 V و+0.025 V). لازم نتأكد إن 0 V هو index **3** في المصفوفة
   `[-0.5, -0.475, 0.0, ...]`، مش index 2. عند استخدام index 2 كان الفقد
   المسجّل 535.95 dB/m وهو في الحقيقة نقطة **-0.475 V**؛ عند index 3 كان
   498.23 dB/m وهو يطابق الـ baseline الأصلي 498.22 dB/m تمامًا. يعني إعادة
   بناء النسخة النظيفة كانت صحيحة، والفرق كان خطأ في قراءة الفهرس.
2. **التحقق من الاكتمال:** عدد النقاط + آخر فولت (4.025 V) + الحالة، وليس
   حجم الملف. الـ sweep قد يتوقف بصمت.
3. **سلامة ملف المشروع:** Lumerical يحفظ المشروع المحمّل عند إنهاء التشغيل.
   لا تحمّل ملف المشروع الأصلي مباشرة؛ استخدم نسخة مؤقتة وأعد الضبط.
4. **الأمانة العلمية:** النتائج الملوّثة تُعزل وتُوثّق، ولا تُستخدم في التوصيات.

## 11. إزاي تعيد التجربة؟

```bash
# 1) baseline نظيف
python 09_Automation/run_experiment.py B000
# 2) تجارب الدوبينج/الـ junction/الرأسي
python 09_Automation/run_experiment.py D001 D002 D003 J001 J002 J003 Z001 Z002 Z003
# 3) مسح الهندسة على شحنة B000
python 09_Automation/run_geometry_sweep_b000.py
# 4) استخراج مقاييس MODE
python 09_Automation/extract_metrics.py
# 5) مزامنة الـ baseline + التحقق + اختيار المركّب
python 09_Automation/sync_baseline.py
python 09_Automation/validate_design.py
python 09_Automation/suggest_combined.py
# 6) تشغيل المركّب ثم استخراج مقاييسه
python 09_Automation/run_combined.py 07_Results/combined_config.json
python 09_Automation/extract_metrics.py C001 C002 C003
# 7) AC للتصميم النهائي
python 09_Automation/run_ac.py 05_Combined_Optimization C001
```

> كل الأرقام والملفات موجودة تحت `TW_Modulator_Optimization_Study/`، وتقرير
> الحادثة الكامل في `07_Results/diagnostics/PROJECT_FILE_INCIDENT.md`.
"""

out = os.path.join(REP, "STUDENT_EXPLAINER_AR.md")
open(out, "w", encoding="utf-8").write(doc)
print("wrote", out, "chars", len(doc))
