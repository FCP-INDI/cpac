import tornado.escape
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.autoreload
from tornado.options import define, options
from tornado.concurrent import run_on_executor

from theodore import __version__
from theodore.backends import DataSettingsSchedule, DataConfigSchedule

import os
import time
import json
import yaml
import tempfile
import logging
import collections


_logger = logging.getLogger(__name__)

class TheoBaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self, **kwargs):
        self.set_status(204)
        self.finish()

    def bad_request(self):
        self.set_status(400)
        return self.finish()

    def prepare(self):
        super(TheoBaseHandler, self).prepare()
        self.json_data = None
        if self.request.body:
            try:
                self.json_data = tornado.escape.json_decode(self.request.body)
            except ValueError:
                pass

    def get_argument(self, arg, default=None):
        if self.request.method in ['POST', 'PUT'] and self.json_data:
            return self.json_data.get(arg, default)
        else:
            return super(TheoBaseHandler, self).get_argument(arg, default)


class MainHandler(TheoBaseHandler):
    def get(self):
        self.finish({
            "api": "theodore",
            "version": __version__,
        })


class BackendsHandler(TheoBaseHandler):
    def get(self):
        self.finish({
            "backends": self.application.settings.get('backends')
        })


class ScheduleHandler(TheoBaseHandler):
    def post(self):

        if "type" not in self.json_data:
            return self.bad_request()

        scheduler = self.application.settings.get("scheduler")

        if self.json_data["type"] == "DATA_CONFIG":

            if not self.json_data.get("data_settings"):
                return self.bad_request()

            upload_folder = tempfile.mkdtemp()
            data_settings_file = os.path.join(upload_folder, "data_settings.yml")

            with open(data_settings_file, "wb") as f:
                f.write(self.json_data["data_settings"].encode("utf-8"))

            schedule = scheduler.schedule(
                DataSettingsSchedule(
                    data_settings=data_settings_file
                )
            )

            return self.finish({"schedule": str(schedule)})

        elif self.json_data["type"] == "PIPELINE":

            if not self.json_data.get("data_config"):
                return self.bad_request()

            if self.json_data["data_config"].startswith('s3://'):
                data_config_file = self.json_data["data_config"]
            else:
                upload_folder = tempfile.mkdtemp()
                data_config_file = os.path.join(upload_folder, "data_config.yml")
                with open(data_config_file, "wb") as f:
                    f.write(self.json_data["data_config"].encode("utf-8"))

            pipeline_file = None
            if self.json_data.get("pipeline"):
                pipeline_file = os.path.join(upload_folder, "pipeline.yml")

            schedule = scheduler.schedule(
                DataConfigSchedule(
                    data_config=data_config_file,
                    pipeline=pipeline_file
                )
            )

            return self.finish({"schedule": str(schedule)})

        return self.bad_request()


class ResultScheduleHandler(TheoBaseHandler):
    def get(self, schedule, result=None):
        scheduler = self.application.settings.get('scheduler')
        schedule = scheduler[schedule].schedule

        schedule_results = schedule.results
        if not schedule_results:
            self.set_status(425, 'Result is not ready')
            return self.finish()

        if result:
            schedule_result = schedule_results[result]

            if schedule_result.mime:
                self.set_header("Content-Type", schedule_result.mime)

            for chunk in schedule_results[result]():
                self.write(chunk)
            return self.finish()

        return self.finish({
            "result": {
                k: v.description
                for k, v in schedule_results.items()
            }
        })


def schedule_watch_wrapper(scheduler, socket, message_id):

    def schedule_watch(schedule):

        content = {
            "type": "SCHEDULE_WATCH",
            "data": {
                "id": str(schedule),
                "statuses": scheduler[schedule].status,
                "available_results": schedule.available_results,
            }
        }

        if message_id:
            content['__theo_message_id'] = message_id

        socket.write_message(json.dumps(content))

    return schedule_watch


class WatchScheduleHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        self.write_message(json.dumps({'connected': True}))
        _logger.debug("Websocket connected")

    def on_message(self, message):
        try:
            message = json.loads(message)
        except:
            return

        if type(message) is not dict:
            return

        if "type" not in message:
            return

        _logger.debug("Websocket message of type %s", message["type"])

        message_id = None
        if '__theo_message_id' in message:
            message_id = message['__theo_message_id']

        scheduler = self.application.settings.get('scheduler')

        if message["type"] == "SCHEDULE_WATCH":
            scheduler.watch(
                message["schedule"],
                schedule_watch_wrapper(scheduler, self, message_id),
                children="children" in message and message["children"]
            )

    def on_close(self):
        _logger.debug("Websocket disconnected")

    def check_origin(self, origin):
        return True


def start(address, scheduler):
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/schedule/(?P<schedule>[^/]+)/result", ResultScheduleHandler),  # TODO uuid regex
            (r"/schedule/(?P<schedule>[^/]+)/result/(?P<result>[^/]+)", ResultScheduleHandler),  # TODO uuid regex
            (r"/schedule/connect", WatchScheduleHandler),
            (r"/schedule", ScheduleHandler),
            (r"/backends", BackendsHandler),
        ],
        scheduler=scheduler
    )

    address, port = address
    app.listen(address=address, port=port)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()
