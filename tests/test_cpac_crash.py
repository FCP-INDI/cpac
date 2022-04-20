import os
import sys

from unittest import mock

import pytest

from cpac.__main__ import run
from .CONSTANTS import set_commandline_args


@pytest.mark.parametrize('argsep', [' ', '='])
def test_cpac_crash(argsep, capsys, platform, tag):
    args = set_commandline_args(platform, tag, argsep)
    crashfile = os.path.join(
        os.path.dirname(__file__), 'test_data', 'test_pickle.pklz'
    )
    argv = ['cpac', 'crash', crashfile]
    argv = [arg for arg in ' '.join([
        w for w in ['cpac', args, 'crash', crashfile] if len(w)
    ]).split(' ') if arg]
    with mock.patch.object(sys, 'argv', argv):
        run()
        captured = capsys.readouterr()
        assert "MemoryError" in captured.out or "MemoryError" in captured.err
