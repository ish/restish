import unittest

from restish import app, http, resource, url
from restish.test.util import wsgi_out


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


class TestApp(unittest.TestCase):

    def test_root(self):
        A = app.RestishApp(Resource('root'))
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'root'

    def test_not_found(self):
        A = app.RestishApp(resource.Resource())
        R = wsgi_out(A, http.Request.blank('/not_found').environ)
        assert R['status'].startswith('404')

    def test_not_found_on_none(self):
        class Resource(resource.Resource):
            def resource_child(self, request, segments):
                return None
        A = app.RestishApp(Resource())
        R = wsgi_out(A, http.Request.blank('/not_found').environ)
        assert R['status'].startswith('404')

    def test_children(self):
        A = app.RestishApp(Resource('root', {'foo': Resource('foo'), 'bar': Resource('bar')}))
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'root'
        R = wsgi_out(A, http.Request.blank('/foo').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'foo'
        R = wsgi_out(A, http.Request.blank('/bar').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'bar'

    def test_resource_returns_resource_when_called(self):
        class WrapperResource(resource.Resource):
            def __call__(self, request):
                return Resource('root')
        A = app.RestishApp(WrapperResource())
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'root'

    def test_resource_returns_resource_when_finding_child(self):
        class WrappedResource(resource.Resource):
            def __init__(self, segments=None):
                self.segments = segments
            def resource_child(self, request, segments):
                return self.__class__(segments), []
            def __call__(self, request):
                return http.ok([], repr(self.segments))
        class WrapperResource(resource.Resource):
            def resource_child(self, request, segments):
                return WrappedResource()
        A = app.RestishApp(WrapperResource())
        R = wsgi_out(A, http.Request.blank('/foo/bar').environ)
        assert R['status'].startswith('200')
        assert R['body'] == "[u'foo', u'bar']"

    def test_client_error(self):
        class Resource(resource.Resource):
            def __call__(self, request):
                raise http.UnauthorizedError()
        A = app.RestishApp(Resource())
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('401')

    def test_no_root_application(self):
        class Resource(resource.Resource):
            def __init__(self, segment):
                self.segment = segment
            def resource_child(self, request, segments):
                return self.__class__(segments[0]), segments[1:]
            def __call__(self, request):
                return http.ok([('Content-Type', 'text/plain')], self.segment.encode('utf-8'))
        A = app.RestishApp(Resource(''))
        assert wsgi_out(A, http.Request.blank('/').environ)['body'] == ''
        assert wsgi_out(A, http.Request.blank('/', base_url='http://localhost/base').environ)['body'] == ''
        assert wsgi_out(A, http.Request.blank('/foo', base_url='http://localhost/base').environ)['body'] == 'foo'

    def test_weird_path_segments(self):
        class Resource(resource.Resource):
            def __init__(self, segment):
                self.segment = segment
            def resource_child(self, request, segments):
                return self.__class__(segments[0]), segments[1:]
            def __call__(self, request):
                return http.ok([('Content-Type', 'text/plain')], self.segment.encode('utf-8'))
        A = app.RestishApp(Resource(''))
        assert wsgi_out(A, http.Request.blank('/').environ)['body'] == ''
        assert wsgi_out(A, http.Request.blank('/foo').environ)['body'] == 'foo'
        print wsgi_out(A, http.Request.blank(url.URL('/').child('foo+bar@example.com').path).environ)['body']
        assert wsgi_out(A, http.Request.blank(url.URL('/').child('foo+bar@example.com').path).environ)['body'] == 'foo+bar@example.com'


if __name__ == '__main__':
    unittest.main()

