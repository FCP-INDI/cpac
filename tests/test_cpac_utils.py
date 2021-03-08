import os
import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import PLATFORM_ARGS, TAGS


@pytest.mark.parametrize('args,platform', [
    (PLATFORM_ARGS[0], 'docker'),
    (PLATFORM_ARGS[1], 'singularity'),
    ('', '')
])
@pytest.mark.parametrize('tag', TAGS)
def test_utils_help(args, tag, capsys, platform):
    if tag is not None:
        args = args + f' --tag {tag}'
    argv = ['cpac', *args.split(' '), 'utils', '--help']
    print(argv)
    with mock.patch.object(sys, 'argv', [arg for arg in argv if len(arg)]):
        run()
        captured = capsys.readouterr()
        if len(platform):
            assert platform.title() in captured.out
        assert 'COMMAND' in captured.out


@pytest.mark.parametrize('args', PLATFORM_ARGS)
@pytest.mark.parametrize('tag', TAGS)
def test_utils_new_settings_template(args, tag, tmp_path):
    wd = tmp_path
    if tag is not None:
        args = args + f' --tag {tag}'
    argv = (
        f'cpac {args} --working_dir {wd} '
        f'utils data_config new_settings_template'
    ).split(' ')
    with mock.patch.object(sys, 'argv', argv):
        run()
        template_path = os.path.join(wd, 'data_settings.yml')
        assert(os.path.exists(template_path))
