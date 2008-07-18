import webob


class Request(object):

    def __init__(self, environ):
        self._request = webob.Request(environ)

    def __getattr__(self, name):
        return getattr(self._request, name)

    def path_segments(self):
        segments = self.path.split("/")[1:]
        if segments == [""]:
            segments = []
        return segments


class Response(object):

    def __init__(self, status, headers, content):
        self._response = webob.Response(content, status, headers)

    def __getattr__(self, name):
        return getattr(self._response, name)



def ok(headers, content):
    return Response("200 OK", headers, content)


def not_found(headers, content):
    return Response("404 Not Found", headers, content)

