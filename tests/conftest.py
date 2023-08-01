#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''conftest.py for cpac.

Read more about conftest.py under:
https://pytest.org/latest/plugins.html
'''
import logging
import pytest  # pylint: disable=import-error
from .CONSTANTS import FIXTURENAMES

LOGGER = logging.getLogger()


@pytest.fixture(autouse=True)
def ensure_logging_framework_not_altered():
    before_handlers = list(LOGGER.handlers)
    yield
    LOGGER.handlers = before_handlers


def pytest_addoption(parser):
    '''Add command line options for pytest.'''
    def add_option(option):
        '''Factory function to add option and fixture'''
        parser.addoption(f'--{option}', action='store', nargs=1,
                         default=[None])
    for option in FIXTURENAMES:
        add_option(option)


def pytest_generate_tests(metafunc):
    '''This is called for every test. Only get/set command line arguments
    if the argument is specified in the list of test 'fixturenames'.'''
    for fixturename in FIXTURENAMES:
        if fixturename in metafunc.fixturenames:
            metafunc.parametrize(fixturename, getattr(metafunc.config.option,
                                                      fixturename))
