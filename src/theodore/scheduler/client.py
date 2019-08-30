import os
import json
import time
import logging

from theodore.scheduler import SCHEDULER_ADDRESS
from theodore.utils import Request, urlopen, bytes, HTTPError

from tornado import gen
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop

_logger = logging.getLogger(__name__)


def schedule(scheduler, backend, data_config_file, pipeline_file=None):

    print(scheduler)

    wait(scheduler)

    if os.path.isfile(data_config_file):
        with open(data_config_file, 'rb') as f:
            data_config_file = f.read()

    if pipeline_file and os.path.isfile(pipeline_file):
        with open(pipeline_file, 'rb') as f:
            pipeline_file = f.read()

    req = Request('http://%s:%d/schedule' % scheduler)
    req.add_header('Content-Type', 'application/json')
    res = urlopen(req, bytes(json.dumps({
        'type': 'PIPELINE',
        'data_config': data_config_file,
        'pipeline': pipeline_file,
    })))

    data = json.loads(res.read())

    if "schedule" in data:
        r = lambda: wait_schedule(scheduler, data["schedule"])
        result = IOLoop.current().run_sync(r)
        print(result)
        

@gen.coroutine
def wait_schedule(scheduler, schedule):
    ws = yield websocket_connect('ws://%s:%d/schedule/connect' % scheduler)
    ws.write_message(json.dumps({
        "type": "SCHEDULE_WATCH",
        "schedule": schedule,
    }))

    while True:
        msg = yield ws.read_message()
        if msg is None:
            break

        data = json.loads(msg)
        if "type" in data and data["type"] == "SCHEDULE_WATCH" and data["data"]["id"] == schedule:
            return data["data"]["statuses"]["status"]


def wait(scheduler):
    while True:
        try:
            _logger.info("Trying %s:%d" % scheduler)
            req = Request('http://%s:%d' % scheduler)
            res = urlopen(req, timeout=5)
            data = json.loads(res.read())
            if data["api"] == "theodore":
                break
        except:
            pass

        time.sleep(1)