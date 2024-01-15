"""Hepler functions for cpac Python package."""
from itertools import chain
import re

TODOs = {
    "persisting_containers": "Some Docker containers unexpectedly "
    "persist after cpac finishes. To clear "
    "them, run\n    "
    r"1. `docker ps` to list the containers"
    "\n  For each C-PAC conatainer that "
    "persists, run\n    "
    r"2. `docker attach <container_name>`"
    "\n    "
    r"3. `exit`"
}


def get_extra_arg_value(extra_args, argument):
    """Parse passed-through arguments and get their values.

    Parameters
    ----------
    extra_args : list

    argument : str

    Returns
    -------
    value : str

    Examples
    --------
    >>> get_extra_arg_value([
    ...     '--preconfig=fmriprep-options',
    ...     '--data_config_file=/configs/data_config_regtest.yml',
    ...     '--participant_ndx=3'], 'preconfig')
    'fmriprep-options'
    >>> get_extra_arg_value([
    ...     '--preconfig=fmriprep-options',
    ...     '--data_config_file=/configs/data_config_regtest.yml',
    ...     '--participant_ndx 3'], 'participant_ndx')
    '3'
    """
    extra_args = list(
        chain.from_iterable([re.split(r"[=\s]", arg) for arg in extra_args])
    )

    for index, item in enumerate(extra_args):
        if item.startswith("-") and item.lstrip("-") == argument:
            return extra_args[index + 1]
    return None


__all__ = ["get_extra_arg_value", "TODOs"]
