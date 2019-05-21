import tornado.web
import tornado.ioloop
from tornado.options import define, options

import yaml


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, " + self.application.settings.get('backend'))


class ScheduleHandler(tornado.web.RequestHandler):
    def post(self):
        if not self.request.files.get('data_config'):
            self.clear()
            self.set_status(400)
            return self.finish()

        data_config = yaml.load(self.request.files['data_config'][0]['body'])
        self.finish(len(data_config))


def start(address, port):
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/schedule", ScheduleHandler),
    ], backend='docker')
    app.listen(address=address, port=port)
    tornado.ioloop.IOLoop.current().start()
