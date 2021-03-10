import os
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import set_commandline_args


def test_utils_help(capsys, platform, tag):
    args = set_commandline_args(platform, tag)
    argv = ['cpac', *args.split(' '), 'utils', '--help']
    print(argv)
    with mock.patch.object(sys, 'argv', [arg for arg in argv if len(arg)]):
        run()
        captured = capsys.readouterr()
        if len(platform):
            assert platform.title() in captured.out
        assert 'COMMAND' in captured.out


def test_utils_new_settings_template(platform, tag, tmp_path):
    args = set_commandline_args(platform, tag)
    wd = tmp_path
    argv = (
        f'cpac {args} --working_dir {wd} '
        f'utils data_config new_settings_template'
    ).split(' ')
    with mock.patch.object(sys, 'argv', argv):
        run()
        template_path = os.path.join(wd, 'data_settings.yml')
        assert(os.path.exists(template_path))
