import json, collections, math
FATHA, DAMMA, KASRA, SUKUN, SHADDA = 'َ', 'ُ', 'ِ', 'ْ', 'ّ'
FT, DT, KT, DAG = 'ً', 'ٌ', 'ٍ', 'ٰ'
HAR = {FATHA: 'a', DAMMA: 'u', KASRA: 'i'}
TAN = {FT: 'a', DT: 'u', KT: 'i'}
MARKS = set([FATHA, DAMMA, KASRA, SUKUN, SHADDA, FT, DT, KT, DAG])
CLITIC = set('وفألكب')
BISM = 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ '

def verses():
    d = json.load(open('q.json'))
    for k in d:
        for v in d[k]:
            t = v['text']
            if v['verse'] == 1 and v['chapter'] != 1 and t.startswith(BISM):
                t = t[len(BISM):]
            yield v['chapter'], v['verse'], t

def clusters(w):
    out = []
    for ch in w:
        if ch in MARKS and out:
            out[-1][1].append(ch)
        else:
            out.append([ch, []])
    return out

def segment(w):
    """returns (segs, info). segs: list of (letter, state, kind). state in a,u,i,S"""
    cl = clusters(w)
    segs, info = [], {'wasla': False, 'anom': [], 'bare': not any(ch in MARKS for ch in w)}
    for idx, (b, m) in enumerate(cl):
        h = next((HAR[x] for x in m if x in HAR), None)
        t = next((TAN[x] for x in m if x in TAN), None)
        prev = segs[-1][1] if segs else None
        nxt = cl[idx + 1] if idx + 1 < len(cl) else None
        if b == 'آ':
            segs += [('ء', 'a', 'har'), ('ا', 'S', 'madd')]
            continue
        if SHADDA in m:
            segs.append((b, 'S', 'gem1'))
            if h: segs.append((b, h, 'har'))
            elif t: segs += [(b, t, 'har'), ('ن', 'S', 'tanwin')]
            else: info['anom'].append(('shadda-no-har', w))
        elif h:
            segs.append((b, h, 'har'))
        elif t:
            segs += [(b, t, 'har'), ('ن', 'S', 'tanwin')]
        elif SUKUN in m:
            kind = 'lin' if (b in 'وي' and prev == 'a') else 'plain'
            segs.append((b, 'S', kind))
        else:  # unmarked
            nxt_sak = nxt is not None and (SUKUN in nxt[1] or SHADDA in nxt[1] or (not nxt[1] and nxt[0] not in 'اوىي'))
            if b == 'ا' and idx == 0:
                info['wasla'] = True
            elif b == 'ا' and prev == 'a' and nxt_sak and all(c[0] in CLITIC for c in cl[:idx]) and idx <= 2:
                info['wasla'] = True  # wasla after clitic(s)
            elif b in 'اى' and prev == 'a':
                segs.append((b, 'S', 'madd'))
            elif b == 'و' and prev == 'u':
                segs.append((b, 'S', 'madd'))
            elif b == 'ي' and prev == 'i':
                segs.append((b, 'S', 'madd'))
            elif b == 'ا' and (prev == 'S' or prev is None or prev in 'iu'):
                if prev in ('i', 'u') and idx <= 2:
                    info['wasla'] = True  # e.g. بِاللَّهِ
                pass  # silent alif
            elif b in 'وي' and prev == 'a':
                segs.append((b, 'S', 'lin'))
            elif b == 'ى' and segs and segs[-1][2] == 'tanwin':
                pass  # silent alif maqsura after tanwin
            elif nxt is not None and SHADDA in nxt[1]:
                pass  # assimilated (shamsi lam / idgham)
            elif b not in 'اى':
                segs.append((b, 'S', 'plain'))  # unmarked consonant = sakin in Tanzil simple
            else:
                info['anom'].append((b, w))
                continue
        if DAG in m and not (segs and segs[-1][2] == 'madd' and segs[-1][0] == b):
            segs.append(('ا', 'S', 'madd'))
    return segs, info
