import webob


class Request(object):

    def __init__(self, environ):
        self._request = webob.Request(environ)

    def __getattr__(self, name):
        return getattr(self._request, name)

    def path_segments(self):
        path = self.url[len(self.application_url):].split('?')[0]
        segments = path.split("/")[1:]
        if segments == [""]:
            segments = []
        return segments


class Response(object):

    def __init__(self, status, headers, content, content_type='text/html', charset='utf-8'):
        self._response = webob.Response(content, status, headers, content_type=content_type, charset=charset)

    def __getattr__(self, name):
        return getattr(self._response, name)


# Successful 2xx

def ok(headers, content):
    return Response("200 OK", headers, content)

def created(location, content):
    return Response("201 Created", [('Location', location)], content)


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

def bad_request():
    return Response("400 Bad Request", [], "")

def forbidden(headers, content):
    return Response("403 Forbidden", headers, content)

def not_found(headers, content):
    return Response("404 Not Found", headers, content)

def method_not_allowed(allow):
    return Response("405 Method Not Allowed", [('Allow', allow)], "405 Method Not Allowed")

def conflict(headers, content):
    return Response("409 Conflict", headers, content)

