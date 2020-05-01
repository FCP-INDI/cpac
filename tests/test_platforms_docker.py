import os

from cpac.__main__ import main


def test_run_missing_data_config(capfd, tmp_path):

    wd = tmp_path

    main((
        f'cpac --platform docker run {wd} {wd} test_config'
    ).split(' '))
    captured = capfd.readouterr()

    assert('not empty' in '\n'.join([captured.err, captured.out]))
