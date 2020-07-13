#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

class Constants:
    TESTS_PATH = os.path.join(os.path.dirname(__file__))
    TESTS_DATA_PATH = os.path.join(TESTS_PATH, 'test_data')


sys.path.append(Constants.TESTS_DATA_PATH)
