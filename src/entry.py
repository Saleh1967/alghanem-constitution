"""المدخلُ الوحيد لهذا المستودع: ذرّاتُ شهادةِ بوّابة الغانم ← خانات. لا نصَّ هنا.

`gate.enter(bytes) → Certificate` في `Saleh1967/Alghanem` (فرع `claude/official-gate`)؛ هنا تصل
`cert.atoms` (كلُّ ذرّةٍ حرفٌ من التسعة والعشرين وعلامةٌ من الأربع) فتُحوَّل خاناتٍ `(حامل، حالة)` كما في
`slge.entry.from_atoms` بعينها، وتعود ذرّاتٍ بعينها بـ`to_atoms` إلى `gate.exit`. ما ليس ذرّةً من الـ116 يُرفض
باسمه (`NOT_A_116_ATOM`) ولا يُصلَح ولا يُخمَّن.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Final

__all__ = ["ALPHABET", "MARKS", "STATES", "Cell", "from_atoms", "licensed", "to_atoms"]

Cell = tuple[str, str]
ALPHABET: Final[tuple[str, ...]] = tuple("ءابتثجحخدذرزسشصضطظعغفقكلمنهوي")
STATES: Final[tuple[str, ...]] = ("فتح", "كسر", "ضم", "سكون")
MARKS: Final[dict[str, str]] = {"َ": "فتح", "ِ": "كسر", "ُ": "ضم", "ْ": "سكون"}
_MARK_OF: Final[dict[str, str]] = {v: k for k, v in MARKS.items()}
_CARRIERS: Final[frozenset[str]] = frozenset(ALPHABET)


def from_atoms(atoms: Iterable[str]) -> tuple[Cell, ...]:
    """ذرّاتُ شهادةٍ ← خانات؛ `ValueError("NOT_A_116_ATOM:…")` لما ليس من الـ116."""

    out: list[Cell] = []
    for a in atoms:
        if len(a) != 2 or a[0] not in _CARRIERS or a[1] not in MARKS:
            raise ValueError(f"NOT_A_116_ATOM:{a!r}")
        out.append((a[0], MARKS[a[1]]))
    return tuple(out)


def to_atoms(cells: Sequence[Cell]) -> tuple[str, ...]:
    """خانات ← ذرّاتُ الشهادة بعينها (`from_atoms` معكوسةً)."""

    return tuple(c + _MARK_OF[s] for c, s in cells)


def licensed(cells: Sequence[Cell]) -> bool:
    """الترخيصُ الثنائيّ (`A116.Admissible` عبر جسر SLGE): لا يبدأ بساكن ولا يتجاور ساكنان."""

    if not cells:
        return True
    if cells[0][1] == "سكون":
        return False
    return all(not (a[1] == "سكون" and b[1] == "سكون") for a, b in zip(cells, cells[1:], strict=False))
