# -*- coding: utf-8 -*-
"""Tests for the frozen lazum vocabulary + Ghazali's production forms (الغانم — الدال)."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LZ = json.loads((ROOT / "data" / "lazum_istilahat.json").read_text(encoding="utf-8"))


def test_one_relation_two_degrees():
    deg = LZ["lazum_vocabulary"]["degree"]["values"]
    assert deg == ["أخصّ", "مساوٍ"]
    assert "إما أخص" in LZ["lazum_vocabulary"]["degree"]["ghazali_quote"]


def test_three_manzilat():
    man = LZ["lazum_vocabulary"]["manzila"]["values"]
    assert man == ["وضعي", "عادي_وجودي", "شرعي"]
    assert "ليس ضروريا عندنا" in LZ["lazum_vocabulary"]["manzila"]["ghazali_quote"]


def test_akhass_produces_two_only():
    ak = LZ["production_forms"]["akhass"]
    assert len(ak["produces"]) == 2
    assert len(ak["non_produces"]) == 2
    assert "عين المقدم" in " ".join(ak["produces"])
    assert "نقيض التالي" in " ".join(ak["produces"])
    assert "عين التالي" in " ".join(ak["non_produces"])
    assert "نقيض المقدم" in " ".join(ak["non_produces"])
    assert "فرسا" in ak["counter_model"] and "حجرا" in ak["counter_model"]


def test_musawi_produces_four():
    ms = LZ["production_forms"]["musawi"]
    assert "أربع" in ms["produces"][0]
    assert "الشمس" in ms["example"] and "النهار" in ms["example"]
    assert "مساو لعلته" in ms["ghazali_quote"]


def test_raiser_needs_named_evidence():
    raisers = LZ["raiser_to_equality"]["kinds"]
    kinds = [r["kind"] for r in raisers]
    assert kinds == ["سياق الكلام", "وصف مفهم", "علّة واحدة"]
    for r in raisers:
        assert r.get("evidence") or r.get("nabhani_anchor") or r.get("ghazali_anchor")
    assert "بلا_رافع" in LZ["raiser_to_equality"]["without_raiser"]


def test_book_cases_frozen():
    bc = LZ["book_cases"]
    g = {c["case"]: c for c in bc["ghazali"]}
    assert g["الشمس والنهار"]["produced_forms"] == 4
    assert g["الإنسان والحيوان"]["produced_forms"] == 2
    n = {c["case"]: c for c in bc["nabhani"]}
    assert "رافع" in n["مفهوم المخالفة في الشرط والصفة والغاية والعدد"]["status"]
    assert "لا علّة" in n["مفهوم الاسم"]["status"]
    j = {c["case"]: c for c in bc["jurjani"]}
    assert "عين التالي" in j["طويل النجاد ← طويل القامة"]["form_used"]
    assert "رافع" in j["طويل النجاد ← طويل القامة"]["status"]
