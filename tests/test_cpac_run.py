import os
import sys

from datetime import date

from cpac.__main__ import main, run

def test_run_help(capfd):
    sys.argv=['cpac', '--platform', 'docker', 'run', '--help']
    run()

    captured = capfd.readouterr()

    assert 'participant' in captured.out

def test_run_test_config(capsys, tmp_path):
    wd = tmp_path

    main((
        'cpac run '
        f's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} '
        'test_config --participant_ndx=2'
    ).split(' '))

    captured = capsys.readouterr()

    assert(
        any([date.today().isoformat() in fp for fp in os.listdir(wd)])
    )
