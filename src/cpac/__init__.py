# -*- coding: utf-8 -*-
"""Init file for cpac."""
try:
    from importlib.metadata import PackageNotFoundError, distribution
except ModuleNotFoundError:
    from importlib_metadata import PackageNotFoundError, distribution  # type: ignore

DIST_NAME = __name__
try:
    __version__ = distribution(DIST_NAME).version
except (AttributeError, NameError, PackageNotFoundError):
    __version__ = "unknown"
finally:
    del distribution, PackageNotFoundError
