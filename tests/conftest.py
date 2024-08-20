#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""conftest.py for cpac.

Read more about conftest.py under:
https://pytest.org/latest/plugins.html
"""
import logging

import pytest  # pylint: disable=import-error

LOGGER = logging.getLogger()


@pytest.fixture(autouse=True)
def ensure_logging_framework_not_altered():
    before_handlers = list(LOGGER.handlers)
    yield
    LOGGER.handlers = before_handlers


def pytest_addoption(parser):
    """Add command line options for pytest."""

    def add_option(option):
        """Factory function to add option and fixture."""  # noqa: D401
        parser.addoption(f"--{option}", action="store", nargs=1, default=[None])

    for option in ["image", "platform", "tag"]:
        add_option(option)


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test 'fixturenames'.
    for option in ["image", "platform", "tag"]:
        fixture = getattr(metafunc.config.option, option)
        if option in metafunc.fixturenames:
            metafunc.parametrize(option, fixture)
