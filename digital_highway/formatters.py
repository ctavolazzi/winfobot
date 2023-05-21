import json

class BaseFormatter:
    def __init__(self, sender):
        self.sender = sender

    def format(self, data):
        raise NotImplementedError


class JSONFormatter(BaseFormatter):
    def format(self, data):
        formatted_data = {
            'sender': self.sender,
            'data': data,
        }
        return json.dumps(formatted_data)