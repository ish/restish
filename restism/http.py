class Request(object):

    def __init__(self, environ):
        self.environ = environ

    def path(self):
        return self.environ["PATH_INFO"].decode("utf-8")

    def path_segments(self):
        segments = self.path().split("/")[1:]
        if segments == [""]:
            segments = []
        return segments


class Response(object):

    def __init__(self, status, headers, content):
        self.status = status
        self.headers = list(headers)
        self.content = content


def ok(headers, content):
    return Response("200 OK", headers, content)


def not_found(headers, content):
    return Response("404 Not Found", headers, content)

