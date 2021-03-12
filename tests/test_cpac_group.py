import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import args_before_after, set_commandline_args


@pytest.mark.parametrize('argsep', [' ', '='])
def test_utils_help(argsep, capsys, platform=None, tag=None):
    def run_test(argv, platform):
        with mock.patch.object(sys, 'argv', argv):
            run()
            captured = capsys.readouterr()
            if platform is not None:
                assert platform.title() in captured.out
            assert 'COMMAND' in captured.out

    argv = 'group --help'
    args = set_commandline_args(platform, tag, argsep)
    if len(args):
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before, platform)
        # test with args after command
        run_test(after, platform)
    else:
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '), platform)
