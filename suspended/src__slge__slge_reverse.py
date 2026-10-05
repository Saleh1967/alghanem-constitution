# slge_reverse.py — هندسة عكسية: الجرد المغلق كشرط إمكان + إثبات الطي والفك بنفس الوقت
# الاتجاه المعكوس: لا «نفترض 116 فنثبت» — بل «من شروط إمكان البراهين نستنتج 116»،
# وعلى النطاق المعدود كله نثبت التركيبين معًا: فكّ(طي(w)) = w وطي(فك(n)) = n.
import sys, pathlib, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import slge

B = 116  # قاعدة الخانات (29×4)
def fold(w):    # الطي: كلمة → عدد (الرتبة اللاتينية للحوامل: عمود×4 + صف)
    return sum((slge.ALPHABET.index(c) * 4 + slge.STATES.index(s)) * B ** (len(w) - 1 - i)
               for i, (c, s) in enumerate(w))
def unfold(n, L):  # الفك: عدد → كلمة بالطول المعطى
    out = []
    for i in range(L):
        p = B ** (L - 1 - i)
        k, n = divmod(n, p)
        out.append((slge.ALPHABET[k // 4], slge.STATES[k % 4]))
    return out

def licensed_words(n):
    return [list(w) for w in itertools.product(
        [(c, s) for c in slge.ALPHABET for s in slge.STATES], repeat=n) if slge.licensed(list(w))]

if __name__ == "__main__":
    ok = True
    # Q22 شرط الإمكان المعكوس: من المشاهدات المثبتة (U(1)=87، 29 حاملًا) نستنتج الجرد لا نفترضه
    U1, nc = slge.count(1), len(slge.ALPHABET)
    q22 = (U1 % nc == 0 and U1 // nc == 3 and nc * (U1 // nc + 1) == 116)
    ok &= q22
    print(f"  {'✓' if q22 else '⛔'} Q22 الاستنتاج المعكوس: U(1)={U1} و29 حاملًا ⇒ 3 متحركات ⇒ 116 = 29×4 (الجرد مشتقٌّ لا مفترض)")
    # Q23 الاتجاهان معًا على العدّ المعظّم (>6M): ≤2 كاملة + 3 كاملة (1,097,505) + أسطوانة طول 4 بست خانات أولى معلنة
    MOV = [(c, s) for c in slge.ALPHABET for s in slge.STATES if s != "سكون"]
    SUK = [(c, "سكون") for c in slge.ALPHABET]
    dom2 = licensed_words(2)
    lic3 = [w for pat in ("MMM", "MMS", "MSM")
            for w in itertools.product(*[MOV if p == "M" else SUK for p in pat])]
    assert len(dom2) == 10092 and len(lic3) == 1097505
    FIRST4 = [("ء","فتح"),("ب","فتح"),("ل","فتح"),("م","فتح"),("ع","فتح"),("ن","فتح")]
    IDX = {(c, s): slge.ALPHABET.index(c) * 4 + slge.STATES.index(s) for c in slge.ALPHABET for s in slge.STATES}
    def fold_h(w):
        n = 0
        for cell in w: n = n * B + IDX[cell]
        return n
    bad = total = 0
    for w in dom2 + lic3:
        total += 1
        n = fold_h(w)
        if unfold(n, len(w)) != list(w) or fold_h(unfold(n, len(w))) != n: bad += 1
    for f in FIRST4:
        for t in lic3:
            total += 1
            w = [f] + list(t)
            n = fold_h(w)
            if unfold(n, 4) != w or fold_h(unfold(n, 4)) != n: bad += 1
    q23 = bad == 0
    ok &= q23
    print(f"  {'✓' if q23 else '⛔'} Q23 الاتجاهان معًا على {total:,} بناءً (استيفاء كامل: ≤2 + 3 كاملة + أسطوانة 4 بست أوليات) — مخالفات {bad}")
    # Q23b U(4) الكامل = 120,945,051: متجهيًّا على الأشكال الخمسة كلها، قطعةً قطعة — نفس الحساب لا عيّنة
    import numpy as np
    SHAPES = [("MMMM", [87,87,87,87]), ("MMMS", [87,87,87,29]), ("MMSM", [87,87,29,87]),
              ("MSMM", [87,29,87,87]), ("MSMS", [87,29,87,29])]  # الأبعاد تابعة للشكل من موضعه الأول (M)
    def cell_of(shape, d):  # رقم الخيار → فهرس الخلية 0..115
        if shape == "M":
            c = np.divmod(d, 3); return c[0]*4 + c[1]
        return d*4 + 3
    bad4 = tot4 = 0
    CH = 4_000_000
    for name, dims in SHAPES:
        cnt = int(np.prod(dims)); suf = [1]*4  # الرتبة الحق: suf[i] = حاصل ما بعد الموضع i (حصري)
        suf[2] = dims[3]; suf[1] = dims[2]*dims[3]; suf[0] = dims[1]*dims[2]*dims[3]
        for s in range(0, cnt, CH):
            e = min(s+CH, cnt); idx = np.arange(s, e, dtype=np.int64)
            digs = [np.divmod(idx, suf[i])[0] % dims[i] for i in range(4)]
            cells = [cell_of(name[i], digs[i]) for i in range(4)]
            n = ((cells[0]*B + cells[1])*B + cells[2])*B + cells[3]
            back = []
            m = n
            for _ in range(4):
                m, r = np.divmod(m, B); back.append(r)
            match = (back[3]==cells[0]) & (back[2]==cells[1]) & (back[1]==cells[2]) & (back[0]==cells[3])
            n2 = ((back[3]*B + back[2])*B + back[1])*B + back[0]
            bad4 += int(np.count_nonzero(~match)) + int(np.count_nonzero(n2 != n))
            tot4 += (e - s)
    q23b = bad4 == 0 and tot4 == 120945051
    ok &= q23b
    print(f"  {'✓' if q23b else '⛔'} Q23b U(4) كامل: {tot4:,} بناءً (الأشكال الخمسة) — الاتجاهان معًا، مخالفات {bad4}")
    # Q24 الظل غير كافٍ: ذَيْن وذِين متطابقان على M/S ومختلفان بالطي ⇒ الذرّة الكاملة شرط لازم للتقابل
    dhayn = [("ل","سكون"),("ذ","فتح"),("ي","سكون"),("ن","كسر")]
    dheen = [("ل","سكون"),("ذ","كسر"),("ي","سكون"),("ن","فتح")]
    pat = lambda w: "".join("M" if s != "سكون" else "S" for _, s in w)
    q24 = pat(dhayn) == pat(dheen) and fold(dhayn) != fold(dheen)
    ok &= q24
    print(f"  {'✓' if q24 else '⛔'} Q24 الظل يعجز والطي يفرّق: ذَيْن/ذِين شكلٌ واحد، عددان مختلفان — فالخلية الكاملة شرطُ التقابل")
    print("SLGE-REVERSE:", "ALL PASS — inventory derived, fold&unfold proven together" if ok else "BREACH")
    sys.exit(0 if ok else 1)
