import os
import subprocess
from contextlib import redirect_stdout
from cpac.__main__ import main
from io import StringIO
from utils import recursive_remove_dir

def test_run_help():
    o = subprocess.getoutput('cpac run --help')

    assert "participant" in o

def test_run_test_config():
    import tempfile
    from datetime import date

    wd = tempfile.mkdtemp(prefix='cpac_pip_temp_')

    f = StringIO()
    with redirect_stdout(f):
        main((
            'cpac run '
            f's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} '
            'test_config --participant_ndx=2'
        ).split(' '))
    o = f.getvalue()

    print(wd)

    print(os.listdir(wd))

    print(date.today().isoformat())

    assert(
        any([date.today().isoformat() in fp for fp in os.listdir(wd)])
    )

    recursive_remove_dir(wd)
