#!/usr/bin/env python3
import hashlib, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
ok = True
m = json.loads((ROOT/"MANIFEST.json").read_text(encoding="utf-8"))
for rel, rec in sorted(m["files"].items()):
    p = ROOT/rel
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != rec["sha256"]:
        print("⛔ بصمة:", rel); ok = False
for f in sorted((ROOT/"src/slge").glob("*.py")):
    r = subprocess.run([sys.executable, str(f)], capture_output=True)
    if r.returncode: print("⛔ محرك:", f.name); ok = False
print("VERIFY:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
