#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pytest
from theodore.backends import docker
from theodore.scheduler import Scheduler

def test_docker():
    scheduler = Scheduler()
    client = docker.Docker(scheduler)

    client.schedule(None, 's3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU')

    while True:
        print(scheduler.statuses)
        time.sleep(1)
