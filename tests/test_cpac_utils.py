import os
import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import SINGULARITY_OPTION
PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION()]


@pytest.mark.parametrize('args,platform', [
    (PLATFORM_ARGS[0], 'docker'),
    (PLATFORM_ARGS[1], 'singularity'),
    ('', '')
])
def test_utils_help(args, capsys, platform):
    argv = ['cpac', *args.split(' '), 'utils', '--help']
    with mock.patch.object(sys, 'argv', [arg for arg in argv if len(arg)]):
        run()
        captured = capsys.readouterr()
        if len(platform):
            assert platform.title() in captured.out
        assert 'COMMAND' in captured.out


@pytest.mark.parametrize('args', PLATFORM_ARGS)
def test_utils_new_settings_template(args, tmp_path):
    wd = tmp_path
    argv = (
        f'cpac {args} --working_dir {wd} --temp_dir {wd} --output_dir {wd} '
        f'utils data_config new_settings_template'
    ).split(' ')
    with mock.patch.object(sys, 'argv', argv):
        run()
        template_path = os.path.join(wd, 'data_settings.yml')
        assert(os.path.exists(template_path))
