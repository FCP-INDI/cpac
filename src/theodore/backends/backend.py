
class Backend(object):

    def __init__(self):
        pass

    def start(self, pipeline_config, subject_config):
        raise NotImplementedError()


class Result(object):

    mime = None

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self):
        yield self.value

    @property
    def description(self):
        return {
            'type': 'object'
        }


class FileResult(Result):

    def __init__(self, name, value, mime):
        self.name = name
        self.value = value
        self.mime = mime

    def __call__(self):
        with open(self.value, 'rb') as f: 
            while True: 
                piece = f.read(1024) 
                if piece: 
                    yield piece 
                else: 
                    return

    @property
    def description(self):
        return {
            'type': 'file',
            'mime': self.mime
        }