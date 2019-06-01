import tornado.escape
import tornado.web
import tornado.ioloop
from tornado.options import define, options

import yaml


class JSONBaseHandler(tornado.web.RequestHandler):

    def prepare(self):
        super(JSONBaseHandler, self).prepare()
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
            return super(JSONBaseHandler, self).get_argument(arg, default)


class MainHandler(JSONBaseHandler):
    def get(self):
        self.finish("hello_cpaki")


class BackendsHandler(JSONBaseHandler):
    def get(self):
        self.finish({"backends": self.application.settings.get('backends')})


class ScheduleHandler(JSONBaseHandler):
    def get(self):
        self.finish("""
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="data_config" />
            <input type="submit" />
        </form>

""")
    def post(self):
        if not self.request.files.get('data_config'):
            self.clear()
            self.set_status(400)
            return self.finish()

        data_config = yaml.load(self.request.files['data_config'][0]['body'])
        self.finish({'subjects': len(data_config)})


def start(address, port, backends):
    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/schedule", ScheduleHandler),
        (r"/backends", BackendsHandler),
    ], backends=backends)
    app.listen(address=address, port=port)
    tornado.ioloop.IOLoop.current().start()
