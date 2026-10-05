# slge_unicode.py — SLGE-ترميز: طبقة يونيكود/UTF-8 تحت الإملاء، تحسم التعارض والتوافيق
# القاعدة: لا خانةَ إلا بمقترنةٍ قانونيةٍ واحدة (NFC)؛ ولا حرفَ خارج الجدول المعلن.
import unicodedata, pathlib, sys

CANON = {  # الحوامل الـ29 بنقاطها القانونية
 "ء":"U+0621","ا":"U+0627","ب":"U+0628","ت":"U+062A","ث":"U+062B","ج":"U+062C","ح":"U+062D","خ":"U+062E",
 "د":"U+062F","ذ":"U+0630","ر":"U+0631","ز":"U+0632","س":"U+0633","ش":"U+0634","ص":"U+0635","ض":"U+0636",
 "ط":"U+0637","ظ":"U+0638","ع":"U+0639","غ":"U+063A","ف":"U+0641","ق":"U+0642","ك":"U+0643","ل":"U+0644",
 "م":"U+0645","ن":"U+0646","ه":"U+0647","و":"U+0648","ي":"U+064A"}
MARKS = {"ً":"U+064B","ٌ":"U+064C","ٍ":"U+064D","َ":"U+064E","ُ":"U+064F","ِ":"U+0650","ّ":"U+0651","ْ":"U+0652"}
# جدول التوافيق: المخالفة → القانوني (مغلق، بالاسم)
SINS = {"ک":"ك", "ی":"ي", "ك":"ك", "د":"د", "أ":"أ", "إ":"إ", "آ":"آ", "ؤ":"ؤ", "ئ":"ئ",
        "ة":"ة", "ى":"ى", "ٱ":"ٱ", "ـ":None, "ٰ":None, "ﻻ":"لا"}
OUTSIDE = set("ﷺﷻ")

def normalize(s):
    for bad, good in SINS.items():
        if good is None: s = s.replace(bad, "")
        elif bad != good: s = s.replace(bad, good)
    return unicodedata.normalize("NFC", s)

def conflicts(s):
    """كاشف التعارض: يقرأ نصًّا ويُخرج ما خالف القانون (اسمًا وموضعًا)"""
    s0 = s
    fixed = normalize(s)
    found = []
    for ch in set(s0):
        if ch in SINS and SINS[ch] not in (None, ch):
            found.append((f"U+{ord(ch):04X} {ch!r} → {SINS[ch]!r}", s0.count(ch)))
        elif ch in OUTSIDE:
            found.append((f"U+{ord(ch):04X} {ch!r} محظور", s0.count(ch)))
    return found, fixed

def audit_file(path):
    raw = pathlib.Path(path).read_text(encoding="utf-8")
    allowed = set(CANON) | set(MARKS) | set(" \n\t،؛.()[]{}:;،«»'\"-–—0123456789=<>|/\\_*#%$&+@!?؟") | set(SINS)
    bad = sorted({f"U+{ord(c):04X} {c!r}" for c in raw
                  if "؀" <= c <= "ۿ" and c not in allowed})  # الفضاء العربي فقط؛ الرياضيات خارج اختصاصه
    return bad

if __name__ == "__main__":
    ok = True
    # Q15: التطبيع متسق الأثر ومتعدد التطبيق
    t = "کِتَاب يَد خَالِد ـٰ"
    n1, n2 = normalize(t), normalize(normalize(t))
    q15 = n1 == n2 and "ک" not in n1 and "ـ" not in n1
    ok &= q15; print(f"  {'✓' if q15 else '⛔'} Q15 التطبيع متسق الأثر (idempotent)")
    # Q16: الكاشف يلتقط المحقونات
    found, _ = conflicts("ک ی ک")
    q16 = sum(n for _, n in found) == 3
    ok &= q16; print(f"  {'✓' if q16 else '⛔'} Q16 كاشف التعارض يلتقط المحقونات ({len(found)})")
    # Q17: مسح ملفات المحرك: لا حرف خارج الجدول القانوني
    base = pathlib.Path(__file__).resolve().parent
    sins_all = []
    for f in ["slge.py", "slge_layers.py", "slge_laws.py", "algebra116.py"]:
        bad = audit_file(base / f)
        if bad: sins_all.append((f, bad[:4]))
    q17 = not sins_all
    ok &= q17
    print(f"  {'✓' if q17 else '⛔'} Q17 مسح ملفات المحرك خالٍ من خارج الجدول: {sins_all if sins_all else 'نظيف'}")
    print("SLGE-UNICODE:", "ALL PASS — encoding layer closed" if ok else "DEBTS FOUND (named above)")
    sys.exit(0 if ok else 1)
