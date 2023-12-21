#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test bare-wrapped commands."""
from subprocess import call

from pytest import mark, skip

from cpac.utils.bare_wrap import _SCRIPTS, get_wrapped


def _join_captured(captured):
    """Join captured stdout and stderr."""
    return "\n".join([captured.out, captured.err])


@mark.parametrize("command", _SCRIPTS.keys())
def test_call(capfd, command):
    """Check that call is performed in bare-wrapped package."""
    wrapped = get_wrapped(command)
    if not wrapped.supported_python:
        skip("Python version not supported by wrapped package.")
    call(["cpac", wrapped.name])
    output = _join_captured(capfd.readouterr())
    if wrapped.positional_arguments:
        assert wrapped.command in output
        assert "error" in output.lower() and "arguments" in output.lower()


@mark.parametrize("command", _SCRIPTS.keys())
def test_usage_string(capfd, command):
    """Check that usage string is passed through from wrapped package."""
    wrapped = get_wrapped(command)
    call(["cpac", wrapped.name, "--help"])
    cpac_output = _join_captured(capfd.readouterr())
    if wrapped.supported_python:
        call([wrapped.command, "--help"])
        bare_output = _join_captured(capfd.readouterr())
        assert (
            bare_output.replace(f" {wrapped.command}", f" cpac {wrapped.name}")
            == cpac_output
        )
    else:
        assert "not supported" in cpac_output
