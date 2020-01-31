import os
import sys
from contextlib import redirect_stdout
from cpac.__main__ import main, run
from io import StringIO
from utils import recursive_remove_dir

def test_run():
    sys.argv.append('utils')
    sys.argv.append('--help')
    f = StringIO()
    with redirect_stdout(f):
        run()
    o = f.getvalue()

    assert "Docker" in o
    assert "COMMAND" in o
