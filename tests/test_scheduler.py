#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import pytest
from theodore.backends import docker, DataSettingsSchedule
from theodore.backends.docker import DockerDataSettingsSchedule
from theodore.scheduler import Scheduler

def test_docker():
    scheduler = Scheduler({
        'docker': docker.Docker
    }, ['docker'])

    schedule = scheduler.schedule(
        DataSettingsSchedule(
            data_settings=os.path.join(os.path.dirname(__file__), 'data_settings_template.yml')
        )
    )

    print(schedule)

    while True:
        statuses = scheduler.statuses
        if statuses:
            print(statuses)
            if statuses['children'][str(schedule)]['status'] == 'success':
                break
        time.sleep(1)

    print(schedule.result())
