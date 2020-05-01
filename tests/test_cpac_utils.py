import os
import sys
from shutil import rmtree

from cpac.__main__ import main, run

def test_utils_help(capfd):
    sys.argv=['cpac', '--platform', 'docker', 'utils', '--help']
    run()

    captured = capfd.readouterr()

    assert 'Docker' in captured.out
    assert 'COMMAND' in captured.out

def test_utils_new_settings_template(tmp_path):
    wd = tmp_path
    main((
        f'cpac --platform docker --working_dir {wd} --temp_dir {wd} --output_dir {wd} '
        f'utils data_config new_settings_template'
    ).split(' '))
    template_path = os.path.join(wd, 'data_settings.yml')

    assert(os.path.exists(template_path))
