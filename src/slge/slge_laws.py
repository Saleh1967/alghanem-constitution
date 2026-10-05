# slge_laws.py — طبقة الإملاء والقوانين الثلاثة، محركاتٌ رسمية داخل SLGE
# القوانين: Q11 الإملاء ذهابًا وإيابًا | Q12 الابتداء | Q13 الوصل (H5) | Q14 الوقف
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import slge

SUN = set("تثدذرزسشصضطظلن")
# محرك الإملاء: ذرّات ⇐⇒ رسم (القواعد الثمان المعلنة)
def to_rasm(cells):
    out, i = [], 0
    while i < len(cells):
        c, s = cells[i]
        if c == "ن" and s == "سكون" and i > 0 and cells[i-1][1] != "سكون":
            v = cells[i-1][1]
            if v == "فتح":
                out.append("ًا") if out[-1].endswith("ا") else out.append("ً")
            else:
                out.append("ٌ" if v == "ضم" else "ٍ")
            i += 1; continue
        mark = {"فتح":"َ","كسر":"ِ","ضم":"ُ","سكون":"ْ"}[s]
        if c == "ء" and i + 1 < len(cells) and cells[i+1] == ("ا","سكون"):
            out.append("آ" if s == "فتح" else "أ" if False else "أ"); i += 2; continue
        if c == "ء":
            out.append({"فتح":"أَ","كسر":"إِ","ضم":"أُ"}[s]); i += 1; continue
        if c == "و" and s == "سكون" and i > 0 and cells[i-1][1] == "ضم":
            out.append("و"); i += 1; continue
        if c == "ي" and s == "سكون" and i > 0 and cells[i-1][1] == "كسر":
            out.append("ى"); i += 1; continue
        out.append(c + mark); i += 1
    return "".join(out)

def to_atoms(word):  # الرسم ⇐ ذرّات (مُطبِّع v5 — القواعد الثمان)
    cells=[]; i=0; n=len(word)
    VOW={"َ":"فتح","ِ":"كسر","ُ":"ضم","ْ":"سكون"}; TW={"ً":"فتح","ٌ":"ضم","ٍ":"كسر"}
    SEAT={"أ":"ء","إ":"ء","ؤ":"ء","ئ":"ء","ة":"ت","ى":"ا","ٱ":"ا"}
    while i < n:
        ch=word[i]
        if ch in "ـٰ": i+=1; continue
        if ch in VOW or ch in TW or ch=="ّ": i+=1; continue
        if ch=="آ": cells+=[("ء","فتح"),("ا","سكون")]; i+=1; continue
        base=SEAT.get(ch,ch)
        if base not in slge.ALPHABET: i+=1; continue
        j=i+1; sh=False; v=None; tw=None
        while j<n and word[j] in ("ّ","ً","ٌ","ٍ","َ","ِ","ُ","ْ"):
            if word[j]=="ّ": sh=True
            elif word[j] in TW: tw=TW[word[j]]
            elif v is None: v=VOW[word[j]]
            j+=1
        if sh: cells.append((base,"سكون"))
        if base=="و" and v is None and j<n and word[j]=="ا" and j+1>=n:
            cells.append(("و","فتح")); i=j+1; continue
        cells.append((base, v or tw or "سكون"))
        if tw:
            if tw=="فتح" and j<n and word[j]=="ا": j+=1
            cells.append(("ن","سكون"))
        if j>=n and base=="ا" and v is None and not sh and len(cells)>=2 and cells[-2][0]=="و" and cells[-2][1]!="سكون": cells.pop()  # الألف الصامتة: بعد واو الجمع فقط — إذا/لا/ما ألفُ مدٍّ لا تُسقط (كشفها الجسر القديم)
        i=j
    return cells

# محرك قانون الابتداء: المطلع من صفٍ متحرك؛ همزة الوصل تُحرَّك
def begin(cells):
    c=list(cells)
    if c and c[0]==("ا","سكون"): c[0]=("ا","فتح")
    if len(c)>2 and c[0][1]!="سكون" and c[1]==("ل","سكون") and c[2][0] in SUN and c[2][1]=="سكون":
        c=[c[0]]+c[2:]
    return c

# محرك قانون الوصل: همزة الوصل تُسقط، والشمسي يُدغم، والوصلة ≠ SS (H5)
def join(prev, nxt):
    c=list(nxt)
    if len(c)>=2 and c[0]==("ا","سكون") and c[1][1]=="سكون": c=c[1:]
    if len(c)>=2 and c[0]==("ل","سكون") and c[1][0] in SUN and c[1][1]=="سكون": c=c[1:]
    out=[]; i=0
    while i<len(c):
        if i+2<len(c) and c[i][1]=="سكون" and c[i+1]==(c[i][0],"سكون") and c[i+2][0]==c[i][0] and c[i+2][1]!="سكون": i+=1
        out.append(c[i]); i+=1
    ok = not (prev and out and prev[-1][1]=="سكون" and out[0][1]=="سكون")
    return out, ok

# محرك قانون الوقف: W — الختام سكون، ونون التنوين والوقاية مع ألفها تحذف
def pause(cells):
    w=list(cells)
    if w[-1]==("ن","سكون") and len(w)>1 and w[-2][1]!="سكون": return w[:-2]+[(w[-2][0],"سكون")]
    if w[-1][0]=="ن" and len(w)>=2 and w[-2][0] in "وا": return w[:-2]
    return w[:-1]+[(w[-1][0],"سكون")] if w[-1][1]!="سكون" else w

if __name__ == "__main__":
    ok = True
    # Q11 الإملاء: ذهاب وإياب على عينات من كل طبقة
    samples = [[("ك","فتح"),("ت","فتح"),("ب","فتح")], [("م","كسر"),("ن","سكون")],
               [("ل","فتح"),("ا","سكون")], [("ء","كسر"),("ذ","فتح"),("ا","سكون")],
               [("ك","فتح"),("ت","فتح"),("ب","فتح"),("ن","سكون")],
               [("ت","كسر"),("ل","سكون"),("ك","فتح")], [("ء","ضم"),("ل","فتح"),("ء","كسر"),("ك","فتح")]]
    fails = [(w, to_atoms(to_rasm(w))) for w in samples if to_atoms(to_rasm(w)) != w]
    if fails: print("   Q11 fails:", fails)
    rt = not fails
    ok &= rt; print(f"  {'✓' if rt else '⛔'} Q11 الإملاء ذهابًا وإيابًا ({len(samples)} عينات)")
    # Q12 الابتداء
    hamd = to_atoms("ٱلْحَمْدُ"); rahman = to_atoms("ٱلرَّحْمَٰنِ")
    q12 = slge.licensed(begin(hamd)) and slge.licensed(begin(rahman)) and begin(hamd)[0][1] != "سكون"
    ok &= q12; print(f"  {'✓' if q12 else '⛔'} Q12 الابتداء: همزة الوصل تُحرَّك والمطلع متحرك")
    # Q13 الوصل: بِسْمِ + الله
    bismi = pauseless = to_atoms("بِسْمِ"); allah = to_atoms("ٱللَّهِ")
    joined, okk = join(bismi, allah)
    q13 = okk and all(not (joined[i][1]=="سكون" and joined[i+1][1]=="سكون") for i in range(len(joined)-1)) and len(joined)>0
    ok &= q13; print(f"  {'✓' if q13 else '⛔'} Q13 الوصل: همزة تُسقط والشمسي يُدغم والوصلة ≠ SS")
    # Q14 الوقف
    kitaban = to_atoms("كِتَابًا"); yafaluna = to_atoms("يَفْعَلُونَ")
    q14 = (len(kitaban) > 2 and pause(kitaban)[-1] == ("ب","سكون")
           and len(pause(yafaluna)) == len(yafaluna) - 2)  # نون الوقاية وألفها تحذفان
    ok &= q14; print(f"  {'✓' if q14 else '⛔'} Q14 الوقف: الختام سكون والتنوين والوقاية يحذفان")
    print("SLGE LAWS:", "ALL PASS — imla + three laws built" if ok else "BREACH")
    sys.exit(0 if ok else 1)
