import asyncio
import tornado.escape
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.autoreload
import tornado.httputil
import tornado.iostream
from tornado.options import define, options
from tornado.concurrent import run_on_executor

from cpac import __version__
from .schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule
from .backends.base import Result, FileResult, CrashFileResult, LogFileResult

import os
import time
import json
import yaml
import tempfile
import logging
import collections
import dataclasses

_logger = logging.getLogger(__name__)


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Result):
            types = {
                Result: "result",
                FileResult: "file",
                CrashFileResult: "crash",
                LogFileResult: "log",
            }
            return {
                "type": types[o.__class__],
                "mime": o.mime,
                "name": o.name if hasattr(o, 'name') else None,
            }
        if isinstance(o, Schedule):
            return repr(o)
        return super().default(o)


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
            "api": "cpacpy",
            "version": __version__,
            "backends": [
                {"id": "docker", "backend": "docker", "tags": ["docker"]},
                {"id": "singularity", "backend": "singularity", "tags": ["singularity"]},
                {"id": "slurm", "backend": "slurm", "tags": ["slurm", "ssh", "singularity"]},
            ]
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

            data_config = self.json.get("data_config")
            if not data_config:
                return self.bad_request()

            upload_folder = None

            if data_config.startswith('s3:'):
                data_config_file = data_config
            elif data_config.startswith('data:'):
                data_config_file = data_config
            else:
                upload_folder = upload_folder or tempfile.mkdtemp()
                data_config_file = os.path.join(upload_folder, "data_config.yml")
                with open(data_config_file, "wb") as f:
                    f.write(data_config.encode("utf-8"))

            pipeline = self.json.get("pipeline")
            pipeline_file = None
            if pipeline:
                if pipeline.startswith('s3:'):
                    pipeline_file = pipeline
                elif pipeline.startswith('data:'):
                    pipeline_file = pipeline
                else:
                    upload_folder = upload_folder or tempfile.mkdtemp()
                    pipeline_file = os.path.join(upload_folder, "pipeline.yml")
                    with open(pipeline_file, "wb") as f:
                        f.write(pipeline.encode("utf-8"))

            data_config_file_repr = \
                data_config_file.split(',', 2)[0] \
                if data_config_file.startswith('data:') \
                else data_config_file

            _logger.info(f"Scheduling for data config {data_config_file_repr}")

            schedule = scheduler.schedule(
                DataConfigSchedule(
                    data_config=data_config_file,
                    pipeline=pipeline_file,
                    schedule_participants=bool(self.json.get("data_config"))
                )
            )

            return self.finish({"schedule": repr(schedule)})

        elif self.json["type"] == "participant":

            subject = self.json.get("subject")
            if not subject:
                return self.bad_request()

            pipeline = self.json.get("pipeline")
            if pipeline:
                if not pipeline.startswith('data:') and not pipeline.startswith('s3:'):
                    return self.bad_request()

            _logger.info(f"Scheduling for participant {subject}")

            schedule = scheduler.schedule(
                ParticipantPipelineSchedule(
                    subject=subject,
                    pipeline=pipeline,
                )
            )

            return self.finish({"schedule": repr(schedule)})

        return self.bad_request()


class StatusHandler(BaseHandler):
    async def get(self, result=None):
        scheduler = self.application.settings.get('scheduler')
        schedule_status = await scheduler.statuses

        return self.finish({
            "status": schedule_status,
        })


class MetadataScheduleHandler(BaseHandler):
    async def get(self, schedule):
        scheduler = self.application.settings.get('scheduler')
        try:
            schedule_tree = scheduler[schedule]
        except KeyError:
            return self.send_error(404)

        schedule = schedule_tree.schedule

        return self.finish({
            "metadata": {
                "parameters": schedule.__json__(),
                "type": schedule.base.__name__,
                "id": repr(schedule),
            },
        })


class StatusScheduleHandler(BaseHandler):
    async def get(self, schedule):
        scheduler = self.application.settings.get('scheduler')
        try:
            schedule_tree = scheduler[schedule]
        except KeyError:
            return self.send_error(404)

        schedule = schedule_tree.schedule
        schedule_status = await schedule.status

        return self.finish({
            "status": schedule_status,
        })


class ResultScheduleHandler(BaseHandler):
    async def get(self, schedule, result=None):
        scheduler = self.application.settings.get('scheduler')

        try:
            schedule_tree = scheduler[schedule]
        except KeyError:
            return self.send_error(404)

        schedule = schedule_tree.schedule

        if not schedule.available_results:
            self.set_status(425, 'Result is not ready')
            return self.finish()

        schedule_results = schedule.results
        if result:
            schedule_result = schedule[result]

            if isinstance(schedule_result, FileResult):
                self.set_header("Content-Type", schedule_result.mime)
                self.set_header("Content-Disposition", f'attachment; filename="{schedule_result.name}"')
                self.set_header("Access-Control-Expose-Headers", "Content-Disposition")

                async with schedule_result as stream:

                    request_range = None
                    range_header = self.request.headers.get("Range")
                    if range_header:
                        request_range = tornado.httputil._parse_request_range(range_header)

                    size = schedule_result.size
                    if request_range:
                        start, end = request_range
                        if start is not None and start < 0:
                            start += size
                            if start < 0:
                                start = 0
                        if (
                            start is not None
                            and (start >= size or (end is not None and start >= end))
                        ) or end == 0:
                            self.set_status(416)  # Range Not Satisfiable
                            self.set_header("Content-Range", f"bytes */{size}")
                            return

                        if end is not None and end > size:
                            end = size

                        if size != (end or size) - (start or 0):
                            self.set_status(206)  # Partial Content
                            self.set_header(
                                "Content-Range",
                                f"bytes {start or 0}-{(end or size) - 1}/{size}"
                            )
                    else:
                        start = end = None

                    if start is not None and end is not None:
                        content_length = end - start
                    elif end is not None:
                        content_length = end
                    elif start is not None:
                        content_length = size - start
                    else:
                        content_length = size

                    self.set_header("Content-Length", content_length)

                    content = schedule_result.slice(start, end)
                    async for chunk in content:
                        try:
                            self.write(chunk)
                            await self.flush()
                        except tornado.iostream.StreamClosedError:
                            break

                    return

            self.set_header("Content-Type", "application/json; charset=UTF-8")
            return self.finish(json.dumps({
                "result": schedule_results
            }, cls=CustomEncoder))

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return self.finish(json.dumps({
            "result": schedule_results,
            "children": list(schedule_tree.children.keys()),
        }, cls=CustomEncoder))


def schedule_watch_wrapper(scheduler, socket, message_id):

    def schedule_watch(self, schedule, message):
        content = {
            "type": "watch",
            "data": {
                "id": repr(schedule),
                "type": message.__class__.__name__,
                "message": message.__dict__ if message else None,
            }
        }

        if message_id:
            content['__cpacpy_message_id'] = message_id

        try:
            socket.write_message(json.dumps(content, cls=CustomEncoder))
        except tornado.websocket.WebSocketClosedError:
            pass

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
        if '__cpacpy_message_id' in message:
            message_id = message['__cpacpy_message_id']

        scheduler = self.application.settings.get('scheduler')

        if message["type"] == "watch":
            watchers = None
            if "watchers" in message:
                watchers = [
                    kls
                    for kls in scheduler.events
                    if kls.__name__ in message["watchers"]
                ]

            schedule = scheduler[message["schedule"]].schedule
            scheduler.watch(
                schedule,
                schedule_watch_wrapper(scheduler, self, message_id),
                children="children" in message and message["children"],
                watcher_classes=watchers
            )

    def on_close(self):
        _logger.debug("Websocket disconnected")

    def check_origin(self, origin):
        return True

app = tornado.web.Application(
    [
        (r"/", MainHandler),
        (r"/schedule/status", StatusHandler),
        (r"/schedule/(?P<schedule>[^/]+)/metadata", MetadataScheduleHandler),  # TODO uuid regex
        (r"/schedule/(?P<schedule>[^/]+)/status", StatusScheduleHandler),  # TODO uuid regex
        (r"/schedule/(?P<schedule>[^/]+)/result", ResultScheduleHandler),  # TODO uuid regex
        (r"/schedule/(?P<schedule>[^/]+)/result/(?P<result>.+)", ResultScheduleHandler),  # TODO uuid regex
        (r"/schedule/connect", WatchScheduleHandler),
        (r"/schedule", ScheduleHandler),
    ],
)

async def start(address, scheduler):
    app.settings['scheduler'] = scheduler
    address, port = address
    server = app.listen(address=address, port=port)
    tornado.autoreload.start()

    print(f"Listening to {address}:{port}")

    while True:
        await scheduler
        await asyncio.sleep(5)
