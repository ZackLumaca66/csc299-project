import subprocess
import sys
from pathlib import Path


SED_TOOL = Path(__file__).resolve().parents[1] / 'scripts' / 'pytools' / 'sed_compat.py'


def run_sed(args, input_text=None):
    cmd = [sys.executable, str(SED_TOOL)] + args
    proc = subprocess.run(cmd, input=input_text, text=True, capture_output=True)
    return proc


def test_basic_replacement():
    r = run_sed(['-e', 's/hello/world/g'], input_text='hello hello\n')
    assert r.returncode == 0
    assert r.stdout == 'world world\n'


def test_inplace_file(tmp_path):
    p = tmp_path / 'sample.txt'
    p.write_text('foo-\n')
    r = run_sed(['-i', '-e', 's/-$//'], input_text=None, )
    # calling without file should be harmless; now run inplace on file
    r = run_sed(['-i', '-e', 's/-$//', str(p)])
    assert r.returncode == 0
    assert p.read_text() == 'foo\n'
