class Error(Exception):
    """
    Base class for exceptions in the digital_highway package.
    """
    def __init__(self, message: str = None, **kwargs):
        """
        Initialize the Error.

        Args:
            message (str): Basic error message.
            **kwargs: Additional keyword arguments to provide extra detail about the error.
        """
        if message is None:
            message = "An error occurred"
        self.message = message
        if kwargs:
            additional_info = ", ".join(f"{key}: {value}" for key, value in kwargs.items())
            self.message += f". Additional Information: {additional_info}"
        super().__init__(self.message)


class ConnectionError(Error):
    """
    Raised when a connection cannot be established.
    """
    pass

class PortError(Exception):
    pass

class AuthenticationError(Error):
    """
    Raised when an authentication attempt fails.
    """
    pass


class HandlerError(Error):
    """
    Raised when there is a problem with the event handler.
    """
    pass

class RetryExceededError(Error):
    """
    Raised when the maximum number of retries has been exceeded.
    """
    pass


# Example usage:
if __name__ == '__main__':
    try:
        raise ConnectionError("Connection error occurred", server="localhost", port="8080", protocol="https")
    except ConnectionError as e:
        print(e)
