import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"src/slge"))
import slge, slge_laws
HAR = {"فتح":"َ","كسر":"ِ","ضم":"ُ","سكون":"ْ"}

def test_legacy_bridge_real_equivalence():
    """الجسر القديم يعمل فعلًا (بلا بيانات خارجية) وذرّاته تطابق SLGE على كلمات التدقيق الخمس"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ab", ROOT/"legacy/alghanem_bridge.py")
    ab = importlib.util.module_from_spec(spec); spec.loader.exec_module(ab)
    assert len(ab.ALPHABET) == 29 and len(ab.A116) == 116
    for w in ["كَتَبَ", "ثَلَاثَةً", "أَإِذَا", "لِسُنَّةِ", "بِمَنِ"]:
        rec = ab.bridge(w); v = ab.verify(rec)
        legacy = v.get("canonical_atoms") or rec["canonical_atoms"]
        mine = [c + HAR[s] for c, s in slge_laws.to_atoms(w)]
        assert legacy == mine, (w, legacy, mine)
        assert (v.get("status") or rec.get("status")) == "READY"

def test_legacy_seg_context():
    # المُطبِّع القديم (seg.py) يُغطى بمعالج السياق: بِسْمِ خامًّا، والألفيات بقانون begin
    assert slge_laws.to_atoms("بِسْمِ")[0][1] != "سكون"
    for word in ["ٱلرَّحِيمِ", "ٱلْحَمْدُ", "ٱللَّهِ"]:
        assert slge_laws.begin(slge_laws.to_atoms(word))[0][1] != "سكون", word
