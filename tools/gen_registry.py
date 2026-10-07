"""يولِّد `SUSPENDED_REGISTRY.json` من شجرة `suspended/` ويفحص مطابقته — على طريقة الغانم وSLGE.

لكلّ وحدةٍ معلَّقة: مسارُها الحاليّ، مسارُها القديم، سببُ تعليقها، تاريخُه، وما يلزم لعودتها.
السببُ يُعيَّن بالمجلّد الأعلى (جدول `REASONS`)، والعودةُ بثلاثةٍ لا تتبدّل (`RE_ADMIT`).

    python tools/gen_registry.py          # يكتب السجلّ
    python tools/gen_registry.py --check  # يفشل إن خالف السجلُّ الشجرة
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUSPENDED = ROOT / "suspended"
REGISTRY = ROOT / "SUSPENDED_REGISTRY.json"
SUSPENDED_AT = "2026-10-07"

RE_ADMIT = [
    "entry and exit only through the Alghanem gate: cells come from a Certificate "
    "(src/entry.py: atoms -> cells), never from text",
    "tests with expectations independent of the code, mutation-tested (20/20 method)",
    "ADR recorded in docs/adr/",
]

REASONS = {
    "src": "copied SLGE engines reading/normalizing text outside the gate (هي/إن تنهاران؛ "
    "الألفُ الخنجريّة تسقط — مقيس); superseded by Saleh1967/Alghanem gate/ and SLGE slge.entry",
    "legacy": "legacy bridge/segmenter/codebook checkers reading text outside the gate",
    "tools": "verify_repo ran the suspended engines; measure_nadhm read text directly",
    "tests": "tests of suspended modules, or expectations derived from the code under test",
}


# --- استخراجُ الدعوى ونوعِ المخالفة وطريقِ العودة لكلّ وحدةٍ معلَّقة ---
IO_READ = {"open", "read_text", "read_bytes", "load", "loads", "reader", "DictReader", "stdin",
           "argv", "input"}
IO_WRITE = {"write_text", "write_bytes", "dump", "dumps", "writer", "print", "stdout"}
IO_NORM = {"normalize", "decode", "encode"}

READMISSION = {
    "reads_text": "input only as gate certificates (gate.enter -> atoms -> cells); "
    "no bytes read here",
    "normalizes": "normalization is the gate's residue rules (A116.Residue); map each rule to "
    "a named residue edit or drop it",
    "writes_text": "outputs are atoms returned to gate.exit, or generated tables checked "
    "with --check",
    "measures": "re-measure on the corpus certificate deposit (18,179 forms) and a held-out "
    "reference",
    "pure": "restate the claim as a Lean theorem on cells + python mirror + conformance table",
    "lean": "re-prove against A116/SLGE definitions; audit axioms "
    "(propext/Classical.choice/Quot.sound)",
    "data": "deposit as certificates (bits) with sha256, never as text",
    "script": "replace by a guarded tool reading only deposits; or drop",
}


def profile(path: Path) -> tuple[str, list[str], list[str]]:
    """(الدعوى: أوّلُ سطرٍ من وثيقة الوحدة، أنواعُ المخالفة، طريقُ العودة)."""

    suf = path.suffix
    if suf == ".lean":
        return "", ["lean"], [READMISSION["lean"]]
    if suf in (".json", ".csv", ".txt", ".tsv", ".md", ".jsonl", ".norm.txt"):
        return "", ["data"], [READMISSION["data"]]
    if suf in (".sh", ".yml", ".yaml"):
        return "", ["script"], [READMISSION["script"]]
    if suf != ".py":
        return "", ["data"], [READMISSION["data"]]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return "", ["script"], [READMISSION["script"]]
    doc = (ast.get_docstring(tree) or "").strip().split("\n")[0][:200]
    kinds: set[str] = set()
    for n in ast.walk(tree):
        name = None
        if isinstance(n, ast.Call):
            f = n.func
            name = (f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute)
                    else None)
        elif isinstance(n, ast.Attribute):
            name = n.attr
        if name in IO_READ:
            kinds.add("reads_text")
        elif name in IO_WRITE:
            kinds.add("measures" if name in ("print", "stdout") else "writes_text")
        elif name in IO_NORM:
            kinds.add("normalizes")
    if not kinds:
        kinds.add("pure")
    order = ["reads_text", "normalizes", "writes_text", "measures", "pure"]
    ks = [k for k in order if k in kinds]
    return doc, ks, [READMISSION[k] for k in ks]


def entries() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for path in sorted(SUSPENDED.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path == SUSPENDED / "__init__.py":
            continue  # الحاجبُ نفسُه ليس وحدةً معلَّقة
        rel = path.relative_to(SUSPENDED)
        top = rel.parts[0]
        claim, kinds, readmission = profile(path)
        out.append(
            {
                "path": str(path.relative_to(ROOT)),
                "previous_path": str(rel),
                "reason": REASONS.get(top, "suspended pending re-admission"),
                "suspended_at": SUSPENDED_AT,
                "claim": claim,
                "violation": kinds,
                "readmission_path": readmission,
                "re_admit_requires": RE_ADMIT,
            }
        )
    return out


def render() -> str:
    units = entries()
    kinds: dict[str, int] = {}
    for u in units:
        for k in list(u["violation"]):  # type: ignore[call-overload]
            kinds[k] = kinds.get(k, 0) + 1
    body = {
        "principle": "suspension without deletion: history stays in git; "
        "nothing returns except by re_admit_requires",
        "violations_by_kind": dict(sorted(kinds.items())),
        "sole_entry_exit": "Saleh1967/Alghanem gate.api (enter, exit); here only src/entry.py "
        "(certificate atoms -> cells)",
        "count": len(entries()),
        "units": entries(),
    }
    return json.dumps(body, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        current = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
        if current != text:
            print("SUSPENDED_REGISTRY.json does not match suspended/ — run tools/gen_registry.py")
            return 1
        print(f"registry matches: {len(entries())} units")
        return 0
    REGISTRY.write_text(text, encoding="utf-8")
    print(f"wrote {REGISTRY.name}: {len(entries())} units")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
