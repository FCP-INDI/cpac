import os
import pytest
import sys

from datetime import date

from cpac.__main__ import run
from cpac.utils import ls_newest
from CONSTANTS import SINGULARITY_OPTION
PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION]


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_run_help(args, capsys):
    sys.argv=['cpac', *args.split(' '), 'run', '--help']
    run()
    captured = capsys.readouterr()
    assert 'participant' in captured.out or 'participant' in captured.err


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_run_test_config(args, capsys, tmp_path):
    wd = tmp_path
    sys.argv=(
        f'cpac {args} run '
        f's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} '
        'test_config --participant_ndx=2'
    ).split(' ')
    run()
    captured = capsys.readouterr()
    assert(
        any([date.today().isoformat() in fp for fp in os.listdir(wd)])
    )


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_run_missing_data_config(args, capsys, tmp_path):
    wd = tmp_path
    sys.argv=(f'cpac {args} run {wd} {wd} test_config').split(' ')
    run()
    captured = capsys.readouterr()
    assert('not empty' in '\n'.join([captured.err, captured.out]))