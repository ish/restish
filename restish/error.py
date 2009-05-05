class RestishException(Exception):
    """
    Base class for all restish exceptions.
    """
    pass


class HTTPError(RestishException):
    """
    Base class for all HTTP (4xx and 5xx) errors.

    Each error response factory defined in restish.http is mirrored by an
    exception type derived from HTTPException.
    
    The derived exception class is expected to override response_factory (None
    by default), providing a callable that accepts all the positional and
    keyword args and returns an http.Response instance.  Typically,
    response_factory can be set to one of the HTTP response convenience
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


class HTTPClientError(HTTPError):
    """
    Base class for all HTTP client (4xx) errors.
    """

class HTTPServerError(HTTPError):
    """
    Base class for all HTTP server (5xx) errors.
    """

