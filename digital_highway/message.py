from datetime import datetime

class Message:
    def __init__(self, sender, content, destination):
        self.source = sender
        self.destination = destination
        self.content = content
        self.timestamp = datetime.now()
        self.type = self.__class__.__name__

    def to_dict(self):
        return {
            'source': self.source,
            'destination': self.destination,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'type': self.type,
        }
