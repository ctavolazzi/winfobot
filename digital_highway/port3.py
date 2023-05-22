class Port:
    ...
    def __init__(self, owner, config=None):
        ...
        self._owner = owner  # Set the owner of the port
        ...

    def connect(self, target):
        ...
        # Send a connection request with a hashed token
        token = secrets.token_hex(16)
        hashed_token = bcrypt.hashpw(token.encode(), bcrypt.gensalt())
        request = ConnectionRequest(self, hashed_token)
        if target.handle_connection_request(request):
            self._connections.add((target, hashed_token))
            ...
        ...

    def handle_connection_request(self, request):
        # Check if the request is valid and if so, add the source port and the hashed token to the connections
        if isinstance(request, ConnectionRequest):
            self._connections.add((request.source_port, request.token))
            return True
        return False

    def send(self, content, destinations):
        for destination, token in self._connections:
            ...
            # Hash the message with the token and send it
            hashed_content = self._hash_message(content, token)
            message = Message(source=self, content=hashed_content, destination=destination)
            destination.receive(message)
            ...

    def receive(self, message):
        # Check if the message is valid (i.e., if it's from a connected port and if the content can be correctly hashed with the token)
        source, content = message.source, message.content
        for port, token in self._connections:
            if port is source and content == self._hash_message(content, token):
                ...
                break
        else:
            return
        ...

    def _hash_message(self, message, token):
        return bcrypt.hashpw(message.encode(), token)

    def broadcast(self, content):
        for destination, token in self._connections:
            ...
            # Hash the message with the token and send it
            hashed_content = self._hash_message(content, token)
            message = Message(source=self, content=hashed_content, destination=destination)
            destination.receive(message)
            ...
