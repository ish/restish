import webob

from restish import error, url


class Request(object):

    def __init__(self, environ):
        self._request = webob.Request(environ)

    def __getattr__(self, name):
        return getattr(self._request, name)

    @property
    def host_url(self):
        return url.URL(self._request.host_url)

    @property
    def application_url(self):
        return url.URL(self._request.application_url)

    @property
    def path_url(self):
        return url.URL(self._request.path_url)

    @property
    def url(self):
        return url.URL(self._request.url)


class Response(object):

    def __init__(self, status, headers, body):
        self._response = webob.Response(body, status, headers)

    def __getattr__(self, name):
        return getattr(self._response, name)


# Successful 2xx

def ok(headers, body):
    return Response("200 OK", headers, body)

def created(location, body, headers=None):
    if headers is None:
        headers = []
    else:
        headers = list(headers)
    headers.append(('Location', location))
    return Response("201 Created", headers, body)


# Redirection 3xx

def moved_permanently(location):
    return Response("301 Moved Permanently", [('Location', location)], "")

def found(location):
    return Response("302 Found", [('Location', location)], "")

def see_other(location):
    return Response("303 See Other", [('Location', location)], "")

def not_modified():
    return Response("304 Not Modified", [], "")


# Client Error 4xx

def bad_request(headers=None, body=None):
    if headers is None:
        headers = [('Content-Type', 'text/plain')]
    if body is None:
        body = '400 Bad Request'
    return Response("400 Bad Request", headers, body)

class BadRequestError(error.HTTPClientError):
    response_factory = staticmethod(bad_request)

def unauthorized():
    return Response("401 Unauthorized", [('Content-Type', 'text/plain')], "401 Unauthorized")

class UnauthorizedError(error.HTTPClientError):
    response_factory = staticmethod(unauthorized)

def forbidden(headers, body):
    return Response("403 Forbidden", headers, body)

class ForbiddenError(error.HTTPClientError):
    response_factory = staticmethod(forbidden)

def not_found(headers, body):
    return Response("404 Not Found", headers, body)

class NotFoundError(error.HTTPClientError):
    response_factory = staticmethod(not_found)

def method_not_allowed(allow):
    return Response("405 Method Not Allowed", [('Content-Type', 'text/plain'), ('Allow', allow)], "405 Method Not Allowed")

class MethodNotAllowedError(error.HTTPClientError):
    response_factory = staticmethod(method_not_allowed)

def conflict(headers, body):
    return Response("409 Conflict", headers, body)

class ConflictError(error.HTTPClientError):
    response_factory = staticmethod(conflict)

