""" Unit tests for the command-line interface (CLI) module """
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import argparse
import logging
import pathlib
from unittest import mock

import pytest

from ba_timeseries_gradients import cli, exceptions


@pytest.fixture
def mock_args() -> mock.MagicMock:
    """Returns a mock argparse.Namespace object with default values for testing purposes.

    Returns:
        mock.MagicMock: A mock argparse.Namespace object.
    """
    args = mock.MagicMock(spec=argparse.Namespace)
    args.verbose = logging.INFO
    args.parcellation = "test.nii.gz"
    args.output_dir = pathlib.Path("/path/to/output")
    args.bids_dir = pathlib.Path("/path/to/bids")
    args.force = False
    args.output_format = "hdf5"
    return args


@pytest.fixture
def mock_files() -> list[str]:
    """Returns a list of mock file paths for testing purposes.

    Returns:
        list[str]: A list of mock file paths.
    """
    return ["/path/to/bids/sub-01/func/sub-01_task-rest_bold.nii.gz"]


def test_get_parser() -> None:
    """Test the _get_parser function to ensure it returns an instance of argparse.ArgumentParser."""
    parser = cli._get_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_raise_invalid_input_existing_output_file(mock_args) -> None:
    """Test _raise_invalid_input when output file already exists."""
    mock_output_file = mock.MagicMock()
    mock_output_file.exists.return_value = True
    mock_args.output_dir = mock_output_file

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._raise_invalid_input(mock_args, [])

    assert "Output file already exists" in str(exc_info.value)


def test_raise_invalid_input_no_input_files(mock_args) -> None:
    """Test _raise_invalid_input when no input files are provided."""
    with pytest.raises(exceptions.InputError) as exc_info:
        cli._raise_invalid_input(mock_args, [])

    assert "No input files found" in str(exc_info.value)


def test_raise_invalid_input_no_parcellation(mock_args, mock_files) -> None:
    """Test _raise_invalid_input when no parcellation is provided."""
    mock_args.parcellation = None

    with pytest.raises(exceptions.InputError) as exc_info:
        cli._raise_invalid_input(mock_args, mock_files)

    assert "Must provide a parcellation" in str(exc_info.value)
