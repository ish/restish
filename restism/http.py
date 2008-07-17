import webob


class Request(object):

    def __init__(self, app, environ):
        self.app = app
        self._request = webob.Request(environ)

    @property
    def path(self):
        return self._request.path

    @property
    def headers(self):
        return self._request.headers

    def path_segments(self):
        segments = self.path.split("/")[1:]
        if segments == [""]:
            segments = []
        return segments


class Response(object):

    def __init__(self, status, headers, content):
        self._response = webob.Response(content, status, headers)

    @property
    def status(self):
        return self._response.status

    @property
    def headers(self):
        return self._response.headerlist

    @property
    def content(self):
        return self._response.body


def ok(headers, content):
    return Response("200 OK", headers, content)


def not_found(headers, content):
    return Response("404 Not Found", headers, content)

