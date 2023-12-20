#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test bare-wrapped commands."""
from subprocess import call

from pytest import mark

from cpac.utils.bare_wrap import _SCRIPTS, get_wrapped


def _join_captured(captured):
    """Join captured stdout and stderr."""
    return "\n".join([captured.out, captured.err])


def _remove_whitespace(captured):
    """Remove whitespace from captured string."""
    return "".join(captured.split())


@mark.parametrize("command", _SCRIPTS.keys())
def test_usage_string(capfd, command):
    """Check that usage string is passed through from wrapped package."""
    wrapped = get_wrapped(command)
    call([wrapped.command, "--help"])
    bare_output = _join_captured(capfd.readouterr())
    call(["cpac", wrapped.name, "--help"])
    cpac_output = _join_captured(capfd.readouterr())
    assert (
        bare_output.replace(f" {wrapped.command}", f" cpac {wrapped.name}")
        == cpac_output
    )
