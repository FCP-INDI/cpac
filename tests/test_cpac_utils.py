import os
import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import args_before_after, set_commandline_args


@pytest.mark.parametrize('argsep', [' ', '='])
@pytest.mark.parametrize('helpflag', ['--help', '-h'])
def test_utils_help(argsep, capsys, helpflag, platform=None, tag=None):
    def run_test(argv, platform):
        with mock.patch.object(sys, 'argv', argv):
            run()
            captured = capsys.readouterr()
            if platform is not None:
                assert platform.title() in captured.out
            assert 'COMMAND' in captured.out

    args = set_commandline_args(platform, tag, argsep)
    argv = f'utils {helpflag}'
    if len(args):
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before, platform)
        # test with args after command
        run_test(after, platform)
    else:
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '), platform)


@pytest.mark.parametrize('argsep', [' ', '='])
def test_utils_new_settings_template(
    argsep, tmp_path, platform=None, tag=None
):
    wd = tmp_path

    def run_test(argv):
        with mock.patch.object(sys, 'argv', argv):
            run()
            template_path = os.path.join(wd, 'data_settings.yml')
            assert(os.path.exists(template_path))

    args = set_commandline_args(platform, tag, argsep)
    argv = f'--working_dir {wd} utils data_config new_settings_template'
    if len(args):
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before)
        # test with args after command
        run_test(after)
    else:
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '))
