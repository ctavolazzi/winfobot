# Description: Errors for the digital_highway package
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ConnectionError(Error):
    """Raised when a connection cannot be established."""

class AuthenticationError(Error):
    """Raised when an authentication attempt fails."""
