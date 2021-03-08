import os
import pytest
import sys

from datetime import date
from unittest import mock

from cpac.__main__ import run
from CONSTANTS import PLATFORM_ARGS, TAGS


@pytest.mark.parametrize('args', PLATFORM_ARGS)
@pytest.mark.parametrize('tag', TAGS)
@pytest.mark.parametrize('helpflag', ['--help', '-h'])
def test_run_help(args, tag, helpflag, capsys):
    if tag is not None:
        args = args + f' --tag {tag}'
    argv = ['cpac', *args.split(' '), 'run', helpflag]
    with mock.patch.object(sys, 'argv', argv):
        run()
        captured = capsys.readouterr()
        assert 'participant' in captured.out or 'participant' in captured.err


@pytest.mark.parametrize('args', PLATFORM_ARGS)
@pytest.mark.parametrize('tag', TAGS)
def test_run_test_config(args, tag, tmp_path):
    wd = tmp_path
    if tag is not None:
        args = args + f' --tag {tag}'
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
