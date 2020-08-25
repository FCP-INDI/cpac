import os
import uuid
import pytest
import asyncio
import logging
from cpac.api.backends import SLURMBackend
from cpac.api.backends.base import RunStatus
from cpac.api.client import Client
from conftest import Constants


@pytest.mark.asyncio
async def test_backend():

    backend = SLURMBackend(host='localhost:22222', username='root', password='root')

    await backend.cancel_all()

    job_id = await backend.run_on_node(f'cpacpy_{str(uuid.uuid4())}', '')

    status = await backend.queue_info(job_id)
    while status[job_id]['STATE'] is not RunStatus.RUNNING:
        await asyncio.sleep(2)
        status = await backend.queue_info(job_id)

    server_addr = await backend.proxy(job_id)

    async with Client(server_addr) as client:
        assert client.info['api'] == 'cpacpy'