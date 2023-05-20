from datetime import datetime

class Message:
    def __init__(self, sender, content, receiver):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = datetime.now()
