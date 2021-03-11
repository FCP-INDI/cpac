import os
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import set_commandline_args


def test_cpac_crash(capsys, platform, tag):
    args = set_commandline_args(platform, tag)
    crashfile = os.path.join(
        os.path.dirname(__file__), 'test_data', 'test_pickle.pklz'
    )
    argv = (
        f'cpac {args} crash {crashfile}'
    ).split(' ')
    with mock.patch.object(sys, 'argv', argv):
        run()
        captured = capsys.readouterr()
        assert(
            "MemoryError" in captured.out or "MemoryError" in captured.err
        )
