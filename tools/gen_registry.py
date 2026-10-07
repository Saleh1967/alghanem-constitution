"""يولِّد `SUSPENDED_REGISTRY.json` من شجرة `suspended/` ويفحص مطابقته — على طريقة الغانم وSLGE.

لكلّ وحدةٍ معلَّقة: مسارُها الحاليّ، مسارُها القديم، سببُ تعليقها، تاريخُه، وما يلزم لعودتها.
السببُ يُعيَّن بالمجلّد الأعلى (جدول `REASONS`)، والعودةُ بثلاثةٍ لا تتبدّل (`RE_ADMIT`).

    python tools/gen_registry.py          # يكتب السجلّ
    python tools/gen_registry.py --check  # يفشل إن خالف السجلُّ الشجرة
"""

from __future__ import annotations

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


def entries() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for path in sorted(SUSPENDED.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(SUSPENDED)
        top = rel.parts[0]
        out.append(
            {
                "path": str(path.relative_to(ROOT)),
                "previous_path": str(rel),
                "reason": REASONS.get(top, "suspended pending re-admission"),
                "suspended_at": SUSPENDED_AT,
                "re_admit_requires": RE_ADMIT,
            }
        )
    return out


def render() -> str:
    body = {
        "principle": "suspension without deletion: history stays in git; "
        "nothing returns except by re_admit_requires",
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
