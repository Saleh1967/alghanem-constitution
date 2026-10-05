"""Small independent finite-table checker; no import of producer/bridge.

Proves consistency, injectivity and exact residual capacity of the deposited
finite tables. Does NOT independently adjudicate Arabic projection rules.
"""
import gzip
import hashlib
import json
from collections import defaultdict, Counter
from pathlib import Path


def check(path):
    total = Counter()
    with gzip.open(path, 'rt', encoding='utf-8') as inp:
        for line in inp:
            row = json.loads(line)
            book = row['book']
            content = json.dumps(book,ensure_ascii=False,sort_keys=True,separators=(',', ':')).encode()
            if hashlib.sha256(content).hexdigest() != row['book_digest']:
                raise ValueError('BOOK_CONTENT_DIGEST_MISMATCH')
            domain = book['domain']
            if domain != sorted(set(domain), key=lambda s:s.encode()):
                raise ValueError('DOMAIN_NOT_CANONICAL_UNIQUE')
            if set(domain) != set(book['decisions']):
                raise ValueError('DECISIONS_DO_NOT_EXHAUST_DOMAIN')
            fibers = defaultdict(list)
            for surface in domain:
                d = book['decisions'][surface]
                if d['status'] == 'READY':
                    if not isinstance(d['atoms'],list):
                        raise ValueError('MISSING_ATOMS')
                    fibers[tuple(d['atoms'])].append(surface)
                elif d['atoms'] is not None or not d['reasons']:
                    raise ValueError('UNEXPLAINED_NONREADY_OR_ATOM_LEAK')
            seen = set()
            for atoms, members in fibers.items():
                m = len(members)
                bits = 0
                while 2**bits < m:
                    bits += 1
                if bits and 2**(bits-1) >= m:
                    raise ValueError('NONMINIMAL_FIXED_RESIDUAL_CAPACITY')
                for rank, surface in enumerate(members):
                    key = (atoms, rank)
                    if key in seen or members[rank] != surface:
                        raise ValueError('INJECTIVITY_OR_INVERSE_FAILURE')
                    seen.add(key)
            total['books'] += 1
            total['domain_cases'] += len(domain)
            total['ready_cases'] += len(seen)
            total['fibers'] += len(fibers)
    return dict(total)


if __name__ == '__main__':
    print(json.dumps(check(Path(__file__).with_name('codebooks.jsonl.gz')),indent=2))
