import os
import pytest
import sys

from datetime import date

from cpac.__main__ import run
from CONSTANTS import SINGULARITY_OPTION


def test_has_singularity_image():
    sys.argv=['cpac', '--platform', 'singularity', 'run', '--help']
    assert SINGULARITY_OPTION()!='--platform singularity'

PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION()]

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