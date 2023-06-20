# -*- coding: utf-8 -*-
try:
    from importlib.metadata import distribution, PackageNotFoundError
except ModuleNotFoundError:
    from importlib_metadata import distribution, PackageNotFoundError

DIST_NAME = __name__
try:
    __version__ = distribution(DIST_NAME).version
except (AttributeError, NameError, PackageNotFoundError):
    __version__ = 'unknown'
finally:
    del distribution, PackageNotFoundError
