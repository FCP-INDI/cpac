import os
import pytest
import subprocess

from contextlib import redirect_stdout
from io import StringIO
from subprocess import CalledProcessError
from utils import recursive_remove_dir

from cpac.__main__ import main

def test_run_missing_data_config():

    import tempfile
    from datetime import date

    wd = tempfile.mkdtemp(prefix='cpac_pip_temp_')
    config_dir = os.path.dirname(__file__)

    f = StringIO()
    with redirect_stdout(f):
        args = (
            f'cpac --platform docker run {wd} {wd} test_config'
        ).split(' ')
        main(args)
    o = f.getvalue()

    assert('not empty' in o)

    recursive_remove_dir(wd)
