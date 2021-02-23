import json
  

class DummyResponse(object):
    def __init__(self, raw, status_code=200):
        self.raw = self.text = self.content = raw
        self.status_code = status_code

    def json(self):
        return json.loads(self.raw)


class DummySession(object):

    def __init__(self, raw_data, status_code='200'):
        self.history = []
        self.response = DummyResponse(raw_data, status_code)

    def post(self, target, *a, **kw):
        self.history.append((target, a, kw))
        return self.response
