import tornado.escape
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.autoreload
from tornado.options import define, options
from tornado.concurrent import run_on_executor

from theodore import __version__

import time
import json
import yaml
import collections


class TheoBaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

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
        self.finish({"backends": self.application.settings.get('backends')})


class ExecutionScheduleHandler(TheoBaseHandler):
    def post(self):

        if not self.request.files.get('data_config'):
            self.clear()
            self.set_status(400)
            return self.finish()

        data_config = yaml.load(self.request.files['data_config'][0]['body'])
        self.finish({'subjects': len(data_config)})


class DataScheduleHandler(TheoBaseHandler):
    def post(self):

        if not self.request.files.get('data_config'):
            self.clear()
            self.set_status(400)
            return self.finish()

        data_config = yaml.load(self.request.files['data_config'][0]['body'])
        self.finish({'subjects': len(data_config)})


class WatchScheduleHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print("New client connected")
        self.write_message(json.dumps({'connected': True}))
        self.loop = tornado.ioloop.PeriodicCallback(
            self.check_periodically,
            1000,
            io_loop=tornado.ioloop.IOLoop.instance()
        )
        self.loop.start()

    def on_message(self, message):
        self.write_message(u"You said: " + message + " -> " + str(self.application.settings.get('scheduler')))

    def on_close(self):
        print("Client disconnected")

    def check_periodically(self):
        try:
            self.write_message(json.dumps({'time': time.time()}))
        except tornado.websocket.WebSocketClosedError:
            self.loop.stop()

    def check_origin(self, origin):
        print(origin)
        return True
    

def start(address, port, scheduler):
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/schedule/watch", WatchScheduleHandler),
            (r"/schedule/data", DataScheduleHandler),
            (r"/schedule/pipeline", ExecutionScheduleHandler),
            (r"/backends", BackendsHandler),
        ],
        scheduler=scheduler
    )

    app.listen(address=address, port=port)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()
