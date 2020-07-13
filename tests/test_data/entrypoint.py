#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import shutil
import sys

__version__ = '0.0.0'

def parse_yaml(value):
    try:
        config = yaml.safe_load(value)
        if type(config) != dict:
            raise Exception
        return config
    except:
        raise argparse.ArgumentTypeError("Invalid configuration: '%s'" % value)

DEFAULT_PIPELINE = "/cpac_resources/default_pipeline.yml"

parser = argparse.ArgumentParser(description='C-PAC Pipeline Runner')
parser.add_argument('bids_dir')
parser.add_argument('output_dir')
parser.add_argument('analysis_level',
                    choices=['participant', 'group', 'test_config', 'gui', 'cli'], type=str.lower)

parser.add_argument('--pipeline_file', default=DEFAULT_PIPELINE)
parser.add_argument('--group_file', default=None)
parser.add_argument('--data_config_file', default=None)
parser.add_argument('--preconfig', default=None)
parser.add_argument('--pipeline_override', type=parse_yaml, action='append')
parser.add_argument('--aws_input_creds', default=None)
parser.add_argument('--aws_output_creds', default=None)
parser.add_argument('--n_cpus', type=int, default=1)
parser.add_argument('--mem_mb', type=float)
parser.add_argument('--mem_gb', type=float)

parser.add_argument('--save_working_dir', nargs='?', default=False)
parser.add_argument('--disable_file_logging', action='store_true', default=False)
parser.add_argument('--participant_label',  nargs="+")
parser.add_argument('--participant_ndx', default=None, type=int)

parser.add_argument('-v', '--version', action='version', version='C-PAC BIDS-App version {}'.format(__version__))
parser.add_argument('--bids_validator_config')
parser.add_argument('--skip_bids_validator', action='store_true')

parser.add_argument('--anat_only', action='store_true')
parser.add_argument('--tracking_opt-out', default=False)
parser.add_argument('--monitoring', action='store_true')

args = parser.parse_args(
    sys.argv[
        1:(
            sys.argv.index('--')
            if '--' in sys.argv
            else len(sys.argv)
        )
    ]
)

if args.analysis_level == "cli":
    more_options = sys.argv[sys.argv.index('--') + 1:]

    if more_options[0:3] == ['utils', 'data_config', 'build']:
        shutil.copy('/code/data_config_template.yml', 'cpac_data_config_test.yml')
        sys.exit(0)
