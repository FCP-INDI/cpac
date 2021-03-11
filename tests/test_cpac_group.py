import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import set_commandline_args


def test_utils_help(capsys, platform, tag):
    args = set_commandline_args(platform, tag)
    argv = ['cpac', *args.split(' '), 'group', '--help']
    with mock.patch.object(sys, 'argv', [arg for arg in argv if len(arg)]):
        run()
        captured = capsys.readouterr()
        assert platform.title() in captured.out
        assert 'COMMAND' in captured.out
