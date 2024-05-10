"""Test actually running C-PAC with cpac."""

from datetime import date, timedelta
import os
from pathlib import Path
import sys
from unittest import mock

import pytest

from cpac.__main__ import run
from cpac.utils import check_version_at_least
from .CONSTANTS import args_before_after, set_commandline_args

MINIMAL_CONFIG = os.path.join(
    os.path.dirname(__file__), "test_data", "minimal.min.yaml"
)


@pytest.mark.parametrize("helpflag", ["--help", "-h"])
@pytest.mark.parametrize("argsep", [" ", "="])
def test_run_help(argsep, capsys, helpflag, image, platform, tag):
    """Test 'help' run command."""

    def run_test(argv):
        argv = [arg for arg in argv if arg]
        with mock.patch.object(sys, "argv", argv):
            run()
            captured = capsys.readouterr()
            assert "participant" in captured.out + captured.err

    args = set_commandline_args(image, platform, tag, argsep)
    argv = f"run {helpflag}"
    if len(args):
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before)
        # test with args after command
        run_test(after)
    else:
        # test without --platform and --tag args
        run_test(f"cpac {argv}".split(" "))


@pytest.mark.parametrize("argsep", [" ", "="])
@pytest.mark.parametrize("pipeline_file", [None, MINIMAL_CONFIG])
def test_run_test_config(argsep, pipeline_file, image, platform, tag, tmp_path):
    """Test 'test_config' run command."""

    def run_test(argv, wd):  # pylint: disable=invalid-name
        os.chdir(wd)
        argv = [arg for arg in argv if arg]
        with mock.patch.object(sys, "argv", argv):
            run()
            possibilities = _where_to_find_runlogs(wd)
            today = date.today()
            datestamps = [
                _date.isoformat()
                for _date in [
                    today,
                    today - timedelta(days=1),
                    today + timedelta(days=1),
                ]
            ]
            assert any(
                datestamp in fp for fp in possibilities for datestamp in datestamps
            ), (
                f"wd: {wd}\n"
                f"expected log ({datestamps[0]} ± 1 day) not found in {possibilities}\n"
            )

    wd = tmp_path  # pylint: disable=invalid-name
    args = set_commandline_args(image, platform, tag, argsep)
    pipeline = (
        "" if pipeline_file is None else " ".join([" --pipeline_file", pipeline_file])
    )
    argv = (
        "run "
        f"s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU {wd} "
        f"test_config --participant_ndx=2{pipeline}"
    )
    if check_version_at_least("1.8.4", platform=platform, image=image):
        argv += " --tracking_opt-out"
    if args:
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before, wd)
        # test with args after command
        run_test(after, wd)
    elif tag == "latest":
        # test without --platform and --tag args
        if image is not None:
            run_test(f"cpac --image{argsep}{image} {argv}".split(" "), wd)
        else:
            run_test(f"cpac {argv}".split(" "), wd)


def _where_to_find_runlogs(_wd) -> list:
    """
    List all the files in both the old and new locations of run logs changed in 1.8.5.

    Parameters
    ----------
    _wd : str or Path

    Returns
    -------
    possibilities : list of str
    """
    possibilities = []
    _wd = Path(_wd)
    if _wd.is_dir():
        # C-PAC < 1.8.5
        for filename in _wd.iterdir():
            if (_wd / filename).is_file():
                possibilities.append(str(filename))
        # C-PAC ≥ 1.8.5
        for subses_dir in _wd.glob("log/pipeline_*/sub-*_ses-*"):
            if subses_dir.is_dir():
                for filename in subses_dir.iterdir():
                    if (subses_dir / filename).is_file():
                        possibilities.append(str(filename))
    return possibilities
