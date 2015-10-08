class RublonConfigurationError(Exception):
    pass


class RublonException(Exception):

    """CURL library is not available."""
    CODE_CURL_NOT_AVAILABLE = 1

    """Invalid response."""
    CODE_INVALID_RESPONSE = 2

    """Response error."""
    CODE_RESPONSE_ERROR = 3

    """CURL error."""
    CODE_CURL_ERROR = 4

    """Connection error."""
    CODE_CONNECTION_ERROR = 5

    """Timestamp error."""
    CODE_TIMESTAMP_ERROR = 6

    """Invalid access token."""
    CODE_INVALID_ACCESS_TOKEN = 7

    def __init__(self, message='', code=0, prev=None):
        self.prev = None
        self.code = code
        self.message = message

        # For backward compatibility check if get_previous() method exists
        if hasattr(self, 'get_previous'):
            super(RublonException, self).__init__(message, code, prev)
        else:
            super(RublonException, self).__init__(message)
            self.code = code
            self.previous = prev

    def __getattr__(self, item):
        """Handler for non-existing attributes."""
        if item == 'get_previous':
            def func():
                return self.previous
            return func
        else:
            raise AttributeError(item)


class RublonCallbackException(RublonException):
    ERROR_MISSING_ACCESS_TOKEN = 1
    ERROR_REST_CREDENTIALS = 2
    ERROR_USER_NOT_AUTHORIZED = 5
    ERROR_DIFFERENT_USER = 6
    ERROR_API_ERROR = 7
