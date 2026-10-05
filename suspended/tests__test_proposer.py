# -*- coding: utf-8 -*-
"""Tests for the proposer (المولِّد) — يقترح ولا يقبل أبدًا."""
import importlib.util, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("propose_rules", ROOT / "tools" / "propose_rules.py")
pr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr)
LEX = json.loads((ROOT / "data" / "proposer_lexicon.json").read_text(encoding="utf-8"))


def test_jurjani_58_condition_detected():
    r = pr.propose("أفلا ترى أن القامة إذا طالت طال النجاد", "§58")
    assert len(r["proposed"]) >= 1
    c = r["proposed"][0]
    assert "قامة" in c["antecedent"] and "نجاد" in c["consequent"]
    assert c["status"] == "مرشح"
    assert c["degree"] == "أخصّ" and c["manzila"] == "عادي_مقترح"
    assert c["evidence"]["source"] == "§58"


def test_causal_verb_detected():
    r = pr.propose("الجوع يؤدي إلى الضعف", "اختبار")
    assert any("جوع" in c["antecedent"] and "ضعف" in c["consequent"] for c in r["proposed"])


def test_kulla_maan_structure():
    r = pr.propose("كلما كثر القرى كثر رماد القدر", "§58")
    assert any("قرى" in c["antecedent"] and "قدر" in c["consequent"] for c in r["proposed"])


def test_similarity_rejected_named():
    r = pr.propose("زيد يشبه خالدًا في الطول", "اختبار")
    assert not r["proposed"]
    assert any(x["reason"] == "تافه_أو_شبه" for x in r["rejected"])


def test_no_candidate_is_ever_accepted():
    for text in ["القامة إذا طالت طال النجاد", "الحر يولّد العطش", "الكسر يستلزم الصوت"]:
        r = pr.propose(text, "فحص")
        for c in r["proposed"]:
            assert c["status"] == "مرشح"           # لا قبول أبدًا
            assert "قبول بدليل" in " ".join(c["needs"])


def test_lexicon_gates_frozen():
    gates = " ".join(g["gate"] + " " + g["rule"] for g in LEX["gates"])
    assert "لا قبول" in gates
    assert "لا شاهد معجم للقاعدة العادية" in gates
    assert "لا تُخمن مساويًا" in gates
    verbs = [c["verb"] for c in LEX["causal_verbs"]]
    assert "يستلزم" in verbs and "يردف" in verbs
