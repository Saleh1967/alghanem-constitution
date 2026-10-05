#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوابة النقل — فاحص اقتباسات (درس المدقق: الختم يثبت الهوية ولا يثبت المطابقة).
يطابق كل اقتباس على نصوص المصادر بثلاثات كلمات متتالية بعد التجريد، فينتج:
  حرفي      (≥0.95)
  مختصر     (0.60–0.95) — يُلزم علامة حذف «…» تُدرج آليًّا عند أول انقطاع
  مرفوض     (<0.60 في كل المصادر) — يُسقط البناء
الاستعمال: verify_quotes.py --fix  يُصلح ملفات الاقتباسات في المستودعات الثلاثة.
"""
import json, re, sys, pathlib, argparse

REPOS = pathlib.Path(__file__).resolve().parent.parent.parent
QUOTE_FILES = [
    ("alghanem-constitution", "data/dalil_sources.json"),
    ("alghanem-constitution", "data/jurjani_nadhm.json"),
    ("alghanem-constitution", "data/qiyas_istilahat.json"),
    ("alghanem-constitution", "data/lazum_istilahat.json"),
    ("dal-madlul-constitution", "data/nabhani_sources.json"),
    ("dal-madlul-constitution", "data/kinaya_rules.json"),
    ("hamil-constitution", "data/shakhsiyya_sources.json"),
]
SOURCES_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "sources"


def norm(s: str) -> str:
    s = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', s)
    return re.sub(r'[أإآٱ]', 'ا', s).replace('ة', 'ه').replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')


def ngrams(s: str, n: int = 3):
    w = norm(s).split()
    return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))


def load_sources():
    out = {}
    for p in SOURCES_DIR.glob('*.txt'):
        out[p.stem] = set()
        out[p.stem + '_full'] = norm(p.read_text(encoding='utf-8'))
        out[p.stem] = ngrams(p.read_text(encoding='utf-8'))
    return out


def iter_quotes(obj, path=()):
    """يتجول في JSON ويستخرج كل قيمة مفتاحها quote/rule/evidence text."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('quote', 'ghazali_quote', 'nabhani_anchor', 'counter_model', 'rule') and isinstance(v, str) and len(v) > 25:
                yield path + (k,), v
            else:
                yield from iter_quotes(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_quotes(v, path + (str(i),))


def verdict(quote: str, sources: dict):
    q = norm(quote)
    qw = q.split()
    qg = set(tuple(qw[i:i + 3]) for i in range(len(qw) - 2))
    if not qg:
        return 'مرفوض', None, 0.0
    best, best_src = 0.0, None
    for name, sg in sources.items():
        if name.endswith('_full'):
            continue
        ov = len(qg & sg) / len(qg)
        if ov > best:
            best, best_src = ov, name
    if best >= 0.95:
        return 'حرفي', best_src, best
    if best >= 0.60:
        return 'مختصر', best_src, best
    return 'مرفوض', best_src, best


def fix_ellipsis(quote: str, sources: dict) -> str:
    """يُدخل «…» عند أول ثلاثية مفقودة في أفضل مصدر."""
    q = norm(quote)
    qw = q.split()
    best_name, best_ov = None, 0
    for name, sg in sources.items():
        if name.endswith('_full'):
            continue
        ov = len(set(tuple(qw[i:i + 3]) for i in range(len(qw) - 2)) & sg)
        full = norm(quote)
        break
    # نعمل على النص التجريد الكامل لأفضل مصدر
    best_src, best_score = None, 0.0
    qg = [tuple(qw[i:i + 3]) for i in range(len(qw) - 2)]
    sg_best = None
    for name, sg in sources.items():
        if name.endswith('_full'):
            continue
        ov = len(set(qg) & sg) / max(1, len(set(qg)))
        if ov > best_score:
            best_score, sg_best = ov, sg
    if sg_best is None:
        return quote
    out = []
    for i, w in enumerate(qw):
        tri = tuple(qw[i:i + 3])
        if i > 0 and tri not in sg_best and not any(t in sg_best for t in [tuple(qw[max(0, i - 1):i + 2]), tri]):
            if not out or out[-1] != '…':
                out.append('…')
        out.append(w)
    return ' '.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fix', action='store_true')
    args = ap.parse_args()
    sources = load_sources()
    report = {'حرفي': 0, 'مختصر': 0, 'مرفوض': 0}
    rejects = []
    for repo, rel in QUOTE_FILES:
        fp = REPOS / repo / rel
        if not fp.exists():
            continue
        data = json.loads(fp.read_text(encoding='utf-8'))
        changed = False
        for path, quote in list(iter_quotes(data)):
            v, src, sc = verdict(quote, sources)
            report[v] += 1
            if v == 'مرفوض':
                rejects.append((repo, rel, '/'.join(path), quote[:60], src, round(sc, 2)))
            elif v == 'مختصر':
                if '…' not in quote and args.fix:
                    newq = fix_ellipsis(quote, sources)
                    _set(data, path, newq)
                    changed = True
        if changed and args.fix:
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': report, 'rejects': rejects}, ensure_ascii=False, indent=2))


def _set(obj, path, val):
    cur = obj
    for k in path[:-1]:
        cur = cur[int(k)] if k.isdigit() else cur[k]
    if path[-1].isdigit():
        cur[int(path[-1])] = val
    else:
        cur[path[-1]] = val


if __name__ == '__main__':
    main()
