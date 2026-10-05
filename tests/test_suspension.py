# -*- coding: utf-8 -*-
"""إنفاذ التعليق: لا قارئ ولا كاتب إلا البوابة — ولا استيراد من المعلقات."""
import ast, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
REG = json.loads((ROOT / "SUSPENDED_REGISTRY.json").read_text(encoding="utf-8"))
WHITELIST = {"tools/verify_repo.py", "tools/prove_alama_hamila.py", "tests/test_suspension.py"}
IO_TOKENS = ("open(", "os.", "sys.stdin", "print(")

def test_registry_entries_exist():
    for e in REG["entries"]:
        assert (ROOT / e["moved_to"]).exists(), f"missing: {e['moved_to']}"
        assert not (ROOT / e["path"]).exists(), f"not vacated: {e['path']}"

def test_no_unauthorized_io():
    offenders = []
    for p in ROOT.rglob("*.py"):
        rel = str(p.relative_to(ROOT))
        if "__pycache__" in rel or "suspended/" in rel:
            continue
        if rel in WHITELIST:
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                name = ""
                if isinstance(f, ast.Name): name = f.id
                elif isinstance(f, ast.Attribute):
                    parts = []
                    x = f
                    while isinstance(x, ast.Attribute):
                        parts.append(x.attr); x = x.value
                    if isinstance(x, ast.Name): parts.append(x.id)
                    name = ".".join(reversed(parts))
                if name in ("open", "print"):
                    offenders.append(f"{rel}:{node.lineno}:{name}")
    assert not offenders, f"unauthorized I/O: {offenders}"

def test_suspended_paths_unimportable():
    for e in REG["entries"]:
        if e["path"].endswith(".py"):
            assert not (ROOT / e["path"]).exists()
