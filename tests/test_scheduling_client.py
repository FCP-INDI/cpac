import asyncio
import datetime
import json
import logging
import os
from itertools import groupby

import numpy as np
import pytest
import tornado

from conftest import Constants

from cpac.api.client import Client
from cpac.api.schedules import Schedule, DataConfigSchedule

from fixtures import event_loop, scheduler, app

@pytest.mark.asyncio
async def test_client_data_config_logs(app, http_client, base_url, scheduler):
    
    response = await http_client.fetch(base_url, raise_error=False)
    assert response.code == 200

    server = base_url.replace('http://', '').split(':')
    async with Client(server) as client:

        schedule = DataConfigSchedule(
            data_config='s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU/',
            schedule_participants=False,
        )

        schedule_id = await client.schedule(schedule)

        async for message in client.listen(schedule):
            print(message)
