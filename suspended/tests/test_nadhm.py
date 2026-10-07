# -*- coding: utf-8 -*-
"""Tests for the surface nadhm measurement + MASAQ schema contract."""
import importlib.util, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
stats = json.loads((ROOT / "data" / "nadhm_stats.json").read_text(encoding="utf-8"))
schema = json.loads((ROOT / "data" / "masaq_schema.json").read_text(encoding="utf-8"))

spec = importlib.util.spec_from_file_location("measure_nadhm", ROOT / "tools" / "measure_nadhm.py")
mn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mn)


def _fixture(tmp_path, text):
    f = tmp_path / "mini_quran.txt"
    f.write_text(text, encoding="utf-8")
    return mn.measure(str(f))


def test_fixture_strict_counts(tmp_path):
    # تمييل يجريد: إِنَّ → إن؛ التصاق الواو يمنع العدّ المستقل
    r = _fixture(tmp_path, "إِنَّ الله غفور\nوَإِذَا جاء نصر الله\nضرب زيد")
    strict = r["counts"]["strict_tokens"]
    assert strict["إن"] == 1
    assert strict["إذا"] == 0            # وإذا ملتصقة — لا تُعدّ إذا مستقلة
    assert r["counts"]["waaw_faa_prefixed"]["وإذا"] == 1


def test_real_corpus_provenance():
    c = stats["corpus"]
    assert c["verses"] == 6236
    assert c["sha256_16"] and len(c["sha256_16"]) == 16
    assert stats["kind"] == "surface_counts_only"
    assert "قياس فقط" in stats["caveat"]


def test_real_counts_sanity():
    strict = stats["counts"]["strict_tokens"]
    pref = stats["counts"]["waaw_faa_prefixed"]
    total_in = strict["إن"] + pref["وإن"] + pref["فإن"]
    total_idha = strict["إذا"] + pref["وإذا"] + pref["فإذا"]
    assert total_in > total_idha          # الواقع: إن أكثر ورودًا من إذا
    assert strict["إن"] == 966 and strict["إذا"] == 221
    assert strict["و"] == 0 and strict["ف"] == 0   # التصاق موثق في caveat


def test_masaq_schema_closed_inventory():
    roles = schema["required_columns"]["Syntactic_Role"]["values"]
    assert len(roles) == 12
    for r in ["فاعل", "خبر", "حال", "شرط"]:
        assert r in roles
    mods = schema["required_columns"]["Modality"]["values"]
    assert set(mods) == {"Habitual", "Future", "Probable", "Certain"}
    inv = " ".join(schema["invariants"])
    assert "لا يُشتق معنى" in inv
