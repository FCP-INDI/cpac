import pytest
import os
import json

from unittest import mock
from conftest import Constants
from cpac.utils import read_crash
from cpac.api.backends.base import CrashFileResult


def test_crash():
    crash_file = os.path.join(Constants.TESTS_DATA_PATH, 'cpac_output/crash/crash-file.pklz')

    crash_data = read_crash(crash_file)
    assert 'traceback' in crash_data
    assert 'node' in crash_data

    node = crash_data['node']
    assert node['name'] == 'resting_preproc_sub-0051074_ses-1.anat_mni_ants_register_0.calc_ants_warp'
    assert node['directory'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_mni_ants_register_0/calc_ants_warp'
    assert 'inputs' in node and type(node['inputs']) == dict

    inputs = node['inputs']
    assert inputs['anatomical_brain'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_preproc_afni_0/anat_skullstrip_orig_vol/sub-0051074_T1w_resample_calc.nii.gz'


@pytest.mark.asyncio
async def test_crash_result():
    crash_file = os.path.join(Constants.TESTS_DATA_PATH, 'cpac_output/crash/crash-file.pklz')

    res = CrashFileResult(crash_file)
    async with res as f:
        content = f.read()

    crash_data = json.loads(content)
    assert 'traceback' in crash_data
    assert 'node' in crash_data

    node = crash_data['node']
    assert node['name'] == 'resting_preproc_sub-0051074_ses-1.anat_mni_ants_register_0.calc_ants_warp'
    assert node['directory'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_mni_ants_register_0/calc_ants_warp'
    assert 'inputs' in node and type(node['inputs']) == dict

    inputs = node['inputs']
    assert inputs['anatomical_brain'] == '/tmp/resting_preproc_sub-0051074_ses-1/anat_preproc_afni_0/anat_skullstrip_orig_vol/sub-0051074_T1w_resample_calc.nii.gz'
