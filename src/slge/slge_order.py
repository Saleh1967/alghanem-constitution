# slge_order.py — دستور الترتيب: اثنا عشر طبقة، منع القفز بالبصمة، التمييز بالبصمة لا بالمعرفة
import sys, pathlib, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import slge

def stamp(cells):  # بصمة البناء: الخلية الكاملة لا ظل المقطع
    return hashlib.sha256(str(tuple(cells)).encode("utf-8")).hexdigest()[:12]

# العمود الفقري: (الطبقة، شرطها) — لا تسبق إلا أختها
LAYERS = [("البتات", None), ("اليونيكود", "البتات"), ("الترميز العثماني", "اليونيكود"),
          ("الإملاء", "الترميز العثماني"), ("المبنيات", "الإملاء"), ("الفعل", "المبنيات"),
          ("الوزن", "الفعل"), ("المعتل", "الوزن"), ("الجذع", "المعتل"),
          ("المشتق", "الجذع"), ("الموضع", "المشتق"), ("الإعراب", "الموضع")]
NAME2IDX = {n: i for i, (n, _) in enumerate(LAYERS)}

def no_leap(name, verified):
    """بوابة منع القفز: لا تُبنى طبقةٌ قبل بصمة شرطها خضراء"""
    i = NAME2IDX[name]
    need = LAYERS[i][1]
    return need is None or need in verified

def build(name, verified):
    if not no_leap(name, verified):
        raise AssertionError(f"قفزٌ جبريٌّ ممنوع: {name} قبل {LAYERS[NAME2IDX[name]][1]}")
    return stamp([(name, "بُني")])

# الدمج: همزة + لام = ال (بخاصية الوصل H5)؛ والإشارة ثلاثي الأضواء على الحركات الثلاث
FUSION = {"ال": [("ا","سكون"),("ل","سكون")],   # همزة الوصل + لام، مقعدها الهمزة (H5)
          "ذا": [("ذ","فتح"),("ا","سكون")], "ذِي": [("ذ","كسر"),("ي","سكون")], "ذُو": [("ذ","ضم"),("و","سكون")]}
# البصمة لا المعرفة: الثلاثة بصماتها تفرّق ولا يفرّقها ظل المقطع
DEMO = {"اللَّذَانِ": [("ل","سكون"),("ذ","فتح"),("ا","سكون"),("ن","ضم")],
        "اللَّذَيْنِ": [("ل","سكون"),("ذ","فتح"),("ي","سكون"),("ن","كسر")],
        "الَّذِينَ":  [("ل","سكون"),("ذ","كسر"),("ي","سكون"),("ن","فتح")]}

if __name__ == "__main__":
    ok = True
    # Q21a العمود الفقري سليم: لا دورات، وكل شرطٍ سابقٌ على طبقته
    acyclic = all(LAYERS[i][1] is None or NAME2IDX[LAYERS[i][1]] < i for i in range(len(LAYERS)))
    ok &= acyclic; print(f"  {'✓' if acyclic else '⛔'} Q21a العمود الفقري 12 طبقة بلا دورة ولا سبق")
    # Q21b منع القفز: الإعراب قبل الموضع تُرفض، وبعده تُقبل
    try:
        build("الإعراب", {"البتات"}); q21b = False
    except AssertionError:
        q21b = True
    q21b &= (build("الإعراب", {"الموضع"}) == stamp([("الإعراب","بُني")]))
    ok &= q21b; print(f"  {'✓' if q21b else '⛔'} Q21b منع القفز جبريًّا: الإعراب لا يُبنى قبل بصمة الموضع")
    # Q21c الدمج مرخّص: ال من همزة+لام (بعد الوصل)، والإشارة ثلاثيها متمايز
    art = slge.wasl_join([("ب","كسر")], FUSION["ال"] + [("ک" if False else "ك","فتح"),("ت","فتح"),("ب","فتح")])
    q21c = slge.licensed(art) and slge.licensed(FUSION["ذا"]) and slge.licensed(FUSION["ذِي"]) and slge.licensed(FUSION["ذُو"])
    q21c &= len({stamp(v) for v in [FUSION["ذا"], FUSION["ذِي"], FUSION["ذُو"]]}) == 3
    ok &= q21c; print(f"  {'✓' if q21c else '⛔'} Q21c الدمج: همزة+لام=ال (بالوصل) وذا/ذِي/ذُو بثلاث بصمات")
    # Q21d البصمة لا المعرفة: الثلاثة أشكال بصماتٌ متميزة، والظل M/S لا يفرّق ذَيْن عن ذِين
    st = {k: stamp(v) for k, v in DEMO.items()}
    pats = {"".join("M" if s != "سكون" else "S" for _, s in v) for v in DEMO.values()}
    q21d = len(set(st.values())) == 3 and slge.licensed([("ب","كسر")] + DEMO["اللَّذَيْنِ"]) \
           and len(pats) < 3  # الظل يعجز — والبصمة تفرّق ببِتّين (حركة الذال وحرف النون)
    ok &= q21d
    print(f"  {'✓' if q21d else '⛔'} Q21d اللَّذَانِ/اللَّذَيْنِ/الَّذِينَ: {list(st.values())} — بالبصمة لا بالمعرفة")
    print("SLGE-ORDER:", "ALL PASS — no leaps, fingerprints rule" if ok else "BREACH")
    sys.exit(0 if ok else 1)
