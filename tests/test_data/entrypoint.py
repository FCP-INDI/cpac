#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
import threading
import time

import yaml

import websockets
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('websockets')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

__version__ = '0.0.0'
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
parser.add_argument('--pipeline_override', action='append')
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
parser.add_argument('--monitoring', default=None, type=int)

print(sys.argv)

args = parser.parse_args(
    sys.argv[
        1:(
            sys.argv.index('--')
            if '--' in sys.argv
            else len(sys.argv)
        )
    ]
)

try:
    more_options = sys.argv[sys.argv.index('--') + 1:]
except:
    more_options = []


print(args, more_options)

time.sleep(3)

if args.analysis_level == "cli":
    more_options = sys.argv[sys.argv.index('--') + 1:]
    if more_options[0:3] == ['utils', 'data_config', 'build']:
        
        with open(more_options[3]) as f:
            data_settings = yaml.safe_load(f)
            data_config_file = '/code/data_config_template.yml'

            if str(data_settings.get('bidsBaseDir')).startswith('s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS'):
                data_config_file = '/code/data_config_template_large.yml'

            shutil.copy(
                data_config_file,
                os.path.join(args.output_dir, 'cpac_data_config_test.yml')
            )
            sys.exit(0)

elif args.analysis_level == "test_config":

    data_config_file = args.data_config_file
    if args.bids_dir.startswith('s3://'):
        data_config_file = '/code/data_config_template.yml'
    if data_config_file.startswith('s3://'):
        data_config_file = '/code/data_config_template.yml'

    shutil.copy(
        data_config_file,
        os.path.join(args.output_dir, 'cpac_data_config_test.yml')
    )
    sys.exit(0)

elif args.analysis_level == "participant":
    with open(args.data_config_file) as f:
        data_config = yaml.safe_load(f)[0]

    # def copytree(src, dst, symlinks=False, ignore=None):
    #     for item in os.listdir(src):
    #         s = os.path.join(src, item)
    #         d = os.path.join(dst, item)
    #         if os.path.isdir(s):
    #             shutil.copytree(s, d, symlinks, ignore)
    #         else:
    #             shutil.copy2(s, d)

    # copytree('/code/cpac_output', args.output_dir)

    nodes = [
        f"resting_preproc_sub-{data_config['subject_id']}.1_anat_pipeline.1_normalize",
        f"resting_preproc_sub-{data_config['subject_id']}.1_anat_pipeline.2_skullstrip",
        f"resting_preproc_sub-{data_config['subject_id']}.1_anat_pipeline.3_segmentation",
        f"resting_preproc_sub-{data_config['subject_id']}.2_func_pipeline.4_skullstrip",
        f"resting_preproc_sub-{data_config['subject_id']}.2_func_pipeline.5_registration",
        f"resting_preproc_sub-{data_config['subject_id']}.2_func_pipeline.6_nuisance_regression",
    ]

    sleep_between_nodes = 1.0

    async def socketee(websocket, path):
        if path != '/log':
            return

        start = time.time()

        for i, node in enumerate(nodes):
            start = time.time()
            await asyncio.sleep(sleep_between_nodes)

            await websocket.send(json.dumps({
                "time": time.time(),
                "message": {
                    "id": node,
                    "hash": f"{i:032}",
                    "start": start,
                    "end": time.time(),
                }
            }))

            logger.info(f"{node}")

        # Keep socket open
        while True:
            await asyncio.sleep(1)

    async def serve():
        server = None
        try:
            server = await websockets.serve(socketee, "0.0.0.0", args.monitoring)
            await server.wait_closed()
        finally:
            if server:
                server.close()

    async def wait_some():
        await asyncio.sleep(3)
        await asyncio.sleep(len(nodes) * sleep_between_nodes)
        await asyncio.sleep(1)

    async def main():
        task = asyncio.create_task(serve())
        wait = asyncio.create_task(wait_some())
        await asyncio.wait([task, wait], return_when=asyncio.FIRST_COMPLETED)

    asyncio.run(main(), debug=True)

    if data_config['subject_id'] in ('0050959', '0051558'):
        sys.exit(1)

    sys.exit(0)
