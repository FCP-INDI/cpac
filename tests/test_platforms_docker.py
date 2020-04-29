import os
import subprocess
from contextlib import redirect_stdout
from cpac.__main__ import main
from io import StringIO
from utils import recursive_remove_dir


def test_run_missing_data_config():
    import tempfile
    from datetime import date

    wd = tempfile.mkdtemp(prefix='cpac_pip_temp_')

    f = StringIO()
    with redirect_stdout(f):
        main((
            f'cpac --platform docker run {wd} {wd} test_config'
        ).split(' '))
    o = f.getvalue()

    assert('not empty' in o)

    recursive_remove_dir(wd)
