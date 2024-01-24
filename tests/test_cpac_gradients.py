"""Unit tests for the command-line interface module of ``ba-timeseries-gradients``."""
from argparse import Namespace
import logging
from pathlib import Path
import sys
from typing import Callable
from unittest import mock

from _pytest.capture import CaptureFixture
from pytest import fixture

from cpac.__main__ import run
from .CONSTANTS import args_before_after, set_commandline_args


@fixture
def mock_args(tmp_path: Path) -> mock.MagicMock:
    """Return a mock argparse.Namespace object with default values for testing purposes.

    Returns
    -------
    mock.MagicMock: A mock argparse.Namespace object.
    """
    args = mock.MagicMock(spec=Namespace)
    args.verbose = logging.INFO
    args.parcellation = "test.nii.gz"
    args.output_dir = tmp_path / "output"
    args.output_dir.mkdir(exist_ok=True, parents=True)
    args.bids_dir = tmp_path / "bids_dir"
    args.bids_dir.mkdir(exist_ok=True, parents=True)
    args.force = False
    args.output_format = "hdf5"
    return args


def _run_mocked_argv(argv: str, platform: str, run_test: Callable) -> None:
    """Run a test with mocked sys.argv."""
    args = set_commandline_args(platform)
    if len(args):
        before, after = args_before_after(argv, args)
        # test with args before command
        run_test(before)
        # test with args after command
        run_test(after)
    else:
        # test without --platform and --tag args
        run_test(f"cpac {argv}".split(" "))


def _run_error_test(
    argv: list[str], capsys: CaptureFixture, error_excerpt: str
) -> None:
    """Run a test and check for a string in the error message."""
    argv = [arg for arg in argv if arg]
    with mock.patch.object(sys, "argv", argv):
        run()
        captured = capsys.readouterr()
        assert error_excerpt in captured.out + captured.err


def test_raise_invalid_input_existing_output_file(
    capsys: CaptureFixture, mock_args: mock.MagicMock, platform: str
) -> None:
    """Test _raise_invalid_input when output file already exists."""

    def run_test(argv: list[str]) -> None:
        _run_error_test(argv, capsys, "Output file already exists")

    output_file = mock_args.output_dir / "gradients.h5"
    output_file.touch()
    _run_mocked_argv(
        f"gradients {mock_args.bids_dir} {mock_args.output_dir} group",
        platform,
        run_test,
    )


def test_raise_invalid_input_no_input_files(
    capsys: CaptureFixture, mock_args: mock.MagicMock, platform: str
) -> None:
    """Test _raise_invalid_input when no input files are provided."""

    def run_test(argv: list[str]) -> None:
        _run_error_test(argv, capsys, "No input files found")

    _run_mocked_argv(
        f"gradients {mock_args.bids_dir} {mock_args.output_dir} group",
        platform,
        run_test,
    )


def test_raise_invalid_input_no_parcellation(
    capsys: CaptureFixture, mock_args: mock.MagicMock, platform: str
) -> None:
    """Test _raise_invalid_input when no parcellation is provided."""

    def run_test(argv: list[str]) -> None:
        _run_error_test(argv, capsys, "Must provide a parcellation")

    (mock_args.bids_dir / "sub-01/func").mkdir(parents=True)
    (mock_args.bids_dir / "sub-01/func/sub-01_task-rest_bold.nii.gz").touch()
    _run_mocked_argv(
        f"gradients {mock_args.bids_dir} {mock_args.output_dir} group",
        platform,
        run_test,
    )
