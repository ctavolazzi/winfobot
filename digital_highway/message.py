from datetime import datetime

class Message:
    def __init__(self, sender, content, receiver):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = datetime.now()
        self.type = self.__class__.__name__

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'type': self.type,
        }
