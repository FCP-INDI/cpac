import asyncio
import json
import logging
import os
import re

import pytest
from tornado.escape import json_decode

from conftest import Constants
from cpac import __version__
from cpac.utils import generate_data_url
from cpac.api.backends.base import RunStatus

from fixtures import event_loop, scheduler, app, app_client

@pytest.mark.asyncio
async def test_version(http_client, base_url, app):
    response = await http_client.fetch(base_url, raise_error=False)
    assert response.code == 200

    content = json_decode(response.body)
    assert content['api'] == 'cpacpy'
    assert content['version'] == __version__
    assert len(content['backends']) == 3  # @TODO create a custom config for the scheduler on test env


@pytest.mark.asyncio
async def test_data_settings(http_client, base_url, app, scheduler):

    with open(os.path.join(Constants.TESTS_DATA_PATH, 'data_settings_template.yml'), 'r') as f:
        data_settings = f.read()

    # Schedule a data_settings => data_config conversion
    body = json.dumps({
        'type': 'data_settings', 
        'data_settings': generate_data_url(data_settings, 'text/yaml'),
    })
    response = await http_client.fetch(f'{base_url}/schedule', method='POST', headers=None, body=body, raise_error=False)
    assert response.code == 200

    body = json_decode(response.body)
    assert 'schedule' in body
    schedule = body['schedule']

    # Check before there are results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    assert response.code == 425

    await scheduler

    response = await http_client.fetch(f'{base_url}/schedule/status', raise_error=False)
    assert response.code == 200
    body = json_decode(response.body)

    # Check when it get results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    assert response.code == 200
    body = json_decode(response.body)

    assert 'result' in body
    result = body['result']

    assert 'data_config' in result
    data_config = result['data_config']

    assert len(data_config) == 4


@pytest.mark.asyncio
async def test_data_config(http_client, base_url, app, scheduler):

    with open(os.path.join(Constants.TESTS_DATA_PATH, 'data_config_template_single.yml'), 'r') as f:
        data_config = f.read()

    body = json.dumps({
        'type': 'pipeline', 
        'data_config': generate_data_url(data_config, 'text/yaml'),
    })
    response = await http_client.fetch(
        f'{base_url}/schedule',
        method='POST',
        headers=None,
        body=body,
        raise_error=False
    )
    assert response.code == 200

    body = json_decode(response.body)
    assert 'schedule' in body
    schedule = body['schedule']

    # Check before there are results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    assert response.code == 425

    await asyncio.sleep(3)

    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/status', raise_error=False)
    body = json_decode(response.body)
    assert body['status'] == RunStatus.RUNNING

    await scheduler

    # Check when it get results
    response = await http_client.fetch(f'{base_url}/schedule/{schedule}/result', raise_error=False)
    body = json_decode(response.body)

    assert 'result' in body
    result = body['result']

    assert 'data_config' in result
    data_config = result['data_config']

    assert len(data_config) == 1

    # Look for the spawned child
    assert 'children' in body
    children = body['children']

    assert len(children) == 1

    child = children[0]
    response = await http_client.fetch(f'{base_url}/schedule/{child}/result', raise_error=False)

    body = json_decode(response.body)

    log = list(body['result']['logs'].keys())[0]
    response = await http_client.fetch(f'{base_url}/schedule/{child}/result/logs/{log}', raise_error=False)
    filename = re.findall('filename="([^"]+)"', response.headers.get('content-disposition'))[0]

    assert filename == '/log/pipeline_analysis/sub-0050952_ses-1/pypeline.log'

    logs = response.body
    assert b'nipype.workflow INFO' in logs.split(b'\n')[0]

    crash = list(body['result']['crashes'].keys())[0]
    response = await http_client.fetch(f'{base_url}/schedule/{child}/result/crashes/{crash}', raise_error=False)
    filename = re.findall('filename="([^"]+)"', response.headers.get('content-disposition'))[0]

    assert filename == '/crash/crash-sub-0050952.pklz'

    crash_data = json_decode(response.body)
    assert crash_data['traceback'].startswith('Traceback')

    node = crash_data['node']
    assert node['name'] == 'resting_preproc_sub-0051074_ses-1.anat_mni_ants_register_0.calc_ants_warp'
    assert node['directory'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_mni_ants_register_0/calc_ants_warp'
    assert 'inputs' in node and type(node['inputs']) == dict

    inputs = node['inputs']
    assert inputs['anatomical_brain'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_preproc_afni_0/anat_skullstrip_orig_vol/sub-0051074_T1w_resample_calc.nii.gz'
