import asyncio
import json
import logging
import os

import pytest
from tornado.escape import json_decode

from conftest import Constants
from cpac.api.backends.base import CrashFileResult
from cpac.api.schedules import ParticipantPipelineSchedule
from fixtures import app, app_client, event_loop, scheduler


@pytest.mark.asyncio
async def test_result_crash(http_client, base_url, app, scheduler):

    crash_file = os.path.join(Constants.TESTS_DATA_PATH, 'cpac_output/crash/crash-file.pklz')
    res = CrashFileResult(crash_file)

    schedule = ParticipantPipelineSchedule(
        subject=os.path.join(Constants.TESTS_DATA_PATH, 'data_config_template_single.yml')
    )

    response = await http_client.fetch(f'{base_url}/schedule/{repr(schedule)}/result', raise_error=False)

    body = json_decode(response.body)

    crash = list(body['result']['crashes'].keys())[0]
    response = await http_client.fetch(f'{base_url}/schedule/{repr(schedule)}/result/crashes/{crash}', raise_error=False)
    crash_data = json_decode(response.body)
    assert crash_data['traceback'].startswith('Traceback')

    node = crash_data['node']
    assert node['name'] == 'resting_preproc_sub-0051074_ses-1.anat_mni_ants_register_0.calc_ants_warp'
    assert node['directory'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_mni_ants_register_0/calc_ants_warp'
    assert 'inputs' in node and type(node['inputs']) == dict

    inputs = node['inputs']
    assert inputs['anatomical_brain'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_preproc_afni_0/anat_skullstrip_orig_vol/sub-0051074_T1w_resample_calc.nii.gz'
