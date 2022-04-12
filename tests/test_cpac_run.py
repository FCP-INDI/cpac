import os
import sys

from datetime import date
from unittest import mock

import pytest

from cpac.__main__ import run
from cpac.utils import check_version_at_least
from .CONSTANTS import args_before_after, set_commandline_args

MINIMAL_CONFIG = os.path.join(
    os.path.dirname(__file__), 'test_data', 'minimal.min.yml'
)


@pytest.mark.parametrize('helpflag', ['--help', '-h'])
@pytest.mark.parametrize('argsep', [' ', '='])
def test_run_help(argsep, capsys, helpflag, platform, tag):
    def run_test(argv):
        argv = [arg for arg in argv if arg]
        with mock.patch.object(sys, 'argv', argv):
            run()
            captured = capsys.readouterr()
            assert 'participant' in captured.out + captured.err

    args = set_commandline_args(platform, tag, argsep)
    argv = f'run {helpflag}'
    if len(args):
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before)
        # test with args after command
        run_test(after)
    else:
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '))


@pytest.mark.parametrize('argsep', [' ', '='])
@pytest.mark.parametrize('pipeline_file', [None, MINIMAL_CONFIG])
def test_run_test_config(argsep, pipeline_file, tmp_path, platform, tag):
    """Test 'test_config' run command"""
    def run_test(argv, wd):  # pylint: disable=invalid-name
        argv = [arg for arg in argv if arg]
        with mock.patch.object(sys, 'argv', argv):
            run()
            assert any(
                date.today().isoformat() in fp for fp in os.listdir(wd))

    wd = tmp_path  # pylint: disable=invalid-name
    args = set_commandline_args(platform, tag, argsep)
    pipeline = '' if pipeline_file is None else ' '.join([
        ' --pipeline_file',
        pipeline_file
    ])
    argv = (
        'run '
        f's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} '
        f'test_config --participant_ndx=2{pipeline}'
    )
    if check_version_at_least('1.8.4', platform):
        argv += ' --tracking_opt-out'
    if args:
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before, wd)
        # test with args after command
        run_test(after, wd)
    else:
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '), wd)
