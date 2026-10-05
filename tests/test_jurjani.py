# -*- coding: utf-8 -*-
"""Tests for the frozen Jurjani nadhm inventory (الغانم — الدال)."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
jn = json.loads((ROOT / "data" / "jurjani_nadhm.json").read_text(encoding="utf-8"))
F = jn["frozen"]


def test_definition_frozen():
    secs = [d["sec"] for d in F["definition"]]
    assert secs == ["§75", "§430"]
    assert "وضع كلامك" in F["definition"][0]["quote"] or "النحو" in F["definition"][0]["quote"]


def test_taalluq_relations_closed_inventory():
    rels = F["no_meaning_without_taalluq"]["relations"]
    assert len(rels) == 12
    for r in ["فاعل", "خبر", "حال", "تمييز", "شرط"]:
        assert r in rels
    assert "§48" == F["no_meaning_without_taalluq"]["sec"]


def test_alternatives_tables():
    a = F["alternatives"]
    assert len(a["khabar"]) == 8
    assert len(a["shart"]) == 5
    assert len(a["hal"]) == 4
    assert len(a["operations"]) == 4
    assert "تعريف وتنكير" in a["operations"] and "إضمار وإظهار" in a["operations"]


def test_particle_rules():
    rules = " ".join(p["rule"] for p in F["particle_rules"])
    assert "نفي الحال" in rules and "نفي الاستقبال" in rules
    assert "إن" in rules and "إذا" in rules


def test_letters_carry_no_meaning():
    q = F["letters_no_meaning"]["quote"]
    assert "§40" == F["letters_no_meaning"]["sec"]
    assert "ربض" in q and "ضرب" in q


def test_meaning_of_meaning_criterion():
    mc = F["meaning_of_meaning"]["transition_criterion"]
    assert "النجاد" in mc["quote"] and "رماد القدر" in mc["quote"]
    assert "الوجود" in mc["rule"]


def test_golden_kinaya():
    gk = {g["id"]: g for g in jn["golden_kinaya"]}
    assert gk["GK1"]["from"] == "طويل النجاد" and gk["GK1"]["to"] == "طويل القامة"
    assert gk["GK2"]["to"] == "كثير القرى"


def test_bridge_to_nabhani():
    b = {x["layer"]: x for x in F["bridge_nabhani_jurjani"]}
    assert "المنطوق" in b["المعنى الأول"]["nabhani"]
    assert "المفهوم" in b["المعنى الثاني"]["nabhani"]
    assert "الوجود" in b["شرط الانتقال"]["jurjani"]
