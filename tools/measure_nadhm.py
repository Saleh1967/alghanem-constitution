#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
قياس النظم على المصحف — سطحي، بلا ادّعاء معنى (الخطوة ٢ من خطة الجرجاني).
يعدّ بدائل الجرجاني (§75) صورًا سطحية بعد تجريد التمييل:
  - زوج الجهة/الزمن: إن × إذا (مع صيغ مسبوقة بواو/فاء)
  - أدوات الوصل: أو × أم × لكن × بل (والواو والفاء وثم للاكتمال)
القياس الكامل بعلاقات التعليق الاثنتي عشرة (§48) يتطلب MASAQ (عمود Syntactic_Role)
— مخططُه المطلوب في data/masaq_schema.json ولا يُختلق قبل توفره.
"""
import json, re, sys, hashlib, pathlib

DIACRITICS = re.compile(r'[\u064B-\u0652\u0670\u0640]')  # تنوين+حركات+مد+تطويل
TARGETS = {
    "modal_pair": ["إن", "إذا"],
    "connectives": ["أو", "أم", "لكن", "بل", "و", "ف", "ثم"],
}
PREFIXED = ["وإن", "فإن", "وإذا", "فإذا"]


def normalize(line: str) -> list:
    return DIACRITICS.sub('', line).split()


def measure(corpus_path: str) -> dict:
    p = pathlib.Path(corpus_path)
    raw = p.read_bytes()
    strict = {k: 0 for k in TARGETS["modal_pair"] + TARGETS["connectives"]}
    prefixed = {k: 0 for k in PREFIXED}
    verses = 0
    for line in raw.decode('utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        verses += 1
        toks = normalize(line)
        for t in toks:
            if t in strict:
                strict[t] += 1
            if t in prefixed:
                prefixed[t] += 1
    return {
        "corpus": {"path": str(p), "sha256_16": hashlib.sha256(raw).hexdigest()[:16],
                   "verses": verses, "bytes": len(raw)},
        "kind": "surface_counts_only",
        "caveat": ("عدّ صوري بعد تجريد التمييل؛ لا تفريق سياقي: «لا» و«ما» يشملان كل استعمالاتهما "
                   "فهو حدّ أعلى لاستعمالهما الجهوي لا قياس دلالته؛ الواو والفاء تلتصق بالكلمة فلا تنكشف "
                   "عدّتُهما المستقلة (و=0، ف=0 انعكاس التصاق لا غياب)؛ لا ادّعاء معنى — قياس فقط"),
        "counts": {"strict_tokens": strict, "waaw_faa_prefixed": prefixed},
        "rules_source": "jurjani_nadhm.json §75 particle_rules",
    }


def main() -> int:
    corpus = sys.argv[1] if len(sys.argv) > 1 else "../hamil-constitution/corpora/quran-simple-enhanced.txt"
    out = measure(corpus)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
