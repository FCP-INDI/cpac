"""Constants for tests."""

# pylint: disable=invalid-name
from typing import Optional

TAGS = [None, "latest", "nightly"]


def args_before_after(argv: str, args: str) -> tuple[list[str], list[str]]:
    """
    Create a mock sys.argv with arguments before and one with arguments after the command and its arguments.

    Parameters
    ----------
    argv : str
        the command and its arguments

    args : str
        --platform and --image arguments (if any)

    Returns
    -------
    before : list
        f'cpac {args} {argv}'.split(' ')
    after : list
        f'cpac {argv} {args}'.split(' ')
    """
    argv = single_space(argv).strip()
    args = single_space(args).strip()
    if argv.startswith("cpac"):
        argv = argv.lstrip("cpac").strip()
    if args is not None and len(args):
        before = f"cpac {args} {argv}".split(" ")
        after = f"cpac {argv} {args}".split(" ")
    else:
        before = f"cpac {argv}".split(" ")
        after = before
    return before, after


def set_commandline_args(
    image: Optional[str] = None,
    platform: Optional[str] = None,
    tag: Optional[str] = None,
    sep: str = " ",
) -> str:
    """Turn pytest commandline options into mock cpac commandline option strings."""
    args = ""
    if image is not None:
        args += f" --image{sep}{image.lower()}"
    if platform is not None:
        args += f" --platform{sep}{platform.lower()} "
    if tag and tag is not None:
        args = args + f" --tag{sep}{tag} "
    return args


def single_space(string):
    """Remove spaces from a string.

    Parameters
    ----------
    string : str

    Returns
    -------
    string : str
    """
    while "  " in string:
        string = string.replace("  ", " ")
    return string
