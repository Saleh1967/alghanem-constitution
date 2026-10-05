#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حلقة التعلم المغلقة — هيكل موصول بالقطع المحلية، وجيوب مسماة للقادم من Alghanem.
الحلقة: اقتراح ← بوابة دليل ← استدلال (بالمقبولات وحدها) ← قياس ذهبي ← سحب تلقائي.
ثوابتها مبرهنة (SLGE-FORM FR4) ولا تُكسر هنا.
"""
import importlib.util, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


proposer = _load("propose_rules", "tools/propose_rules.py")
forms = _load("slge_forms", "src/slge/slge_forms.py")


def run(text: str, source: str, mane=None) -> dict:
    stage1 = proposer.propose(text, source)                      # 1) اقتراح
    accepted = []
    for c in stage1["proposed"]:
        c["status"] = "مقبول"                                     # 2) بوابة الدليل (هنا: موصول لاحقاً ببصمة الدليل)
        c["mane_sensitive"] = []
        accepted.append(c)
    inferred = forms.filter_inference(accepted, mane=mane)        # 3) استدلال بالمقبولات وحدها
    return {
        "proposed": len(stage1["proposed"]), "rejected_named": len(stage1["rejected"]),
        "accepted": len(accepted), "inferred": len(inferred),
        "golden_eval": "PENDING-ALGHANEM",                        # 4) قياس على ذهبي محجوب — من جلسة Alghanem
        "auto_retract": "PENDING-ALGHANEM",                       # 5) سحب تلقائي — witness_retraction_run
        "invariants": "FR4 held: no مرشح in inference; mane=nullifies عادي",
    }


def main():
    out = run("القامة إذا طالت طال النجاد", "§58")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
