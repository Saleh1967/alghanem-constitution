import subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINES = sorted((ROOT/"src/slge").glob("*.py"))
def test_all_engines_exit_zero():
    for f in ENGINES:
        assert subprocess.run([sys.executable, str(f)], capture_output=True).returncode == 0, f.name
