# -*- coding: utf-8 -*-
"""Tests for the frozen qiyas vocabulary + golden standard (الغانم — الدال)."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ist = json.loads((ROOT / "data" / "qiyas_istilahat.json").read_text(encoding="utf-8"))
gs = json.loads((ROOT / "data" / "qiyas_golden.json").read_text(encoding="utf-8"))


def test_frozen_terms_complete():
    terms = [f["term"] for f in ist["frozen"]]
    for needed in ["أركان القياس الأربعة", "تعريف العلّة", "شروط العلّة الثمانية",
                   "طرق معرفة العلّة", "العلّة غير السبب", "العلّة غير المناط",
                   "رفض القياس بالشبه", "الاسم الجامد لا يُعلَّل"]:
        assert needed in terms, f"missing: {needed}"


def test_arkaan_are_four():
    arkaan = next(f for f in ist["frozen"] if f["term"] == "أركان القياس الأربعة")
    for r in ["الفرع", "الأصل", "الحكم", "العلة"]:
        assert r in arkaan["quote"]


def test_eight_conditions_frozen():
    conds = next(f for f in ist["frozen"] if f["term"] == "شروط العلّة الثمانية")
    for c in ["باعثاً", "ظاهراً", "مؤثرة", "مطّردة", "متعدّية", "دليل شرعي"]:
        assert c in conds["quote"]


def test_gates_named_rejections():
    gates = " ".join(ist["gates"])
    for tag in ["شبه_فقط", "جامد", "قاصرة", "بلا_دليل"]:
        assert tag in gates


def test_golden_cases_present():
    cases = {c["id"]: c for c in gs["golden_cases"]}
    assert set(cases) == {"GS1", "GS2", "GS3", "GS4"}
    assert cases["GS1"]["expected"] == "إلحاق بعلّة" and cases["GS1"]["illah"].startswith("الإلهاء")
    assert cases["GS3"]["expected"].startswith("رفض") and cases["GS3"]["illah"] is None
    assert cases["GS4"]["expected"].startswith("رفض") and "شبه" in cases["GS4"]["expected"]


def test_four_exits():
    exits = gs["four_exits"]
    assert len(exits) == 4
    assert any("عموم" in e for e in exits)
    assert any("علّة" in e for e in exits)
    assert any("رفض" in e for e in exits)
    assert any("تعليق" in e for e in exits)
