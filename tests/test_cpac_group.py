import pytest
import sys

from unittest import mock

from cpac.__main__ import run
from CONSTANTS import SINGULARITY_OPTION
PLATFORM_ARGS = ['--platform docker', SINGULARITY_OPTION()]


@pytest.mark.parametrize('args,platform', [
    (PLATFORM_ARGS[0], 'docker'),
    (PLATFORM_ARGS[1], 'singularity')
])
def test_utils_help(args, capsys, platform):
    argv = ['cpac', *args.split(' '), 'group', '--help']
    with mock.patch.object(sys, 'argv', [arg for arg in argv if len(arg)]):
        run()
        captured = capsys.readouterr()
        assert platform.title() in captured.out
        assert 'COMMAND' in captured.out
