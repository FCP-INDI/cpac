import tornado.escape
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.autoreload
from tornado.options import define, options
from tornado.concurrent import run_on_executor

from cpac import __version__
from .schedules import Schedule, DataSettingsSchedule, DataConfigSchedule

import os
import time
import json
import yaml
import tempfile
import logging
import collections
import dataclasses


_logger = logging.getLogger(__name__)

class BaseHandler(tornado.web.RequestHandler):

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
        super(BaseHandler, self).prepare()
        self.json = None
        if self.request.body:
            try:
                self.json = tornado.escape.json_decode(self.request.body)
            except ValueError:
                pass

    def get_argument(self, arg, default=None):
        if self.request.method in ['POST', 'PUT'] and self.json:
            return self.json.get(arg, default)
        else:
            return super(BaseHandler, self).get_argument(arg, default)


class MainHandler(BaseHandler):
    def get(self):
        self.finish({
            "api": "C-PAC",
            "version": __version__,
        })


class BackendsHandler(BaseHandler):
    def get(self):
        self.finish({
            "backends": self.application.settings.get('backends')
        })


class ScheduleHandler(BaseHandler):
    def post(self):

        if "type" not in self.json:
            return self.bad_request()

        scheduler = self.application.settings.get("scheduler")

        if self.json["type"] == "data_settings":

            if not self.json.get("data_settings"):
                return self.bad_request()

            data_settings_file = self.json["data_settings"]

            schedule = scheduler.schedule(
                DataSettingsSchedule(
                    data_settings=data_settings_file
                )
            )

            return self.finish({"schedule": repr(schedule)})

        elif self.json["type"] == "pipeline":

            if not self.json.get("data_config"):
                return self.bad_request()

            if self.json["data_config"].startswith('s3:'):
                data_config_file = self.json["data_config"]
            elif self.json["data_config"].startswith('data:'):
                data_config_file = self.json["data_config"]
            else:
                upload_folder = tempfile.mkdtemp()
                data_config_file = os.path.join(upload_folder, "data_config.yml")
                with open(data_config_file, "wb") as f:
                    f.write(self.json["data_config"].encode("utf-8"))

            pipeline_file = None
            if self.json.get("pipeline"):
                pipeline_file = os.path.join(upload_folder, "pipeline.yml")

            _logger.info(f"Scheduling for data config {data_config_file}")

            schedule = scheduler.schedule(
                DataConfigSchedule(
                    data_config=data_config_file,
                    pipeline=pipeline_file
                )
            )

            return self.finish({"schedule": repr(schedule)})

        return self.bad_request()


class StatusScheduleHandler(BaseHandler):
    async def get(self, schedule, result=None):
        scheduler = self.application.settings.get('scheduler')
        schedule_tree = scheduler[schedule]
        schedule = schedule_tree.schedule
        schedule_status = await schedule.status

        return self.finish({
            "status": schedule_status,
        })


class ResultScheduleHandler(BaseHandler):
    def get(self, schedule, result=None):
        scheduler = self.application.settings.get('scheduler')
        schedule_tree = scheduler[schedule]
        schedule = schedule_tree.schedule

        if not schedule.available_results:
            self.set_status(425, 'Result is not ready')
            return self.finish()

        schedule_results = schedule.results
        if result:
            schedule_result = schedule_results[result]

            # if schedule_result.mime:
            #     self.set_header("Content-Type", schedule_result.mime)
            # for chunk in schedule_results[result]():
            #     self.write(chunk)

            self.write(schedule_result)
            return self.finish()

        return self.finish({
            "result": schedule_results,
            "children": list(schedule_tree.children.keys()),
        })


class ScheduleEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Schedule):
            return repr(o)
        return super().default(o)


def schedule_watch_wrapper(scheduler, socket, message_id):

    def schedule_watch(schedule, message):
        content = {
            "type": "watch",
            "data": {
                "id": repr(schedule),
                "type": message.__class__.__name__,
                "message": message.__dict__ if message else None,
            }
        }

        if message_id:
            content['__gui_message_id'] = message_id

        socket.write_message(json.dumps(content, cls=ScheduleEncoder))

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
        if '__gui_message_id' in message:
            message_id = message['__gui_message_id']

        scheduler = self.application.settings.get('scheduler')

        if message["type"] == "watch":
            schedule = scheduler[message["schedule"]].schedule
            scheduler.watch(
                schedule,
                schedule_watch_wrapper(scheduler, self, message_id),
                children="children" in message and message["children"]
            )

    def on_close(self):
        _logger.debug("Websocket disconnected")

    def check_origin(self, origin):
        return True

app = tornado.web.Application(
    [
        (r"/", MainHandler),
        (r"/schedule/(?P<schedule>[^/]+)/status", StatusScheduleHandler),  # TODO uuid regex
        (r"/schedule/(?P<schedule>[^/]+)/result", ResultScheduleHandler),  # TODO uuid regex
        (r"/schedule/(?P<schedule>[^/]+)/result/(?P<result>)", ResultScheduleHandler),  # TODO uuid regex
        (r"/schedule/connect", WatchScheduleHandler),
        (r"/schedule", ScheduleHandler),
        (r"/backends", BackendsHandler),
    ],
)

def start(address, scheduler):
    app.settings['scheduler'] = scheduler
    address, port = address
    app.listen(address=address, port=port)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()
