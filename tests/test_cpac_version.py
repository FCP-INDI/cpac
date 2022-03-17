"""Test version-checking commands"""
import pytest
import sys

from unittest import mock

from cpac import __version__
from cpac.__main__ import run
from .CONSTANTS import set_commandline_args

wrapper_version_string = f'cpac (convenience wrapper) version {__version__}'


def startswith_cpac_version(captured):
    """Check if captured text starts with cpac version

    Parameters
    ----------
    captured : str

    Returns
    -------
    bool
    """
    return captured.out.strip().startswith(wrapper_version_string)


@pytest.mark.parametrize('argsep', [' ', '='])
def test_cpac_version(argsep, capsys, platform=None, tag=None):
    r"""Test `cpac version`"""
    def run_test(argv, platform):
        with mock.patch.object(sys, 'argv', argv):
            run()
            captured = capsys.readouterr()
            assert startswith_cpac_version(captured)
            assert 'C-PAC version ' in captured.out
            if platform is not None:
                assert platform.title() in captured.out
            else:
                assert 'Docker' in captured.out
    args = set_commandline_args(platform, tag, argsep)
    argv = 'version'


def test_cpac__version(capsys):
    r"""Test `cpac --version`"""
    with mock.patch.object(sys, 'argv', ['cpac', '--version']):
        with pytest.raises(SystemExit):
            run()
        captured = capsys.readouterr()
        assert startswith_cpac_version(captured)
