#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from theodore.backends import docker

def test_docker():
    client = docker.Docker().client
    try:
        print(client.ping())
    except Exception as e:
        print(type(e))
