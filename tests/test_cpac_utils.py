"""Tests for cpac utilities"""
# pylint: disable=too-many-arguments
import os
import sys
from unittest import mock
import pytest
from cpac.__main__ import run
from .CONSTANTS import args_before_after, set_commandline_args


@pytest.mark.parametrize('argsep', [' ', '='])
@pytest.mark.parametrize('helpflag', ['--help', '-h'])
def test_utils_help(argsep, capsys, helpflag, image, platform, tag):
    def run_test(argv, platform):
        argv = [arg for arg in argv if arg]
        with mock.patch.object(sys, 'argv', argv):
            run()
            captured = capsys.readouterr()
            if platform is not None:
                assert platform.title() in captured.out
            assert 'COMMAND' in captured.out

    args = set_commandline_args(image, platform, tag, argsep)
    argv = f'utils {helpflag}'
    if args:
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before, platform)
        # test with args after command
        run_test(after, platform)
    elif tag=='latest':
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '), platform)


@pytest.mark.parametrize('argsep', [' ', '='])
def test_utils_new_settings_template(argsep, tmp_path, image, platform, tag):
    """Test 'utils data_config new_settings_template' command"""
    wd = tmp_path  # pylint: disable=invalid-name

    def run_test(argv):
        argv = [arg for arg in argv if arg]
        with mock.patch.object(sys, 'argv', argv):
            run()
            template_path = os.path.join(wd, 'data_settings.yml')
            assert os.path.exists(template_path)

    args = set_commandline_args(image, platform, tag, argsep)
    argv = f'--working_dir {wd} utils data_config new_settings_template'
    if args:
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before)
        # test with args after command
        run_test(after)
    elif tag=='latest':
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '))
