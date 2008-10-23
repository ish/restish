import unittest
import webob

from restish import app, http, resource


class Resource(resource.Resource):

    def __init__(self, name, children={}):
        self.name = name
        self.children = children

    def resource_child(self, request, segments):
        try:
            return self.children[segments[0]], segments[1:]
        except KeyError:
            return None

    def __call__(self, request):
        return http.ok([('Content-Type', 'text/plain')], self.name)


def wsgi_out(app, environ):
    out = {}
    def start_response(status, headers):
        out['status'] = status
        out['headers'] = headers
    out['body'] = app(environ, start_response)
    return out


class TestApp(unittest.TestCase):

    def test_root(self):
        A = app.RestishApp(Resource('root'))
        R = wsgi_out(A, webob.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'root'

    def test_not_found(self):
        A = app.RestishApp(resource.Resource())
        R = wsgi_out(A, webob.Request.blank('/not_found').environ)
        assert R['status'].startswith('404')

    def test_children(self):
        A = app.RestishApp(Resource('root', {'foo': Resource('foo'), 'bar': Resource('bar')}))
        R = wsgi_out(A, webob.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'root'
        R = wsgi_out(A, webob.Request.blank('/foo').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'foo'
        R = wsgi_out(A, webob.Request.blank('/bar').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'bar'


if __name__ == '__main__':
    unittest.main()

