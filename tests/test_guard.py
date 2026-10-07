"""الحارسُ والسجلُّ والمدخل: لا خرقَ في الشجرة، الخرقُ المزروعُ يُلتقط، المعلَّقُ غيرُ قابلٍ للاستيراد، السجلُّ
مولَّدٌ لا محرَّر، والمدخلُ ذرّاتُ الشهادة بعينها ذهابًا وإيابًا."""

from __future__ import annotations

import importlib
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

from guard import breaches  # noqa: E402
import entry  # noqa: E402


def test_tree_has_no_breach() -> None:
    assert breaches() == []


def test_guard_catches_a_planted_breach() -> None:
    planted = ROOT / "zz_planted.py"
    planted.write_text("open('x').read()\nimport suspended.src\n", encoding="utf-8")
    try:
        b = breaches()
    finally:
        planted.unlink()
    assert {x.what for x in b} >= {"open", "import suspended.src"}


def test_suspended_is_not_importable() -> None:
    for name in ("slge", "slge_laws", "algebra116", "alghanem_bridge", "suspended.src.slge.slge"):
        try:
            mod = importlib.import_module(name)
        except ImportError:
            continue
        where = pathlib.Path(getattr(mod, "__file__", "") or "").resolve()
        assert ROOT not in where.parents, f"{name} ما زال قابلًا للاستيراد من هذه الشجرة: {where}"


def test_registry_matches_suspended_tree() -> None:
    spec = importlib.util.spec_from_file_location("gen_registry", ROOT / "tools" / "gen_registry.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.render() == (ROOT / "SUSPENDED_REGISTRY.json").read_text(encoding="utf-8")
    units = json.loads((ROOT / "SUSPENDED_REGISTRY.json").read_text(encoding="utf-8"))["units"]
    assert len(units) == 20 and all(u["reason"] and u["re_admit_requires"] for u in units)
    assert all(not (ROOT / u["previous_path"]).exists() for u in units)  # نقلٌ لا نسخ


def test_entry_is_the_certificate_atoms_exactly() -> None:
    # ذرّاتُ شهادةٍ حقيقيّة من gate.enter(b"بِسْمِ") كما طُبعت خامًا: ('بِ', 'سْ', 'مِ')
    atoms = ("بِ", "سْ", "مِ")
    cells = entry.from_atoms(atoms)
    assert cells == (("ب", "كسر"), ("س", "سكون"), ("م", "كسر"))
    assert entry.to_atoms(cells) == atoms and entry.licensed(cells)
    assert not entry.licensed((("ك", "سكون"),)) and not entry.licensed((("ك", "فتح"), ("ت", "سكون"), ("ب", "سكون")))
    # الطفرة: ذرّةٌ ليست من الـ116 تُرفض باسمها، لا تُصلَح
    for bad in (("ب",), ("ٱَ",), ("بٌ",), ("x",)):
        try:
            entry.from_atoms(bad)
        except ValueError as e:
            assert str(e).startswith("NOT_A_116_ATOM")
        else:
            raise AssertionError(bad)
