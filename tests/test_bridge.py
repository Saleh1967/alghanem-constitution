import pathlib, sys, csv, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"src/slge"))
import slge

ADMITTED = {"WELL_TYPED", "MODEL_ADMISSIBLE"}            # أحكام القبول المعلنة
SUSPENDED_NAMED = {"VOWELS_DIFFER", "BASE_NOT_CV"}       # مخزون أسباب التعليق المغلق

def test_alphabet_canonical():
    assert len(slge.ALPHABET) == 29 and len(set(slge.ALPHABET)) == 29 and slge.ALPHABET[0] == "ء"
def test_cells_116():
    assert len([(c,s) for c in slge.ALPHABET for s in slge.STATES]) == 116
def test_audit_dispositions():
    with open(ROOT/"data/candidate_audit.csv", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    stages = collections.Counter(r["stage"] for r in rows)
    assert stages == {"ATOM": 116, "CVV": 348, "CVC": 3364}
    # لا حكم مجهول ولا غير مسموح: كل صفٍّ حكمُه من المخزون المغلق (قبول معلن + تعليق بسبب مسمّى)
    models = collections.Counter(r["model"].strip() for r in rows)
    assert set(models) <= ADMITTED | SUSPENDED_NAMED
    suspended = [r for r in rows if r["model"].strip() not in ADMITTED]
    assert all(r["model"].strip() in SUSPENDED_NAMED for r in suspended)   # لا تعليق مجهول
    assert len(suspended) == 174 + 928                                     # 1,102 معلقة بالاسم
    assert sum(models.values()) == 3828 == 2726 + 1102                     # قبول + تعليق = الكل
