import os
import pytest
import sys

from datetime import date
from unittest import mock

from cpac.__main__ import run
from CONSTANTS import set_commandline_args


@pytest.mark.parametrize('helpflag', ['--help', '-h'])
def test_run_help(capsys, helpflag, platform, tag):
    args = set_commandline_args(platform, tag)
    argv = ['cpac', *args.split(' '), 'run', helpflag]
    with mock.patch.object(sys, 'argv', argv):
        run()
        captured = capsys.readouterr()
        assert 'participant' in captured.out or 'participant' in captured.err


def test_run_test_config(platform, tag, tmp_path):
    wd = tmp_path
    args = set_commandline_args(platform, tag)
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
