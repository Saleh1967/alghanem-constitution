# slge_wazun.py — محرك أوزان «على بُنيَانِهم»: الاستخراج من النشرة المشكولة المودعة
# الدين المعلن: لا نشرة مشكولة لأبواب سيبويه مودعة في المستودعات، ولن تُشكَّل من الذاكرة.
# فهذا المحرك كاملٌ كآلة، بانتظار البيان — وفي غيابه يُبلَّغ «واقفًا على البوابة» لا فاشلاً.
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import slge, slge_laws

PUBLICATION = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "abwab_mushakkala.json"
# مخطط النشرة المطلوب إيداعها (كل بابٍّ: مشكوله + موضعه من الطبعة):
# [{"bab": "فَعَلَ", "mushakkala": "فَعَلَ يَفْعُلُ", "source": "K. I, ص ١٤، س ٥"}, ...]

def extract_from_mushakkala(pub):
    """النشرة المشكولة ⇒ أنماط الخلايا + المواضع الجذرية + الزوائد — بقوانين المشروع نفسها"""
    out = []
    for row in pub:
        cells = slge_laws.to_atoms(slge_laws.normalize(row["mushakkala"].replace(" ", "")))
        assert slge.licensed(cells), row
        rootish = [c for c in "فعل" if c in row["mushakkala"]]
        zaids = [(c, s) for i, (c, s) in enumerate(cells) if c not in rootish]
        out.append({"bab": row["bab"], "pattern": "".join("M" if s != "سكون" else "S" for _, s in cells),
                    "cells": cells, "zaids": zaids, "source": row["source"]})
    return out

def compare_with_freeze(extracted):
    frozen = json.loads((pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "freeze_wazn.json")
                        .read_text(encoding="utf-8"))
    fr_pats = {w["wazn"] for w in frozen["inventory"]}
    return {"matched": [e["bab"] for e in extracted if e["bab"] in fr_pats],
            "new": [e for e in extracted if e["bab"] not in fr_pats]}

if __name__ == "__main__":
    if not PUBLICATION.exists():
        print("  ⏸ SLGE-WAZUN واقف على بوابة الإيداع:")
        print(f"    المطلوب: data/abwab_mushakkala.json — نشرة مشكولة لأبواب الأبنية بمواضعها من طبعة هارون")
        print("    الحال: غير مودعة — فدعوى الإغلاق المعجمي في ساق الأوزان تبقى B-مشروطة، لا مثبتة ولا منفية")
        print("    والمحرك جاهز: أودِع النشرة ⇒ يُستخرج بالقوانين نفسها ويُقارن بالجرد المجمد فورًا")
        sys.exit(0)  # واقف لا فاشل — البوابة معلنة
    pub = json.loads(PUBLICATION.read_text(encoding="utf-8"))
    ex = extract_from_mushakkala(pub)
    cmp = compare_with_freeze(ex)
    print(f"  ✓ استُخرج {len(ex)} بابًا من النشرة المشكولة | مطابق للجرد: {len(cmp['matched'])} | جديد: {len(cmp['new'])}")
    sys.exit(0)
