import os
import pytest
import sys

from datetime import date
from unittest import mock

from cpac.__main__ import run
from CONSTANTS import args_before_after, set_commandline_args


@pytest.mark.parametrize('helpflag', ['--help', '-h'])
@pytest.mark.parametrize('argsep', [' ', '='])
def test_run_help(argsep, capsys, helpflag, platform=None, tag=None):
    def run_test(argv):
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
def test_run_test_config(argsep, tmp_path, platform=None, tag=None):
    def run_test(argv):
        with mock.patch.object(sys, 'argv', argv):
            run()
            assert(
                any([date.today().isoformat() in fp for fp in os.listdir(wd)])
            )

    wd = tmp_path
    args = set_commandline_args(platform, tag, argsep)
    argv = (
        'run '
        f's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} '
        'test_config --participant_ndx=2'
    )
    if len(args):
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before)
        # test with args after command
        run_test(after)
    else:
        # test without --platform and --tag args
        run_test(f'cpac {argv}'.split(' '))
