"""Tests for top-level cpac cli."""
import sys
from contextlib import redirect_stdout
from io import StringIO, TextIOWrapper, BytesIO
from unittest import mock

import pytest

from cpac.backends import Backends
from cpac.__main__ import run
from .CONSTANTS import set_commandline_args


def test_loading_message(platform, tag):
    """Test loading message"""
    if platform is not None:
        redirect_out = StringIO()
        with redirect_stdout(redirect_out):
            loaded = Backends(platform, tag=tag)
        with_symbol = ' '.join([
            'Loading',
            loaded.platform.symbol,
            loaded.platform.name
        ])
        assert with_symbol in redirect_out.getvalue()

        redirect_out = TextIOWrapper(
            BytesIO(), encoding='latin-1', errors='strict', write_through=True)
        with redirect_stdout(redirect_out):
            loaded = Backends(platform, tag=tag)
        without_symbol = ' '.join([
            'Loading',
            loaded.platform.name
        ])
        # pylint: disable=no-member
        assert without_symbol in redirect_out.buffer.getvalue().decode()


@pytest.mark.parametrize('argsep', [' ', '='])
def test_pull(argsep, capsys, platform, tag):
    """Test pull command"""
    def run_test(argv):
        argv = [arg for arg in argv if arg]
        with mock.patch.object(sys, 'argv', argv):
            run()
            captured = capsys.readouterr()
            checkstring = f':{tag}' if tag is not None else ':latest'
            outstring = captured.out + captured.err
            assert checkstring in outstring or 'cached' in outstring

    args = set_commandline_args(platform, tag, argsep)

    # test args before command
    run_test(f'cpac {args} pull'.split(' '))

    # test args after command
    run_test(f'cpac pull {args}'.split(' '))
