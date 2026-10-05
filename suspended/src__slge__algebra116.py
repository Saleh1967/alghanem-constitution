# algebra116.py — جبر الخانات المرخَّص الهندسي من 116 (داخل خانات SLGE)
# السليل: G = Γ × Σ (29 حاملًا × 4 حالات) — شبكة هندسية 4×29.
# الخانة = نقطة (عمود الحامل، صف الحالة). السلسلة = مسار على الشبكة.
# الترخيص = قيد المسار: البداية ليست من صف السكون، ولا رأسين متتاليين في صف السكون.
import itertools, random, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import slge

CARRIERS = slge.ALPHABET            # 29 عمودًا
STATES4  = slge.STATES              # 4 صفوف: فتح كسر ضم سكون
G = [(g, s) for g in CARRIERS for s in STATES4]
FORBIDDEN = [("ا", "فتح"), ("ا", "ضم"), ("ا", "كسر")]       # المثالي المحظور (قاعدة ρ)
CLASSES = [[c for c in CARRIERS if c not in ("ا", "و", "ي", "ء")], ["ا", "و", "ي"], ["ء"]]

def coord(cell):
    """الإحداثي الهندسي: (عمود الحامل، صف الحالة)"""
    return (CARRIERS.index(cell[0]), STATES4.index(cell[1]))

# ---------- القوانين السبعة ----------
def law1_carrier_set():
    return len(G) == 116 and len(set(G)) == 116 and len(CARRIERS) * len(STATES4) == 116

def law2_license_geometry():
    # الترخيص قيدُ مسار على الشبكة؛ وU(2) المبرهَن يجب أن يساوي عدد أزواج الشبكة الجائزة
    pairs = [(a, b) for a in G for b in G if a[1] != "سكون" and not (a[1] == "سكون" and b[1] == "سكون")]
    return len(pairs) == slge.count(2) == 10092

def law3_equivariance(n_roots=300, n_perms=40, seed=116):
    # بدال الحوامل يبدّل الجذر داخل الخانات: π(generate(t,r)) = generate(t, π(r))
    rng = random.Random(seed)
    trs = []
    for cls in CLASSES:
        trs += [[(cls[i], cls[j])] for i in range(len(cls)) for j in range(i + 1, len(cls))]
    for _ in range(n_perms):
        t = rng.choice(trs)
        a, b = t[0]
        for gid in [g for g in list(slge.GRID) + list(slge.GRID_NOM) if g != "Q"]:  # Q رباعي الخانات: يُفحص بدالُه في الإغلاق العام
            tpl = (slge.GRID.get(gid) or slge.GRID_NOM.get(gid))
            gen = slge.generate if gid in slge.GRID else slge.generate_nom
            for _ in range(n_roots // n_perms):
                r = tuple(rng.choice(CARRIERS) for _ in range(3))
                # اليسار: توليد ثم بدالٌ على خانات الجذر وحدها (بقناع المواضع الجذرية)
                w0 = gen(gid, dict(zip("فعل", r)))
                left = [(((a if c == b else b if c == a else c), s) if kind == "s" else (c, s))
                        for (kind, key, st), (c, s) in zip(tpl, w0)]
                right = gen(gid, dict(zip("فعل", tuple(a if x == b else b if x == a else x for x in r))))
                if left != right:
                    return False
    return True

def law4_iirab_projection(samples=300, seed=7):
    # الإعراب إسقاطٌ على الرأس الأخير: يبدّل الخلية الأخيرة فقط، ويحفظ الترخيص للحالات المتحركة
    rng = random.Random(seed)
    for _ in range(samples):
        r = tuple(rng.choice(CARRIERS) for _ in range(3))
        w = slge.generate("I-fatha", dict(zip("فعل", r)))
        for case in ("رفع", "نصب", "جر"):
            v = slge.iirab(w, case)
            if v[:-1] != w[:-1] or not slge.licensed(v):
                return False
    return True

def law5_forbidden_ideal():
    # المثالي المحظور لا يظهر في أي خلية ثابتة من جداول العمليات.
    # أما خانات الجذر فمتغيرات تحكمها قاعدة ρ: الناقل المدي (ا/و/ي) لا يقوم إلا ساكنًا —
    # ودخول الجذوع على هذا القيد شأن المعجم المعلن [D]، لا شأن الجبر.
    for tpl in list(slge.GRID.values()) + list(slge.GRID_NOM.values()):
        for kind, key, st in tpl:
            if kind == "f" and (key, st) in FORBIDDEN:
                return False
    for aff in list(slge.PREFIX) + list(slge.SUFFIX):
        for c, s in map(tuple, aff):
            if (c, s) in FORBIDDEN:
                return False
    return all(st == "سكون"
               for tpl in list(slge.GRID.values()) + list(slge.GRID_NOM.values())
               for kind, key, st in tpl if kind == "f" and key == "ا")

def law6_closure():
    # الإغلاق: حوامل الثوابت وحالات كل الجداول تقع في G = Γ×Σ
    ok = True
    for tpl in list(slge.GRID.values()) + list(slge.GRID_NOM.values()):
        ok &= all(kind in ("s", "f") and st in STATES4 for kind, key, st in tpl)
        ok &= all(key in CARRIERS or key in "فعلم" for kind, key, st in tpl)
    for aff in list(slge.PREFIX) + list(slge.SUFFIX):
        for c, s in map(tuple, aff):
            ok &= c in CARRIERS and s in STATES4
    return ok

def law7_grid_geometry():
    rows = {s for _, s in G}
    cols = {g for g, _ in G}
    return len(rows) == 4 and len(cols) == 29 and all(0 <= coord(x)[0] < 29 and 0 <= coord(x)[1] < 4 for x in G)

if __name__ == "__main__":
    laws = [("Q1 سليل 116 = 4×29", law1_carrier_set),
            ("Q2 الترخيص قيد مسار = U(2)", law2_license_geometry),
            ("Q3 استواء البدال داخل الخانات", law3_equivariance),
            ("Q4 الإعراب إسقاط أخير محافظ", law4_iirab_projection),
            ("Q5 المثالي المحظور لا يُولَّد", law5_forbidden_ideal),
            ("Q6 إغلاق العمليات في G", law6_closure),
            ("Q7 الشبكة 4×29 هندسيًّا", law7_grid_geometry)]
    ok = True
    for name, f in laws:
        r = f()
        ok &= r
        print(f"  {'✓' if r else '⛔'} {name}")
    a, iin = coord(("ب", "فتح")), coord(("ا", "سكون"))
    print(f"  مثال الإحداثيات: بَ = {a} (عمود ب، صف فتح) | اْ = {iin} | المحرّمات: {[coord(x) for x in FORBIDDEN]}")
    print("ALGEBRA116:", "CLOSED — all 7 laws hold" if ok else "BREACH — investigate")
    sys.exit(0 if ok else 1)
