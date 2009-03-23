import unittest

from restish import app, http, resource, url
from restish.tests.util import wsgi_out


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

    def test_resource_returns_resource(self):
        """
        Check resources can return other resources.
        """
        class WrappedResource(resource.Resource):
            def __init__(self, segments=None):
                self.segments = segments
            def resource_child(self, request, segments):
                return self.__class__(segments), []
            def __call__(self, request):
                return http.ok([], repr(self.segments))
        class WrapperResource(object):
            def resource_child(self, request, segments):
                return WrappedResource()
            def __call__(self, request):
                return WrappedResource()
        A = app.RestishApp(WrapperResource())
        # Call the wrapper
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == "None"
        # Call a child of the wrapper
        R = wsgi_out(A, http.Request.blank('/foo/bar').environ)
        assert R['status'].startswith('200')
        assert R['body'] == "[u'foo', u'bar']"

    def test_accepting_resource_returns_resource(self):
        """
        Check resource with accept match that returns another resource.

        This test was added because of a bug in resource.Resource where it
        assumed the request handler would return a response object but only
        broke when some accept matching had occurred.
        """
        class WrappedResource(resource.Resource):
            def __call__(self, request):
                return http.ok([], "WrappedResource")
        class WrapperResource(resource.Resource):
            @resource.GET(accept='html')
            def html(self, request):
                return WrappedResource()
        A = app.RestishApp(WrapperResource())
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == "WrappedResource"

    def test_resource_returns_func(self):
        def func(request):
            return http.ok([], 'func')
        class WrapperResource(resource.Resource):
            @resource.GET()
            def GET(self, request):
                return func
        A = app.RestishApp(WrapperResource())
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'func'

    def test_client_error(self):
        class Resource(resource.Resource):
            def __call__(self, request):
                raise http.BadRequestError()
        A = app.RestishApp(Resource())
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('400')

    def test_server_error(self):
        class Resource(resource.Resource):
            def __call__(self, request):
                raise http.BadGatewayError()
        A = app.RestishApp(Resource())
        R = wsgi_out(A, http.Request.blank('/').environ)
        assert R['status'].startswith('502')

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
        assert wsgi_out(A, http.Request.blank(url.URL('/').child('foo+bar@example.com').path).environ)['body'] == 'foo+bar@example.com'

    def test_iterable_response_body(self):
        def resource(request):
            def gen():
                yield "Three ... "
                yield "two ... "
                yield "one ... "
                yield "BANG!"
            return http.ok([('Content-Type', 'text/plain')], gen())
        A = app.RestishApp(resource)
        assert wsgi_out(A, http.Request.blank('/').environ)['body'] == 'Three ... two ... one ... BANG!'


class CallableResource(object):
    def __call__(self, request):
        return http.ok([], 'CallableResource')


class TraversableResource(object):
    def resource_child(self, request, segments):
        return CallableResource(), []


def resource_func(request):
    return http.ok([], 'resource_func')


class TestResourceLike(unittest.TestCase):
    """
    Test non-Resource subclasses work as expected.
    """

    def test_callable(self):
        A = app.RestishApp(CallableResource())
        assert wsgi_out(A, http.Request.blank('/').environ)['body'] == 'CallableResource'

    def test_not_callable(self):
        A = app.RestishApp(TraversableResource())
        self.assertRaises(TypeError, wsgi_out, A, http.Request.blank('/').environ)
        
    def test_traversable(self):
        A = app.RestishApp(TraversableResource())
        assert wsgi_out(A, http.Request.blank('/foo').environ)['body'] == 'CallableResource'

    def test_not_traversable(self):
        A = app.RestishApp(CallableResource())
        wsgi_out(A, http.Request.blank('/foo').environ)['status'].startswith('404')

    def test_func_callable(self):
        A = app.RestishApp(resource_func)
        assert wsgi_out(A, http.Request.blank('/').environ)['body'] == 'resource_func'

    def test_func_not_traversable(self):
        A = app.RestishApp(resource_func)
        wsgi_out(A, http.Request.blank('/foo').environ)['status'].startswith('404')
        

if __name__ == '__main__':
    unittest.main()

