class RestishException(Exception):
    """
    Base class for all restish exceptions.
    """
    pass


class HTTPClientError(RestishException):
    """
    Base class for all HTTP client (4xx) errors.

    Each 4xx response is mirrored by an exception type that subclasses from
    HTTPClientException. The subclass should override response_factory setting
    it to a callable that will accept all the positional and keyword args and
    return an http.Response instance.

    Typically, response_factory factory can be set to one of the convenience
    functions in the http module.
    """

    response_factory = None

    def __init__(self, *args, **kwargs):
        RestishException.__init__(self)
        self.args = args
        self.kwargs = kwargs

    def make_response(self):
        """
        Create an HTTP response for this exception type.
        """
        return self.response_factory(*self.args, **self.kwargs)

