"""حارسُ عدم الخرق — على طريقة `gate.guard` في الغانم: لا يقرأ بايتًا ولا يكتبه ولا يفكّ ترميزًا شيءٌ
في هذه الشجرة؛ النصُّ يدخل في الغانم وحدَه، وهنا تدخل ذرّاتُ الشهادة (`src/entry.py`).

يمشي على كلّ `.py` خارج `suspended/` و`tests/` ويرفض: `open`/`read_text`/`write_text`/`decode`/
`encode`/`normalize`/`json.load`/`csv.reader`، و`print`/`input`/`sys.argv`/`stdin`، واستيرادَ `suspended`.
القائمةُ البيضاء: `tools/gen_registry.py` و`tools/guard.py` نفسُه.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXEMPT_DIRS = ("suspended", "tests", ".git", "__pycache__", ".pytest_cache")
EXEMPT_FILES = ("tools/gen_registry.py", "tools/guard.py")
IO_ATTRS = frozenset(
    {
        "read_text", "read_bytes", "write_text", "write_bytes", "open", "decode", "encode",
        "normalize", "load", "loads", "reader", "DictReader", "argv", "stdin", "stdout",
    }
)
IO_NAMES = frozenset({"open", "print", "input", "exec", "eval"})
FORBIDDEN_IMPORT_PREFIXES = ("suspended", "slge_", "slge.slge", "algebra116", "alghanem_bridge")


@dataclass(frozen=True)
class Breach:
    path: str
    line: int
    what: str


def _files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.py"):
        rel = p.relative_to(ROOT)
        if any(part in EXEMPT_DIRS for part in rel.parts[:-1]) or str(rel) in EXEMPT_FILES:
            continue
        out.append(p)
    return sorted(out)


def breaches() -> list[Breach]:
    found: list[Breach] = []
    for p in _files():
        rel = str(p.relative_to(ROOT))
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for n in ast.walk(tree):
            if isinstance(n, ast.Import | ast.ImportFrom):
                names = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""]
                for m in names:
                    if m.startswith(FORBIDDEN_IMPORT_PREFIXES):
                        found.append(Breach(rel, n.lineno, f"import {m}"))
            elif isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name) and f.id in IO_NAMES:
                    found.append(Breach(rel, n.lineno, f.id))
                elif isinstance(f, ast.Attribute) and f.attr in IO_ATTRS:
                    found.append(Breach(rel, n.lineno, f.attr))
            elif isinstance(n, ast.Attribute) and n.attr in ("argv", "stdin"):
                found.append(Breach(rel, n.lineno, n.attr))
    return found


def main() -> int:
    b = breaches()
    for x in b:
        print(f"خرق: {x.path}:{x.line} {x.what}")
    print("الحارس:", "لا خرق" if not b else f"{len(b)} خرقًا")
    return 1 if b else 0


if __name__ == "__main__":
    raise SystemExit(main())
