import os
import pytest
import sys

from datetime import date
from unittest import mock

from cpac.__main__ import run
from CONSTANTS import SINGULARITY_OPTION

PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION()]


@pytest.mark.parametrize('args,helpflag', [
    (arg, flag) for arg in PLATFORM_ARGS for flag in ['--help', '-h']
])
def test_run_help(args, capsys, helpflag):
    argv = ['cpac', *args.split(' '), 'run', helpflag]
    with mock.patch.object(sys, 'argv', argv):
        run()
        captured = capsys.readouterr()
        assert 'participant' in captured.out or 'participant' in captured.err


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_run_test_config(args, tmp_path):
    wd = tmp_path
    argv = (
        f'cpac {args} run '
        f's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} '
        'test_config --participant_ndx=2'
    ).split(' ')
    with mock.patch.object(sys, 'argv', argv):
        run()
        assert(
            any([date.today().isoformat() in fp for fp in os.listdir(wd)])
        )
