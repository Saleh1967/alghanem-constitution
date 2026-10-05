#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLGE-FORM (FR) — جدول صور الاستدلال الغزالي منفَّذًا، مع ثوابت التعلم.
LAW CODES
  FR1 ثماني خانات: درجتان × أربع صور — لا خانة تاسعة
  FR2 الأخص ينتج صورتين فقط: عين المقدم ونقيض التالي
  FR3 المساوي ينتج أربعًا كلها
  FR4 ثوابت التعلم: المرشح لا يُنتج حكمًا أبدًا؛ والعادية تسقط بحضور مانعها
الجدول مبرهن في Lean بجلسة الأداة (غير مثبتة هنا) — هذا نظيره المنفَّذ بايثون،
والمطابقة بينهما فحص إلزامي عند توفر الأداة.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def forms():
    return {
        ("أخصّ", "عين المقدم"): True, ("أخصّ", "نقيض التالي"): True,
        ("أخصّ", "عين التالي"): False, ("أخصّ", "نقيض المقدم"): False,
        ("مساوٍ", "عين المقدم"): True, ("مساوٍ", "نقيض التالي"): True,
        ("مساوٍ", "عين التالي"): True, ("مساوٍ", "نقيض المقدم"): True,
    }


def produces(degree: str, form: str) -> bool:
    return forms().get((degree, form), False)


def filter_inference(candidates, mane=None):
    """ثوابت التعلم (FR4): لا مرشح في النتيجة؛ والمانع يسقط العادية."""
    out = []
    for c in candidates:
        if c.get("status") == "مرشح":
            continue                                  # المرشح لا يُنتج أبدًا
        if mane is not None and c.get("manzila") == "عادي_مقترح" and mane in (c.get("mane_sensitive") or []):
            continue                                  # المانع القائم يوقفها
        out.append(c)
    return out


def main() -> int:
    f = forms()
    assert len(f) == 8, "FR1"
    assert sum(1 for (d, _), v in f.items() if d == "أخصّ" and v) == 2, "FR2"
    assert all(v for (d, _), v in f.items() if d == "مساوٍ"), "FR3"
    demo = [{"id": "A", "status": "مرشح"}, {"id": "B", "status": "مقبول", "manzila": "عادي_مقترح", "mane_sensitive": ["كسوف"]}]
    assert [c["id"] for c in filter_inference(demo)] == ["B"], "FR4a"
    assert [c["id"] for c in filter_inference(demo, mane="كسوف")] == [], "FR4b"
    print("FR1 cells=8 | FR2 akhass=2 | FR3 musawi=4 | FR4 learning-constants pass")
    print("SLGE-FORM: ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
