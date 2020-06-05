import os
import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import PLATFORM_ARGS


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_utils_new_settings_template(args, capsys):
    crashfile = os.path.join(
        os.path.dirname(__file__), 'test_data', 'test_pickle.pklz'
    )
    argv = (
        f'cpac {args} crash {crashfile}'
    ).split(' ')
    with mock.patch.object(sys, 'argv', argv):
        run()
        captured = capsys.readouterr()
        assert("MemoryError" in captured.out or "MemoryError" in captured.err)
