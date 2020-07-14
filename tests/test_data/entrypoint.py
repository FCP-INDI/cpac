#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import shutil
import socketserver
import sys
import threading

import yaml

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
        shutil.copy(
            '/code/data_config_template.yml',
            os.path.join(args.output_dir, 'cpac_data_config_test.yml')
        )
        sys.exit(0)

elif args.analysis_level == "test_config":
    shutil.copy(
        '/code/data_config_template.yml',
        os.path.join(args.output_dir, 'cpac_data_config_test.yml')
    )
    sys.exit(0)

elif args.analysis_level == "participant":
    data_config = yaml.safe_load(args.data_config_file)


    class LoggingRequestHandler(socketserver.BaseRequestHandler):

        def handle(self):

            tree = {}

            # self.server.pipeline_name
            for sub_config in self.server.data_config:
                tree[sub_config['subject_id']] = {
                    "node-00001": {
                        "hash": "00000000000000000000000000000000",
                        "start": "2020-01-01T10:00:00",
                        "finish": "2020-01-01T10:10:00",
                    }
                }

            headers = '''
HTTP/1.1 200 OK
Connection: close

'''
            self.request.sendall(headers + json.dumps(tree) + "\n")


    class LoggingHTTPServer(socketserver.ThreadingTCPServer):
        def __init__(self, pipeline_name, data_config='', host='', port=8080, request=LoggingRequestHandler):
            super(LoggingHTTPServer, self).__init__((host, port), request)
            self.pipeline_name = pipeline_name
            self.data_config = data_config

    def monitor_server(pipeline_name, data_config, host='0.0.0.0', port=8080):
        httpd = LoggingHTTPServer(pipeline_name, data_config, host, port, LoggingRequestHandler)
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.isDaemon = True
        server_thread.start()
        return server_thread

    sys.exit(0)
