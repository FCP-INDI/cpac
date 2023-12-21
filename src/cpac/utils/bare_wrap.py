#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wrap another Python package without any modifications."""
from argparse import _SubParsersAction, ArgumentParser, HelpFormatter, REMAINDER
from dataclasses import dataclass
from importlib.metadata import requires
from logging import ERROR, log
from shutil import which
from subprocess import call as sub_call, CalledProcessError
from sys import exit as sys_exit, version_info
from typing import Optional, TypedDict

if version_info.minor < 9:  # noqa: PLR2004
    from typing import Dict, List, Tuple
else:
    Dict = dict  # type: ignore
    List = list  # type: ignore
    Tuple = tuple  # type: ignore

from packaging.requirements import Requirement

try:
    from ba_timeseries_gradients.parser import get_parser as gradients_parser
except (ImportError, ModuleNotFoundError):
    gradients_parser = None

try:
    from tsconcat.utils import build_bidsapp_group_parser
except (ImportError, ModuleNotFoundError):
    tsconcat_parser = build_bidsapp_group_parser = None

from cpac.utils import INTERVAL_CHECKS, version_tuple

if build_bidsapp_group_parser is not None:
    """
    This parser is built in the main function of the wrapped package https://github.com/cmi-dair/tsconcat/blob/a7e31880431621fe47f48664df4736eb7a455859/src/tsconcat/cli.py#L78C14-L104 , so we recreate it here to generate the usage string for the wrapper."""
    from tsconcat.cli import REDUCE_COLUMNS

    tsconcat_parser = build_bidsapp_group_parser(
        prog="ba-tsconcat", description="Concatenate MRI timeseries."
    )
    tsconcat_parser.add_argument(
        "-c",
        "--concat",
        type=str,
        help=f"Concat across. Can be any combination of {', '.join(REDUCE_COLUMNS)} separated by spaces. "
        f"Output data will be grouped by the set difference.",
        default="ses",
    )
    tsconcat_parser.add_argument(
        "-d",
        "--dry_run",
        action="store_true",
        help="Dry run. Print output directory structure instead of actually doing something. "
        "If this is enabled 'bids_dir' may be a path to a bids2table parquet directory.",
        default=False,
    )
    tsconcat_parser.add_argument(
        "-f",
        "--fake",
        action="store_true",
        help="Fake output. Output a bids2table parquet directory instead of actually doing something.",
        default=False,
    )

_PARSERS = {"gradients": gradients_parser(), "tsconcat": tsconcat_parser}
"""CLI parsers for wrapped packages"""
WRAPPED = {}
"""memoization of wrapped packages"""


class ScriptInfo(TypedDict):
    """Info needed for bare package wrapping."""

    command: str
    """The command to run."""
    helpstring: Optional[str]
    """The original usage string."""
    package: str
    """The canonical name of the wrapped package."""
    positional_arguments: bool
    """Whether the original command takes positional arguments."""
    supported_python: str
    """Constraints for supported Python versions in interval notation."""
    url: str
    """The URL to the wrapped package's documentation."""


_SCRIPTS: Dict[str, ScriptInfo] = {
    "gradients": {
        "command": "ba_timeseries_gradients",
        "helpstring": None,
        "package": "ba_timeseries_gradients",
        "positional_arguments": True,
        "supported_python": "[3.11, 3.12)",
        "url": "https://cmi-dair.github.io/ba-timeseries-gradients/ba_timeseries_gradients.html",
    },
    "tsconcat": {
        "command": "ba-tsconcat",
        "helpstring": None,
        "package": "tsconcat",
        "positional_arguments": True,
        "supported_python": "[3.11, 4.0)",
        "url": "https://cmi-dair.github.io/tsconcat/tsconcat.html",
    },
}
"""Info needed for bare package wrapping."""


@dataclass
class WrappedBare:
    """Info needed for bare package wrapping."""

    name: str
    """The cpac command string."""
    command: str
    """The wrapped command."""
    _helpstring: Optional[str]
    """The original usage string."""
    package: str
    """The canonical name of the wrapped package."""
    positional_arguments: bool
    """Whether the original command takes positional arguments."""
    supported_python_range: str
    """Constraints for supported Python versions in interval notation."""
    url: str
    """The URL to the wrapped package's documentation."""

    @property
    def helpstring(self):
        """Get the helpstring."""
        if self._helpstring is None:
            if not self.supported_python:
                self._helpstring = f"Extra command '{self.name}' not supported on Python {f'{version_info.major}.{version_info.minor}.{ version_info.micro}'}; supported Python versions range is {self.supported_python_range}.\n\nSee {self.url} for more information and system requirements."
            else:
                self._helpstring = f"Extra package {self.package} not found. See {self.url} for more information and system requirements, or run `pip install cpac[{self.name}]` to try to install it."
        return self._helpstring.replace(f"usage: {self.command}", f"cpac {self.name}")

    @property
    def split_range(self) -> Tuple[str, str]:
        """Split the supported Python range into min and max."""
        if not hasattr(self, "_split_range"):
            py_min, py_max = (
                _.strip() for _ in self.supported_python_range.split(",", 1)
            )
            self._split_range = (py_min, py_max)
        return self._split_range

    @property
    def supported_python(self) -> bool:
        """Whether the wrapped package supports the current Python version."""
        py_min, py_max = self.split_range
        return getattr(version_info, INTERVAL_CHECKS[py_min[0]])(
            version_tuple(py_min[1:])
        ) and getattr(version_info, INTERVAL_CHECKS[py_max[-1]])(
            version_tuple(py_max[:-1])
        )


class WrappedHelpFormatter(HelpFormatter):
    """HelpFormatter that wraps the usage string."""

    def add_arguments(self, actions):
        """Don't add arguments."""
        pass


def add_bare_wrapper(parser: _SubParsersAction, command: str) -> None:
    """Add a bare wrapper to the parser.

    Parameters
    ----------
    parser : _SubParsersAction
        The subparsers to add the wrapper to

    command : str
        The command to wrap
    """
    from cpac.__main__ import ExtendAction

    bare_parser: ArgumentParser = parser.add_parser(
        command,
        formatter_class=WrappedHelpFormatter,
        help=f"Run {get_wrapped(command).package}",
        usage=get_wrapped(command).helpstring,
    )
    bare_parser.add_argument("args", nargs=REMAINDER)
    bare_parser.register("action", "extend", ExtendAction)


def call(name: str, command: list) -> None:
    """Call a bare-wrapped command.

    Parameters
    ----------
    name : str
        The name of the package to call

    command : list
        The command to run
    """
    script = get_wrapped(name)
    cpac_requires = requires("cpac") or []
    _requirements: List[Requirement] = [Requirement(req) for req in cpac_requires]
    requirements: Dict[str, Requirement] = {req.name: req for req in _requirements}
    del _requirements
    try:
        package_info = requirements[script.package]
    except KeyError as ke:
        raise KeyError(f"Package {name} not defined in dependencies") from ke
    marker = getattr(package_info, "marker", None)
    if marker and marker.evaluate({"extra": name}) is False:
        raise EnvironmentError(
            f"Current environment does not meet requirements ({marker}) for package {name}"
        )
    try:
        sub_call([script.command, *command])
    except CalledProcessError as cpe:
        log(ERROR, str(cpe))
        sys_exit(cpe.returncode)
    sys_exit(0)


def check_for_package(package_name: str) -> bool:
    """Check if a package is installed."""
    return which(package_name) is not None


def _collect_usage_string(name: str) -> None:
    """Collect a usage string from a wrapped package to use in the helpstring."""
    if _PARSERS[name] is not None:
        try:
            _SCRIPTS[name]["helpstring"] = _PARSERS[name].format_help()
        except AttributeError:
            print(name)


def get_wrapped(name: str) -> WrappedBare:
    """Get the name of the script to run.

    Parameters
    ----------
    name : str
        The name of the package to run

    Returns
    -------
    str
        The name of the script to run
    """
    if name not in WRAPPED:
        _collect_usage_string(name)
        if name in _SCRIPTS:
            WRAPPED[name] = WrappedBare(
                name,
                _SCRIPTS[name]["command"],
                _SCRIPTS[name]["helpstring"],
                _SCRIPTS[name]["package"],
                _SCRIPTS[name]["positional_arguments"],
                _SCRIPTS[name]["supported_python"],
                _SCRIPTS[name]["url"],
            )
        else:
            raise KeyError(f"Package {name} not defined in scripts")
    return WRAPPED[name]


__all__ = ["add_bare_wrapper", "call", "WRAPPED"]
