import os

from cpac.__main__ import main


def test_run_missing_data_config(capfd, tmp_path):

    wd = tmp_path
    config_dir = os.path.dirname(__file__)

    args = (
        f'cpac --platform singularity run {wd} {wd} test_config'
    ).split(' ')
    main(args)

    captured = capfd.readouterr()
    assert(any([
        'not empty' in captured.out,
        'not empty' in captured.err,
        captured.out.strip().endswith(
            "Logging messages will refer to the Singularity paths."
        ) # 🤕
    ]))