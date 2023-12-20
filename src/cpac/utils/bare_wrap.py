#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wrap another Python package without any modifications."""
from argparse import _SubParsersAction, ArgumentParser, HelpFormatter, REMAINDER
from dataclasses import dataclass
from logging import ERROR, log, WARNING
from shutil import which
from subprocess import call as sub_call, CalledProcessError
from sys import exit as sys_exit, version_info
from typing import Any, Literal, Optional, TypedDict

if version_info.minor < 9:  # noqa: PLR2004
    from typing import Dict
else:
    Dict = dict  # type: ignore

from packaging.markers import Marker

try:
    import tomllib
except (ImportError, ModuleNotFoundError):
    import toml

try:
    from ba_timeseries_gradients.parser import get_parser as gradients_parser
except (ImportError, ModuleNotFoundError):
    gradients_parser = None

from cpac.utils import get_project_root

WRAPPED = {}
"""memoization of wrapped packages"""


class ScriptInfo(TypedDict):
    """Info needed for bare package wrapping."""

    command: str
    """The command to run."""
    helpstring: Optional[str]
    """The original usage string."""
    positional_arguments: bool
    """Whether the original command takes positional arguments."""
    url: str
    """The URL to the wrapped package's documentation."""


_SCRIPTS: Dict[str, ScriptInfo] = {
    "gradients": {
        "command": "ba_timeseries_gradients",
        "helpstring": None,
        "positional_arguments": True,
        "url": "https://cmi-dair.github.io/ba-timeseries-gradients/ba_timeseries_gradients.html",
    }
}
"""Info needed for bare package wrapping."""


@dataclass
class WrappedBare:
    """Info needed for bare package wrapping."""

    name: str
    command: str
    _helpstring: Optional[str]
    positional_arguments: bool
    url: str

    @property
    def helpstring(self):
        """Get the helpstring."""
        if self._helpstring is None:
            self._helpstring = f"Extra script {self.command} not found. See {self.url} for more information, or run `pip install cpac[{self.name}]` to install it."
        return self._helpstring.replace(f"usage: {self.command}", f"cpac {self.name}")


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
        help=f"Run {get_wrapped(command).command}",
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
    if version_info.minor < 11:  # noqa: PLR2004
        pyproject = toml.load(get_project_root() / "pyproject.toml")
    else:
        with open(get_project_root() / "pyproject.toml", "rb") as _f:
            pyproject = tomllib.load(_f)
    script = get_wrapped(name)
    try:
        package_info = get_nested(
            pyproject, ["tool", "poetry", "dependencies", script.command]
        )
    except KeyError as ke:
        raise KeyError(f"Package {name} not defined in dependencies") from ke
    marker = Marker(package_info["marker"]) if "marker" in package_info else None
    if marker and marker.evaluate() is False:
        raise EnvironmentError(
            f"Current environment does not meet requirements ({marker}) for package {name}"
        )
    if not check_for_package(script.command):
        sub_call(["poetry", "install", "--extras", name], cwd=get_project_root())
    try:
        sub_call([script.command, *command])
    except CalledProcessError as cpe:
        log(ERROR, str(cpe))
        sys_exit(cpe.returncode)
    sys_exit(0)


def check_for_package(package_name: str) -> bool:
    """Check if a package is installed."""
    return which(package_name) is not None


def get_nested(
    dct: dict, keys: list, error: Literal["raise", "warn", None] = "raise"
) -> Any:
    """Get a nested dictionary value.

    Parameters
    ----------
    dct : dict
        The dictionary to search

    keys : Iterable
        The keys to search for

    error : Literal['raise', 'warn', None]
        How to handle errors:
        'raise' : raise an error
        'warn' : log a warning and return None
        None : return None without a warning

    Returns
    -------
    Any
        The value of the nested key or None

    Examples
    --------
    >>> dct = {'a': {'b': {'c': 1}}}
    >>> get_nested(dct, ['a', 'b', 'c'])
    1
    >>> get_nested(dct, ['a', 'b', 'd'])
    Traceback (most recent call last):
    ...
    KeyError: 'd'
    >>> get_nested(dct, ['a', 'b', 'd'], error=None) is None
    True
    """
    key = keys.pop(0)
    if key in dct:
        if len(keys) == 0:
            return dct[key]
        return get_nested(dct[key], keys, error)
    if error == "raise":
        return dct[key]
    if error == "warn":
        log(WARNING, "Key %s not found in %s", key, dct)
    return None


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
        if gradients_parser is not None:
            _SCRIPTS["gradients"]["helpstring"] = gradients_parser().format_help()
        if name in _SCRIPTS:
            WRAPPED[name] = WrappedBare(
                name,
                _SCRIPTS[name]["command"],
                _SCRIPTS[name]["helpstring"],
                _SCRIPTS[name]["positional_arguments"],
                _SCRIPTS[name]["url"],
            )
        else:
            raise KeyError(f"Package {name} not defined in scripts")
    return WRAPPED[name]


__all__ = ["add_bare_wrapper", "call", "WRAPPED"]
