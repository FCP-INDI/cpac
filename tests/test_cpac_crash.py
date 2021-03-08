import os
import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import PLATFORM_ARGS, TAGS


@pytest.mark.parametrize('args', PLATFORM_ARGS)
@pytest.mark.parametrize('tag', TAGS)
def test_cpac_crash(args, capsys, tag):
    crashfile = os.path.join(
        os.path.dirname(__file__), 'test_data', 'test_pickle.pklz'
    )
    if tag is not None:
        args = args + f' --tag {tag}'
    argv = (
        f'cpac {args} crash {crashfile}'
    ).split(' ')
    with mock.patch.object(sys, 'argv', argv):
        run()
        captured = capsys.readouterr()
        assert(
            "MemoryError" in captured.out or "MemoryError" in captured.err
        )
