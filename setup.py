#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version
from semver.version import Version
from setuptools import setup

_MIN_VERSION = '61.2'
_MIN_VERSION = Version(*_MIN_VERSION.split('.'))
assert Version(*version('setuptools').split('.')).compare(_MIN_VERSION), (
    f"Version of setuptools is too old ({_MIN_VERSION})!")

if __name__ == "__main__":
    setup()
