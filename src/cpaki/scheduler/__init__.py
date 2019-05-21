import tornado.web
import tornado.ioloop
from tornado.options import define, options

import yaml


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, " + "+".join(self.application.settings.get('backends')))


class ScheduleHandler(tornado.web.RequestHandler):
    def post(self):
        if not self.request.files.get('data_config'):
            self.clear()
            self.set_status(400)
            return self.finish()

        data_config = yaml.load(self.request.files['data_config'][0]['body'])
        self.finish(len(data_config))


def start(address, port, backends):
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/schedule", ScheduleHandler),
        # TODO (r"/backends", BackendsHandler),  get available backends on server
    ], backends=backends)
    app.listen(address=address, port=port)
    tornado.ioloop.IOLoop.current().start()
