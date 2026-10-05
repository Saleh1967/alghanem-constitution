#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
المولِّد (proposer) — يقرأ نصًّا ويقترح قواعد وجودية «مرشّحة» من بنى:
  1) الشرط الزماني: «X إذا V فـ Y» / «إذا V X فـ Y» / «كلما V X V Y»
  2) الأفعال السببية من proposer_lexicon.json: «X يؤدي إلى Y» ونحوها
الحكم الحديد: يقترح ولا يقبل أبدًا. كل مخرج status=مرشح، منزلته عادية
مقترحة، ودرجته أخصّ (لا تُخمَّن مساواة بلا علّة واحدة بدليل).
القبول عمل آخر يحتاج دليل وجودي — انظر CHAPTER-93 (الحال) والبوابات في المعجم.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEX = json.loads((ROOT / "data" / "proposer_lexicon.json").read_text(encoding="utf-8"))
CAUSAL = sorted({c["verb"] for c in LEX["causal_verbs"]}, key=len, reverse=True)

VERB = "(" + "|".join(LEX.get("conditional_verbs", [])) + ")"


def _clean(s: str) -> str:
    return re.sub(r"[\u064B-\u0652\u0670\u0640]", '', s).strip(" .،,؛:؟!«»")


def propose(text: str, source: str = "<نص>") -> dict:
    proposed, rejected = [], []
    s = re.sub(r"[\u064B-\u0652\u0670\u0640]", '', text)

    # 1) الشرط الزماني: «(الفاعل) إذا (فعل1) (فعل2) (مفعول)» — §58
    for m in re.finditer(r"(\S{2,12})\s+(?:إذا|متى)\s+" + VERB + r"\s+" + VERB + r"(?:\s+(\S{2,12}(?:\s+\S{2,12})?))?", s):
        subj, v1, v2, tail = m.group(1), m.group(2), m.group(3), m.group(4)
        antecedent = _clean(f"{subj} {v1}")
        consequent = _clean(tail) if tail else _clean(f"{subj} {v2}")
        _add(proposed, rejected, antecedent, consequent, "شرط زماني", source, m.group(0))

    # 1ب) «كلما (فعل1) (X) (فعل2) (Y)»
    for m in re.finditer(r"كلما\s+" + VERB + r"\s+(\S{2,12}(?:\s+\S{2,12})?)\s+" + VERB + r"\s+(\S{2,12}(?:\s+\S{2,12})?)", s):
        _add(proposed, rejected, _clean(m.group(2)), _clean(m.group(4)), "شرط كلما", source, m.group(0))

    # 2) الأفعال السببية: «X سبب Y»
    for verb in CAUSAL:
        pat = re.compile(r"(\S{2,14}(?:\s+\S{2,14})?)\s+" + re.escape(verb) + r"\s+(\S{2,14}(?:\s+\S{2,14})?)")
        for m in pat.finditer(s):
            _add(proposed, rejected, _clean(m.group(1)), _clean(m.group(2)), f"فعل سببي «{verb}»", source, m.group(0))

    return {"source": source, "proposed": proposed, "rejected": rejected}


def _add(proposed, rejected, antecedent, consequent, via, source, surface):
    if len(antecedent) < 3 or len(consequent) < 3:
        rejected.append({"surface": surface, "reason": "تافه_أو_شبه"}); return
    a_tokens, c_tokens = set(antecedent.split()), set(consequent.split())
    if antecedent == consequent or a_tokens == c_tokens or (a_tokens & c_tokens and len(a_tokens & c_tokens) == len(a_tokens | c_tokens) - 1 and len(a_tokens | c_tokens) <= 3):
        rejected.append({"surface": surface, "reason": "تافه_أو_شبه"}); return
    proposed.append({
        "id": f"CAND-{len(proposed)+1:03d}",
        "rule": f"إذا {antecedent} فـ{consequent}",
        "antecedent": antecedent, "consequent": consequent,
        "via": via, "surface": surface,
        "degree": "أخصّ",
        "manzila": "عادي_مقترح",
        "evidence": {"type": "نص", "source": source, "note": "اقتراح لا قبول"},
        "status": "مرشح",
        "needs": ["قبول بدليل وجودي يوافق منزلته", "تحديد الرافع إن استُعمل عين التالي"]
    })


def main() -> int:
    text = sys.argv[1] if len(sys.argv) > 1 else "القامة إذا طالت طال النجاد"
    src = sys.argv[2] if len(sys.argv) > 2 else "<وسيطة>"
    print(json.dumps(propose(text, src), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
