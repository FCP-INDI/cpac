#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''conftest.py for cpac.

Read more about conftest.py under:
https://pytest.org/latest/plugins.html
'''


# import pytest
def pytest_addoption(parser):
    parser.addoption('--platform', action='store', nargs=1, default=[])
    parser.addoption('--tag', action='store', nargs=1, default=[])


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test 'fixturenames'.
    platform = metafunc.config.option.platform
    tag = metafunc.config.option.tag
    if 'platform' in metafunc.fixturenames:
        metafunc.parametrize('platform', platform)
    if 'tag' in metafunc.fixturenames:
        metafunc.parametrize('tag', tag)
