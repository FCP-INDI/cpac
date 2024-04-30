# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Modifications to ``spython`` run Apptainer instead of Singularity."""
from spython.main import get_client as get_spython_client


def get_client(quiet=False, debug=False):
    """Create the spython Client singleton and replace its ._init_command."""
    Client = get_spython_client(quiet, debug)
    Client._init_command = init_command
    return Client


def init_command(self, action, flags=None):
    """
    Return the initial Apptainer command with any added flags.

    Modified from `spython.main.base.command.init_command <https://github.com/singularityhub/singularity-cli/blob/2b22233/spython/main/base/command.py#L16-L36>`_. Calls ``apptainer`` instead of ``singularity``.

    Parameters
    ----------
    action: the main action to perform (e.g., build)
    flags: one or more additional apptainer options
    """
    flags = flags or []

    if not isinstance(action, list):
        action = [action]
    cmd = ["apptainer", *flags, *action]

    if self.quiet:
        cmd.insert(1, "--quiet")
    if self.debug:
        cmd.insert(1, "--debug")

    return cmd
