"""الجسرُ المرجعيُّ لبروتوكول A116-CANONICAL-TXT-1.0.

الدالّةُ `bridge` تأخذ النصَّ الأصليَّ أو بايتاتِه، وترميزَه المصرَّحَ به، وملفَّ
القراءة النصّيّة، وحالَ الابتداء والوصل والوقف، والشواهدَ اللازمةَ لحسم
المعلومات المحذوفة؛ وتعيد سجلًّا محفوظَ المصدر وإحدى حالاتٍ متنافية:
`READY` و`DEFER` و`REJECT` و`INVALID_ENCODING_OR_TYPE` و`INVALID_CONFIGURATION`.

وفي كلِّ حالٍ غيرِ `READY` يكون `canonical_atoms` و`canonical_text` عدمًا،
و`count_eligible` كذبًا. و`READY` شهادةُ صحّةٍ بالنسبة للقواعد المنفَّذة
والتعليقات المصرَّح بها؛ ليست شهادةَ صحّةٍ صرفيّةً أو معجميّةً للكلمة، ولا
إثباتًا لشمول جميع العربيّة.
"""

from __future__ import annotations

import base64
import hashlib
import unicodedata
from enum import Enum
from typing import Any

PROTOCOL_VERSION = "A116-CANONICAL-TXT-1.0"
"""إصدارُ العقد؛ وتوسيعُ الملفّ يحتاج قاعدةً مصرَّحًا بها وشاهدًا واختبارات."""

ALPHABET: tuple[str, ...] = (
    "ء",
    "ب",
    "ت",
    "ث",
    "ج",
    "ح",
    "خ",
    "د",
    "ذ",
    "ر",
    "ز",
    "س",
    "ش",
    "ص",
    "ض",
    "ط",
    "ظ",
    "ع",
    "غ",
    "ف",
    "ق",
    "ك",
    "ل",
    "م",
    "ن",
    "ه",
    "و",
    "ي",
    "ا",
)
"""الحواملُ التسعةُ والعشرون؛ تشمل الهمزةَ والألف."""

FATHA = "\u064e"
DAMMA = "\u064f"
KASRA = "\u0650"
SUKUN = "\u0652"
SHADDA = "\u0651"
TANWIN_FATH = "\u064b"
TANWIN_DAMM = "\u064c"
TANWIN_KASR = "\u064d"
DAGGER_ALIF = "\u0670"
MADDA_ABOVE = "\u0653"
HAMZA_ABOVE = "\u0654"
HAMZA_BELOW = "\u0655"
TATWEEL = "\u0640"
ALIF_WASLA = "\u0671"

HARAKAT: tuple[str, ...] = (FATHA, DAMMA, KASRA, SUKUN)
"""الحركاتُ الأربع؛ والسكونُ فيها حالةٌ معياريّةٌ لا اشتراطُ ظهورِ علامة."""

A116: tuple[str, ...] = tuple(
    letter + haraka for letter in ALPHABET for haraka in HARAKAT
)
"""الخاناتُ الستَّ عشرةَ بعد المئة؛ ووجودُ الخانة لا يمنحها ترخيصًا في كلِّ موضع."""

VOWELS = frozenset({FATHA, DAMMA, KASRA})
TANWINS = frozenset({TANWIN_FATH, TANWIN_DAMM, TANWIN_KASR})
SUPPORTED_MARKS = frozenset(
    {
        FATHA,
        DAMMA,
        KASRA,
        SUKUN,
        SHADDA,
        TANWIN_FATH,
        TANWIN_DAMM,
        TANWIN_KASR,
        DAGGER_ALIF,
        MADDA_ABOVE,
        HAMZA_ABOVE,
        HAMZA_BELOW,
    }
)

PROFILES: tuple[str, ...] = ("modern-vocalized", "uthmani-explicit")
"""ملفّا القراءة المنفَّذان؛ والثاني يعلن قصدَ معالجةِ نصٍّ عثمانيٍّ لا استيعابَه."""

ENTRY_STATES: tuple[str, ...] = ("start", "joined")
EXIT_STATES: tuple[str, ...] = ("continue", "pause")

SUPPORTED_ROLES: tuple[str, ...] = ("WASL", "SILENT_SUPPORT")
"""الأدوارُ المدعومة بالتعليق؛ وما سواها لا يُدخَل بالتخمين."""

DECODERS: tuple[str, ...] = (
    "utf-8-sig",
    "utf-8",
    "utf-16",
    "utf-16-le",
    "utf-16-be",
    "utf-32",
    "utf-32-le",
    "utf-32-be",
)


class BridgeStatus(str, Enum):
    """حالاتُ الجسر المتنافية؛ والعدُّ متاحٌ في الجاهزة وحدها."""

    READY = "READY"
    DEFER = "DEFER"
    REJECT = "REJECT"
    INVALID_ENCODING_OR_TYPE = "INVALID_ENCODING_OR_TYPE"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"


class CountingRefused(RuntimeError):
    """تُرفَع عند طلب العدّ من شهادةٍ غيرِ جاهزة؛ فالعدُّ محظورٌ لا مُقدَّر."""


# ---------------------------------------------------------------------------
# أوّلًا: فكُّ الترميز الصارم وحفظُ المصدر
# ---------------------------------------------------------------------------


def _decode(source: Any, encoding: str | None) -> tuple[str, bytes, str]:
    if isinstance(source, str):
        return source, source.encode("utf-8"), "utf-8"
    if not isinstance(source, bytes | bytearray):
        raise TypeError("الدخلُ نصٌّ أو بايتات؛ وما سواهما لا يُقرأ.")
    raw = bytes(source)
    candidates = (encoding,) if encoding is not None else DECODERS
    for candidate in candidates:
        try:
            return raw.decode(candidate, errors="strict"), raw, candidate
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError("تعذّر فكُّ البايتات بترميزٍ مصرَّحٍ به؛ ولا تجاوزَ بالإهمال.")


# ---------------------------------------------------------------------------
# ثانيًا: الجسرُ الطباعيّ، ثمّ جسرُ الحرف والعلامات
# ---------------------------------------------------------------------------


def _typographic_bridge(text: str) -> tuple[str, list[dict[str, Any]]]:
    """تُفكَّك أشكالُ العرض العربيّةُ محلّيًّا، ويُحذَف التطويلُ مع تسجيل موضعه."""

    out: list[str] = []
    notes: list[dict[str, Any]] = []
    for offset, character in enumerate(text):
        if character == TATWEEL:
            notes.append(
                {"offset": offset, "character": TATWEEL, "note": "TATWEEL_DROPPED"}
            )
            continue
        if "\ufb50" <= character <= "\ufeff":
            folded = unicodedata.normalize("NFKC", character)
            if folded != character:
                notes.append(
                    {
                        "offset": offset,
                        "character": character,
                        "note": "PRESENTATION_FORM_FOLDED",
                    }
                )
            out.append(folded)
            continue
        out.append(character)
    return "".join(out), notes


def _is_arabic_letter(character: str) -> bool:
    return character in {
        "ء",
        "آ",
        "أ",
        "ؤ",
        "إ",
        "ئ",
        "ا",
        "ب",
        "ة",
        "ت",
        "ث",
        "ج",
        "ح",
        "خ",
        "د",
        "ذ",
        "ر",
        "ز",
        "س",
        "ش",
        "ص",
        "ض",
        "ط",
        "ظ",
        "ع",
        "غ",
        "ف",
        "ق",
        "ك",
        "ل",
        "م",
        "ن",
        "ه",
        "و",
        "ى",
        "ي",
        ALIF_WASLA,
    }


def _is_mark(character: str) -> bool:
    return unicodedata.category(character) == "Mn"


def _segment(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """قسمةُ النصّ إلى كلماتٍ وحدودٍ غيرِ ذرّيّة، محفوظةَ المواضع."""

    words: list[dict[str, Any]] = []
    boundaries: list[dict[str, Any]] = []
    index = 0
    length = len(text)
    while index < length:
        character = text[index]
        if _is_arabic_letter(character) or _is_mark(character):
            start = index
            while index < length and (
                _is_arabic_letter(text[index]) or _is_mark(text[index])
            ):
                index += 1
            words.append(
                {
                    "index": len(words),
                    "source": text[start:index],
                    "source_span": [start, index],
                }
            )
            continue
        start = index
        while index < length and not (
            _is_arabic_letter(text[index]) or _is_mark(text[index])
        ):
            index += 1
        boundaries.append(
            {
                "source": text[start:index],
                "source_span": [start, index],
                "atomic": False,
            }
        )
    return words, boundaries


def _clusters_of(word: str) -> list[dict[str, Any]]:
    """عناقيدُ الكلمة بعد NFD؛ الرسمُ والكرسيُّ والعلاماتُ محفوظةٌ كما وردت."""

    decomposed = unicodedata.normalize("NFD", word)
    clusters: list[dict[str, Any]] = []
    for character in decomposed:
        if _is_mark(character) and clusters:
            clusters[-1]["marks"].append(character)
            continue
        clusters.append(
            {
                "index": len(clusters),
                "base": character,
                "marks": [],
                "role": None,
                "atoms": [],
            }
        )
    return clusters


# ---------------------------------------------------------------------------
# ثالثًا: التعليقاتُ وواجهةُ الحدود
# ---------------------------------------------------------------------------


def _normalise_annotations(annotations: Any) -> dict[int, dict[int, dict[str, Any]]]:
    if annotations is None:
        return {}
    if not isinstance(annotations, dict):
        raise ValueError("التعليقاتُ كائنٌ من مفاتيحَ عدديّةٍ للكلمات والعناقيد.")
    out: dict[int, dict[int, dict[str, Any]]] = {}
    for word_key, cluster_map in annotations.items():
        word_index = _as_index(word_key, "مفتاحُ كلمةٍ")
        if not isinstance(cluster_map, dict):
            raise ValueError("تعليقُ الكلمةِ كائنٌ من مفاتيحِ عناقيد.")
        inner: dict[int, dict[str, Any]] = {}
        for cluster_key, payload in cluster_map.items():
            cluster_index = _as_index(cluster_key, "مفتاحُ عنقود")
            if not isinstance(payload, dict):
                raise ValueError("تعليقُ العنقودِ كائنٌ من حقول.")
            inner[cluster_index] = _validated_annotation(payload)
        out[word_index] = inner
    return out


def _as_index(key: Any, what: str) -> int:
    if isinstance(key, bool):
        raise ValueError(f"{what} ليس عددًا صحيحًا يبدأ بالصفر.")
    if isinstance(key, int):
        value = key
    elif isinstance(key, str) and key.isdigit():
        value = int(key)
    else:
        raise ValueError(f"{what} ليس عددًا صحيحًا يبدأ بالصفر.")
    if value < 0:
        raise ValueError(f"{what} سالبٌ لا يُقبَل.")
    return value


def _validated_annotation(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {"role", "start_vowel", "state", "evidence"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError(f"حقولٌ غيرُ مدعومةٍ في التعليق: {sorted(unknown)}")
    supplied = {key for key in ("role", "start_vowel", "state") if key in payload}
    if supplied and not str(payload.get("evidence", "")).strip():
        raise ValueError("الحقلُ evidence إلزاميٌّ عند توريد قيمة.")
    role = payload.get("role")
    if role is not None and role not in SUPPORTED_ROLES:
        raise ValueError(f"دورٌ غيرُ مدعومٍ في التعليق: {role!r}")
    for key in ("start_vowel", "state"):
        value = payload.get(key)
        if value is not None and value not in HARAKAT:
            raise ValueError(f"قيمةُ {key} ليست من الحركات الأربع.")
    return dict(payload)


def _normalise_contexts(contexts: Any, word_count: int) -> list[dict[str, str]]:
    if contexts is None:
        resolved: list[dict[str, str]] = [
            {"entry": "start", "exit": "continue"} for _ in range(word_count)
        ]
        return resolved
    if not isinstance(contexts, dict):
        raise ValueError("واجهةُ الحدود كائنٌ من مفاتيحِ الكلمات.")
    resolved = [{"entry": "start", "exit": "continue"} for _ in range(word_count)]
    seen: set[int] = set()
    for key, payload in contexts.items():
        index = _as_index(key, "مفتاحُ كلمةٍ في واجهة الحدود")
        if index >= word_count:
            raise ValueError("واجهةُ الحدود تشير إلى كلمةٍ خارج النصّ.")
        if not isinstance(payload, dict):
            raise ValueError("حالُ الكلمةِ كائنٌ فيه entry وexit.")
        entry = payload.get("entry", "start")
        exit_ = payload.get("exit", "continue")
        if entry not in ENTRY_STATES or exit_ not in EXIT_STATES:
            raise ValueError("حالُ الدخول أو الخروج خارج المحورين المعلنَين.")
        resolved[index] = {"entry": entry, "exit": exit_}
        seen.add(index)
    return resolved


def _check_boundary_interface(
    states: list[dict[str, str]], words: list[dict[str, Any]], text: str
) -> None:
    if states and states[0]["entry"] == "joined":
        raise ValueError("الوصلُ في أوّل النصّ يمنع العدَّ لغياب السياق الأيسر.")
    for index in range(1, len(states)):
        previous = states[index - 1]
        current = states[index]
        gap = text[words[index - 1]["source_span"][1] : words[index]["source_span"][0]]
        if current["entry"] == "joined":
            if previous["exit"] != "continue":
                raise ValueError("الوصلُ يتطلّب استمرارَ السابق.")
            if not gap or not gap.isspace():
                raise ValueError("الوصلُ يتطلّب فراغًا بين الكلمتين.")
        elif previous["exit"] != "pause":
            raise ValueError("الابتداءُ التالي يتطلّب وقفًا سابقًا.")


# ---------------------------------------------------------------------------
# رابعًا: الجسرُ الإملائيُّ والصوتيُّ النصّيّ
# ---------------------------------------------------------------------------


class _Refusal(Exception):
    def __init__(self, status: BridgeStatus, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.status = status
        self.reason = reason
        self.detail = detail


def _defer(reason: str, detail: str = "") -> _Refusal:
    return _Refusal(BridgeStatus.DEFER, reason, detail)


def _reject(reason: str, detail: str = "") -> _Refusal:
    return _Refusal(BridgeStatus.REJECT, reason, detail)


def _marks_reading(
    cluster: dict[str, Any], annotation: dict[str, Any]
) -> dict[str, Any]:
    marks = list(cluster["marks"])
    for mark in marks:
        if mark not in SUPPORTED_MARKS:
            raise _defer("UNSUPPORTED_MARK", repr(mark))
    vowels = [mark for mark in marks if mark in VOWELS]
    tanwins = [mark for mark in marks if mark in TANWINS]
    has_sukun = SUKUN in marks
    has_shadda = SHADDA in marks
    if len(vowels) > 1 or len(tanwins) > 1:
        raise _reject("CONFLICTING_MARKS", "".join(marks))
    if vowels and has_sukun:
        raise _reject("VOWEL_WITH_SUKUN", "".join(marks))
    if has_shadda and has_sukun:
        raise _reject("SHADDA_WITH_SUKUN", "".join(marks))
    if tanwins and (has_sukun or vowels):
        raise _reject("TANWIN_WITH_ANOTHER_HARAKA", "".join(marks))
    state = annotation.get("state")
    if state is not None:
        if vowels or has_sukun or tanwins:
            raise _reject("ANNOTATION_CONTRADICTS_AN_EXPLICIT_MARK", state)
        if state == SUKUN:
            has_sukun = True
        else:
            vowels = [state]
    return {
        "vowel": vowels[0] if vowels else None,
        "tanwin": tanwins[0] if tanwins else None,
        "sukun": has_sukun,
        "shadda": has_shadda,
        "dagger": DAGGER_ALIF in marks,
        "madda": MADDA_ABOVE in marks,
        "hamza_seat": HAMZA_ABOVE in marks or HAMZA_BELOW in marks,
    }


def _carrier_atoms(
    carrier: str, reading: dict[str, Any], *, is_final: bool, exit_: str
) -> list[str]:
    """ذرّاتُ حاملٍ صامتٍ بحالته؛ والشدّةُ نصفان، والوقفُ بالسكون."""

    atoms: list[str] = []
    if reading["shadda"]:
        atoms.append(carrier + SUKUN)
    pausing = is_final and exit_ == "pause"
    tanwin = reading["tanwin"]
    if tanwin is not None and not is_final:
        raise _defer("TANWIN_ATTACHMENT_IS_AMBIGUOUS", carrier)
    if tanwin is not None:
        if pausing:
            if tanwin == TANWIN_FATH:
                atoms.extend([carrier + FATHA, "ا" + SUKUN])
            else:
                atoms.append(carrier + SUKUN)
            return atoms
        vowel = {
            TANWIN_FATH: FATHA,
            TANWIN_DAMM: DAMMA,
            TANWIN_KASR: KASRA,
        }[tanwin]
        atoms.extend([carrier + vowel, "ن" + SUKUN])
        return atoms
    if pausing:
        if reading["vowel"] is None and not reading["sukun"]:
            raise _defer("FINAL_HARAKA_IS_ABSENT", carrier)
        atoms.append(carrier + SUKUN)
        return atoms
    if reading["sukun"]:
        atoms.append(carrier + SUKUN)
        return atoms
    if reading["vowel"] is None:
        raise _defer("HARAKA_IS_ABSENT_AND_IS_NEVER_GUESSED", carrier)
    atoms.append(carrier + reading["vowel"])
    if reading["dagger"] and reading["vowel"] == FATHA:
        atoms.append("ا" + SUKUN)
    return atoms


def _final_index(clusters: list[dict[str, Any]]) -> int:
    """آخرُ عنقودٍ منطوقٍ؛ وألفُ تنوين الفتح حرفُ دعمٍ لا يُزحزح الطرف."""

    last = len(clusters) - 1
    while last > 0:
        cluster = clusters[last]
        if cluster["base"] in {"ا", "ى"} and not cluster["marks"]:
            previous = clusters[last - 1]
            if TANWIN_FATH in previous["marks"]:
                last -= 1
                continue
        break
    return last


def _word_atoms(
    clusters: list[dict[str, Any]], state: dict[str, str], annotations: dict[int, Any]
) -> list[str]:
    atoms: list[str] = []
    last = _final_index(clusters)
    for position, cluster in enumerate(clusters):
        annotation = annotations.get(position, {})
        reading = _marks_reading(cluster, annotation)
        base = cluster["base"]
        is_final = position == last
        produced = _cluster_atoms(
            base,
            reading,
            annotation,
            clusters,
            position,
            is_final=is_final,
            state=state,
        )
        for atom in produced:
            if atom not in A116:
                raise _reject("ATOM_OUTSIDE_A116", atom)
        cluster["atoms"] = produced
        atoms.extend(produced)
    return atoms


def _previous_reading(clusters: list[dict[str, Any]], position: int) -> dict[str, Any]:
    if position == 0:
        return {}
    return clusters[position - 1].get("reading") or {}


def _cluster_atoms(
    base: str,
    reading: dict[str, Any],
    annotation: dict[str, Any],
    clusters: list[dict[str, Any]],
    position: int,
    *,
    is_final: bool,
    state: dict[str, str],
) -> list[str]:
    clusters[position]["reading"] = reading
    previous = _previous_reading(clusters, position)
    exit_ = state["exit"]
    role = annotation.get("role")

    if base == "ا" and reading["madda"]:
        clusters[position]["role"] = "MADDA"
        return ["ء" + FATHA, "ا" + SUKUN]

    if base == "ء" or reading["hamza_seat"]:
        clusters[position]["role"] = "HAMZA"
        return _carrier_atoms("ء", reading, is_final=is_final, exit_=exit_)

    if base == ALIF_WASLA or (base == "ا" and role == "WASL"):
        if position != 0:
            raise _defer("WASL_IS_DECLARED_OUTSIDE_A_WORD_START", base)
        clusters[position]["role"] = "WASL"
        if state["entry"] == "joined":
            return []
        start_vowel = annotation.get("start_vowel") or reading["vowel"]
        if start_vowel is None or start_vowel == SUKUN:
            raise _defer("START_VOWEL_OF_WASL_IS_UNKNOWN", base)
        return ["ء" + start_vowel]

    if base in {"ا", "ى"}:
        if reading["tanwin"] is not None:
            raise _defer("TANWIN_ATTACHMENT_IS_AMBIGUOUS", base)
        if role == "SILENT_SUPPORT":
            clusters[position]["role"] = "SILENT_SUPPORT"
            return []
        if previous.get("tanwin") == TANWIN_FATH:
            clusters[position]["role"] = "TANWIN_SUPPORT"
            return []
        if (
            previous.get("vowel") == FATHA
            and reading["vowel"] is None
            and not reading["sukun"]
        ):
            clusters[position]["role"] = "MADD"
            return ["ا" + SUKUN]
        if reading["vowel"] is not None or reading["sukun"]:
            clusters[position]["role"] = "ALIF_WITH_ITS_OWN_MARK"
            return _carrier_atoms("ا", reading, is_final=is_final, exit_=exit_)
        raise _defer("THE_ROLE_OF_THIS_ALIF_IS_UNDECIDED", base)

    if base == "ة":
        if not is_final:
            raise _defer("TA_MARBUTA_IS_NOT_FINAL", base)
        clusters[position]["role"] = "TA_MARBUTA"
        if exit_ == "pause":
            return ["ه" + SUKUN]
        return _carrier_atoms("ت", reading, is_final=is_final, exit_=exit_)

    if base in {"و", "ي"}:
        wanted = DAMMA if base == "و" else KASRA
        if reading["sukun"] and previous.get("vowel") == wanted:
            clusters[position]["role"] = "MADD"
            return [base + SUKUN]
        clusters[position]["role"] = "CONSONANT"
        return _carrier_atoms(base, reading, is_final=is_final, exit_=exit_)

    if base in ALPHABET:
        clusters[position]["role"] = "CONSONANT"
        return _carrier_atoms(base, reading, is_final=is_final, exit_=exit_)

    raise _defer("UNSUPPORTED_LETTER", base)


# ---------------------------------------------------------------------------
# خامسًا: الجسرُ كلُّه، ثمّ بوّابةُ العدّ
# ---------------------------------------------------------------------------


def _blank_record(
    status: BridgeStatus, reason: str, detail: str, options: dict[str, Any]
) -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "unicode_version": unicodedata.unidata_version,
        "status": status.value,
        "count_eligible": False,
        "canonical_text": None,
        "canonical_atoms": None,
        "words": [],
        "boundaries": [],
        "typographic_notes": [],
        "deferrals": [{"reason": reason, "detail": detail}]
        if status is BridgeStatus.DEFER
        else [],
        "rejections": [{"reason": reason, "detail": detail}]
        if status is BridgeStatus.REJECT
        else [],
        "error": {"reason": reason, "detail": detail},
        "source_text": None,
        "source_bytes_base64": None,
        "source_sha256": None,
        "encoding": None,
        "options": options,
    }


def bridge(
    source: str | bytes,
    *,
    encoding: str | None = None,
    profile: str = "modern-vocalized",
    contexts: Any = None,
    annotations: Any = None,
) -> dict[str, Any]:
    """الجسرُ المرجعيّ: سجلٌّ محفوظُ المصدر مع إحدى الحالات المتنافية."""

    options = {
        "encoding": encoding,
        "profile": profile,
        "contexts": contexts,
        "annotations": annotations,
    }
    try:
        text, raw, used_encoding = _decode(source, encoding)
    except (TypeError, ValueError) as error:
        return _blank_record(
            BridgeStatus.INVALID_ENCODING_OR_TYPE, "DECODE_FAILED", str(error), options
        )

    record = _blank_record(BridgeStatus.READY, "", "", options)
    record["source_text"] = text
    record["source_bytes_base64"] = base64.b64encode(raw).decode("ascii")
    record["source_sha256"] = hashlib.sha256(raw).hexdigest()
    record["encoding"] = used_encoding
    record["error"] = None

    if profile not in PROFILES:
        return _blank_record(
            BridgeStatus.INVALID_CONFIGURATION, "UNKNOWN_PROFILE", profile, options
        )

    projected, notes = _typographic_bridge(text)
    record["typographic_notes"] = notes
    words, boundaries = _segment(projected)
    record["boundaries"] = boundaries

    try:
        resolved_annotations = _normalise_annotations(annotations)
        states = _normalise_contexts(contexts, len(words))
        if contexts is not None or len(words) <= 1:
            _check_boundary_interface(states, words, projected)
    except ValueError as error:
        blank = _blank_record(
            BridgeStatus.INVALID_CONFIGURATION,
            "INVALID_BOUNDARY_OR_ANNOTATION",
            str(error),
            options,
        )
        blank.update(
            {
                "source_text": text,
                "source_bytes_base64": record["source_bytes_base64"],
                "source_sha256": record["source_sha256"],
                "encoding": used_encoding,
            }
        )
        return blank

    if not words:
        record["status"] = BridgeStatus.DEFER.value
        record["deferrals"] = [{"reason": "NO_ARABIC_WORD_IN_SOURCE", "detail": ""}]
        return record

    if len(words) > 1 and contexts is None:
        record["status"] = BridgeStatus.DEFER.value
        record["deferrals"] = [
            {"reason": "A_MULTI_WORD_TEXT_NEEDS_A_BOUNDARY_INTERFACE", "detail": ""}
        ]
        return record

    deferrals: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    atoms: list[str] = []
    word_records: list[dict[str, Any]] = []

    for word in words:
        clusters = _clusters_of(word["source"])
        state = states[word["index"]]
        word_annotations = resolved_annotations.get(word["index"], {})
        entry: dict[str, Any] = {
            "index": word["index"],
            "source": word["source"],
            "source_span": word["source_span"],
            "entry": state["entry"],
            "exit": state["exit"],
            "clusters": clusters,
            "atoms": None,
        }
        try:
            produced = _word_atoms(clusters, state, word_annotations)
        except _Refusal as refusal:
            payload = {
                "word": word["index"],
                "reason": refusal.reason,
                "detail": refusal.detail,
            }
            if refusal.status is BridgeStatus.REJECT:
                rejections.append(payload)
            else:
                deferrals.append(payload)
        else:
            entry["atoms"] = produced
            atoms.extend(produced)
        word_records.append(entry)

    record["words"] = word_records
    record["deferrals"] = deferrals
    record["rejections"] = rejections
    if rejections:
        record["status"] = BridgeStatus.REJECT.value
        return record
    if deferrals:
        record["status"] = BridgeStatus.DEFER.value
        return record
    record["status"] = BridgeStatus.READY.value
    record["count_eligible"] = True
    record["canonical_atoms"] = atoms
    record["canonical_text"] = " ".join(
        "".join(word["atoms"] or []) for word in word_records
    )
    return record


def verify(record: dict[str, Any]) -> dict[str, Any]:
    """إعادةُ تنفيذ الشهادة من مصدرها وخياراتها؛ تشغيلٌ مرتبطٌ بالمصدر لا تدقيقٌ لغويّ."""

    if record.get("source_bytes_base64") is None:
        raise CountingRefused("شهادةٌ بلا مصدرٍ محفوظٍ لا يُعاد تنفيذها.")
    raw = base64.b64decode(record["source_bytes_base64"])
    options = record.get("options") or {}
    replay = bridge(
        raw,
        encoding=record.get("encoding"),
        profile=options.get("profile", "modern-vocalized"),
        contexts=options.get("contexts"),
        annotations=options.get("annotations"),
    )
    agrees = (
        replay["status"] == record["status"]
        and replay["source_sha256"] == record["source_sha256"]
        and replay["canonical_atoms"] == record["canonical_atoms"]
    )
    return {"reproduced": agrees, "replay": replay}


def count_atoms(record: dict[str, Any]) -> dict[str, int]:
    """بوّابةُ العدّ الوحيدة: إعادةُ التحقّق من المصدر، ثمّ عدُّ الذرّات فقط.

    ويحوي التعدادُ جميعَ مفاتيح الـ116 بما فيها الأصفار، ولا يخلق وجودُ المفتاح
    ترخيصًا لخانةٍ غائبة. والذرّاتُ الجزئيّةُ في السجلّ تشخيصيّةٌ لا تُجمَع.
    """

    if record.get("status") != BridgeStatus.READY.value:
        raise CountingRefused(f"العدُّ محظورٌ في حالٍ غيرِ جاهزة: {record.get('status')}")
    outcome = verify(record)
    if not outcome["reproduced"]:
        raise CountingRefused("إعادةُ التنفيذ لم تُطابق الشهادة؛ فلا يمرّ عدّ.")
    counts = dict.fromkeys(A116, 0)
    for atom in record["canonical_atoms"]:
        counts[atom] += 1
    return counts
