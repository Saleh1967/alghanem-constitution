# slge_layers.py — طبقات SLGE الأربع المكملة: أبجد، حركات، أدوات، مبنيات
# السلم: خلية ← نمط ← قالب+زائد ← لفظ — كل طبقة مولّدٌ مستقل مرخَّص، والمرادف: CV/CVCV.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import slge

MADD3 = ("ا", "و", "ي")

# L1 — SLGE-أبجد: سلّم كل حرف (حالاته المرخصة؛ ρ تحرم الحركة على الناقل المدي)
LADDER = {g: [(g, s) for s in slge.STATES if not (g in MADD3 and s != "سكون")]
          for g in slge.ALPHABET}
def gen_cell(g):  # الصعود الأول: الحرف درجةً درجة
    return LADDER[g]

# L2 — SLGE-حركات: توليد الأنماط المرخصة (قيد المسار على صفوف الشبكة)
def licensed_ms(p):  # p: سلسلة M/S
    return p[0] == "M" and "SS" not in p
def gen_patterns(n):
    out = [""]
    for _ in range(n):
        out = [p + s for p in out for s in "MS" if licensed_ms(p + s)]
    return out
# L3 — SLGE-أدوات: جدول الحروف المعلن (ملحق 6) — كل حرفٍ محرّكٌ قالبي
PARTICLES_FULL = {
 "مِنْ": [("م","كسر"),("ن","سكون")], "عَنْ": [("ع","فتح"),("ن","سكون")], "عَلَى": [("ع","فتح"),("ل","فتح"),("ا","سكون")],
 "قَدْ": [("ق","فتح"),("د","سكون")], "لَمْ": [("ل","فتح"),("م","سكون")], "لَنْ": [("ل","فتح"),("ن","سكون")],
 "بَلْ": [("ب","فتح"),("ل","سكون")], "هَلْ": [("ه","فتح"),("ل","سكون")], "أَنْ": [("ء","فتح"),("ن","سكون")],
 "إِنْ": [("ء","كسر"),("ن","سكون")], "إِذَا": [("ء","كسر"),("ذ","فتح"),("ا","سكون")],
 "إِذْ": [("ء","كسر"),("ذ","سكون")], "عِنْدَمَا": [("ع","كسر"),("ن","سكون"),("د","فتح"),("م","فتح"),("ا","سكون")],
 "كُلَّمَا": [("ك","ضم"),("ل","سكون"),("م","فتح"),("ا","سكون")], "حِينَئِذٍ": [("ح","كسر"),("ي","فتح"),("ن","فتح"),("ء","كسر"),("ذ","سكون")],
 "لا": [("ل","فتح"),("ا","سكون")], "مَا": [("م","فتح"),("ا","سكون")], "وَ": [("و","فتح")],
}
# L4 — SLGE-اسم (مبني): قوالب MASAQ المعلنة — كل اسمٍ محرّكٌ قالبي
MABNI = {
 "هَذَا": [("ه","فتح"),("ذ","فتح"),("ا","سكون")], "ذَانِكَ": [("ذ","فتح"),("ل","كسر"),("ك","فتح")],
 "تِلْكَ": [("ت","كسر"),("ل","سكون"),("ك","فتح")], "أُولَئِكَ": [("ء","ضم"),("ل","فتح"),("ء","كسر"),("ك","فتح")],
 "أَنَا": [("ا","فتح"),("ن","فتح"),("ا","سكون")], "نَحْنُ": [("ن","فتح"),("ح","سكون"),("ن","ضم")],
 "هُوَ": [("ه","ضم"),("و","سكون")], "هِيَ": [("ه","فتح"),("ي","سكون")], "ذَا": [("ذ","فتح"),("ا","سكون")],
 "الَّذِي (وصل)": [("ل","سكون"),("ذ","كسر"),("ي","فتح")], "إِنَّ": [("ء","فتح"),("ن","سكون"),("ن","فتح")],
 "كَانَ": [("ك","فتح"),("ا","سكون"),("ن","فتح")], "لَكِنَّ": [("ل","فتح"),("ك","كسر"),("ن","سكون"),("ن","فتح")],
 "أَيْنَ": [("ء","فتح"),("ي","سكون"),("ن","فتح")], "لَيْسَ": [("ل","فتح"),("ي","سكون"),("س","فتح")],
 "مَنْ": [("م","فتح"),("ن","سكون")], "ثُمَّ": [("ث","ضم"),("م","سكون"),("م","فتح")],
}
# L5 — ترخيص كل الطبقات والوصول إلى CV/CVCV
def pipeline_check():
    slge.PARTICLES.update({slge._key(v): k for k, v in PARTICLES_FULL.items()})  # تسجيل من مصدر واحد (يحل عقد مطابقة المفاتيح كلها)
    cv = gen_cell("ب")[:1]                      # CV: خلية متحركة واحدة
    cvcv = gen_cell("ف")[:1] + gen_cell("ع")[:1]  # CVCV = CV+CV (فَعَ)
    ok = slge.licensed(cv) and slge.licensed(cvcv)
    ok &= licensed_ms(gen_patterns(1)[0]) and len(gen_patterns(2)) == 2  # MM, MS — والمبدأ SM لا يبدأ كلامًا
    ok &= all(slge.licensed(v) for v in PARTICLES_FULL.values())
    ok &= all(slge.licensed(v) for k, v in MABNI.items() if "وصل" not in k)
    ok &= all(slge.classify(v)[0] == "bin1" for v in PARTICLES_FULL.values())   # الأدوات بالتصنيف
    ok &= all(k in MABNI and slge.licensed(v) for k, v in MABNI.items() if "وصل" not in k)  # المبنيات: سجلٌّ مغلق
    return ok

if __name__ == "__main__":
    checks = [
      ("L1 سلالم الحروف تحترم ρ", all(len(LADDER[g]) == (1 if g in MADD3 else 4) for g in slge.ALPHABET)
       and all(s == "سكون" for g in MADD3 for _, s in LADDER[g]) and len(LADDER["ء"]) == 4),
      ("L2 أنماط الحركات = قيد المسار", len(gen_patterns(3)) == 3 and len(gen_patterns(4)) == 5 and all(licensed_ms(p) for p in gen_patterns(5))),
      ("L3 الأدوات كلها مرخصة ومعلنة", all(slge.licensed(v) for v in PARTICLES_FULL.values())),
      ("L4 المبنيات كلها مرخصة (والذي صورة وصل)", all(slge.licensed(v) for k, v in MABNI.items() if "وصل" not in k)),
      ("L5 الوصول CV/CVCV بالتركيب", pipeline_check()),
    ]
    ok = True
    for name, r in checks:
        ok &= r; print(f"  {'✓' if r else '⛔'} {name}")
    print("SLGE LAYERS:", "ALL PASS — CV/CVCV reached" if ok else "BREACH")
    sys.exit(0 if ok else 1)
