#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pytest
from cpac.backends import docker
from cpac.scheduler import Scheduler

def test_remap():
    newdict, mapping = docker.DockerSchedule._remap_files({
        'anat': '/fcp-indi/data/Projects/ADHD200/RawDataBIDS/KKI/sub-2014113/ses-1/anat/sub-2014113_ses-1_run-1_T1w.nii.gz',
        'func': {
            'rest_acq-2_run-1': {
                'scan': '/fcp-indi/data/Projects/ADHD200/RawDataBIDS/KKI/sub-2014113/ses-1/func/sub-2014113_ses-1_task-rest_acq-2_run-1_bold.nii.gz',
                'scan_parameters': '/fcp-indi/data/Projects/ADHD200/RawDataBIDS/KKI/task-rest_acq-2_bold.json',
            }
        },
        'site': 'KKI',
        'subject_id': '2014113',
        'unique_id': '1',
    })

    assert newdict['subject_id'] == '2014113'

    # TODO add asserts for paths