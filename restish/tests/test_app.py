import unittest
import webtest

from restish import app, http, resource, url


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
        R = webtest.TestApp(A).get('/', status=200)
        assert R.body == 'root'

    def test_not_found(self):
        A = app.RestishApp(resource.Resource())
        R = webtest.TestApp(A).get('/not_found', status=404)

    def test_not_found_on_none(self):
        class Resource(resource.Resource):
            def resource_child(self, request, segments):
                return None
        A = app.RestishApp(Resource())
        R = webtest.TestApp(A).get('/not_found', status=404)

    def test_children(self):
        A = app.RestishApp(Resource('root', {'foo': Resource('foo'), 'bar': Resource('bar')}))
        R = webtest.TestApp(A).get('/', status=200)
        assert R.body == 'root'
        R = webtest.TestApp(A).get('/foo', status=200)
        assert R.body == 'foo'
        R = webtest.TestApp(A).get('/bar', status=200)
        assert R.body == 'bar'

    def test_resource_returns_resource_when_called(self):
        class WrapperResource(resource.Resource):
            def __call__(self, request):
                return Resource('root')
        A = app.RestishApp(WrapperResource())
        R = webtest.TestApp(A).get('/', status=200)
        assert R.body == 'root'

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
                return http.ok([('Content-Type', 'text/plain')], repr(self.segments))
        class WrapperResource(object):
            def resource_child(self, request, segments):
                return WrappedResource()
            def __call__(self, request):
                return WrappedResource()
        A = app.RestishApp(WrapperResource())
        # Call the wrapper
        R = webtest.TestApp(A).get('/', status=200)
        assert R.body == "None"
        # Call a child of the wrapper
        R = webtest.TestApp(A).get('/foo/bar', status=200)
        assert R.body == "[u'foo', u'bar']"

    def test_accepting_resource_returns_resource(self):
        """
        Check resource with accept match that returns another resource.

        This test was added because of a bug in resource.Resource where it
        assumed the request handler would return a response object but only
        broke when some accept matching had occurred.
        """
        class WrappedResource(resource.Resource):
            def __call__(self, request):
                return http.ok([('Content-Type', 'text/html')], "WrappedResource")
        class WrapperResource(resource.Resource):
            @resource.GET(accept='html')
            def html(self, request):
                return WrappedResource()
        A = app.RestishApp(WrapperResource())
        R = webtest.TestApp(A).get('/', status=200)
        assert R.body == "WrappedResource"

    def test_resource_returns_func(self):
        def func(request):
            return http.ok([('Content-Type', 'text/plain')], 'func')
        class WrapperResource(resource.Resource):
            @resource.GET()
            def GET(self, request):
                return func
        A = app.RestishApp(WrapperResource())
        R = webtest.TestApp(A).get('/', status=200)
        assert R.body == 'func'

    def test_client_error(self):
        class Resource(resource.Resource):
            def __call__(self, request):
                raise http.BadRequestError()
        A = app.RestishApp(Resource())
        R = webtest.TestApp(A).get('/', status=400)

    def test_server_error(self):
        class Resource(resource.Resource):
            def __call__(self, request):
                raise http.BadGatewayError()
        A = app.RestishApp(Resource())
        R = webtest.TestApp(A).get('/', status=502)

    def test_no_root_application(self):
        class Resource(resource.Resource):
            def __init__(self, segment):
                self.segment = segment
            def resource_child(self, request, segments):
                return self.__class__(segments[0]), segments[1:]
            def __call__(self, request):
                return http.ok([('Content-Type', 'text/plain')], self.segment.encode('utf-8'))
        A = app.RestishApp(Resource(''))
        assert webtest.TestApp(A).get('/').body == ''
        assert webtest.TestApp(A).get('/', extra_environ={'SCRIPT_NAME': '/base'}).body == ''
        assert webtest.TestApp(A).get('/foo', extra_environ={'SCRIPT_NAME': '/base'}).body == 'foo'

    def test_weird_path_segments(self):
        class Resource(resource.Resource):
            def __init__(self, segment):
                self.segment = segment
            def resource_child(self, request, segments):
                return self.__class__(segments[0]), segments[1:]
            def __call__(self, request):
                return http.ok([('Content-Type', 'text/plain')], self.segment.encode('utf-8'))
        A = app.RestishApp(Resource(''))
        assert webtest.TestApp(A).get('/').body == ''
        assert webtest.TestApp(A).get('/foo').body == 'foo'
        assert webtest.TestApp(A).get(url.URL('/').child('foo+bar@example.com').path).body == 'foo+bar@example.com'

    def test_iterable_response_body(self):
        def resource(request):
            def gen():
                yield "Three ... "
                yield "two ... "
                yield "one ... "
                yield "BANG!"
            return http.ok([('Content-Type', 'text/plain')], gen())
        A = app.RestishApp(resource)
        assert webtest.TestApp(A).get('/').body == 'Three ... two ... one ... BANG!'


class CallableResource(object):
    def __call__(self, request):
        return http.ok([('Content-Type', 'text/plain')], 'CallableResource')


class TraversableResource(object):
    def resource_child(self, request, segments):
        return CallableResource(), []


def resource_func(request):
    return http.ok([('Content-Type', 'text/plain')], 'resource_func')


class TestResourceLike(unittest.TestCase):
    """
    Test non-Resource subclasses work as expected.
    """

    def test_callable(self):
        A = app.RestishApp(CallableResource())
        assert webtest.TestApp(A).get('/').body == 'CallableResource'

    def test_not_callable(self):
        A = app.RestishApp(TraversableResource())
        self.assertRaises(TypeError, webtest.TestApp(A).get, '/')
        
    def test_traversable(self):
        A = app.RestishApp(TraversableResource())
        assert webtest.TestApp(A).get('/foo').body == 'CallableResource'

    def test_not_traversable(self):
        A = app.RestishApp(CallableResource())
        webtest.TestApp(A).get('/foo', status=404)

    def test_func_callable(self):
        A = app.RestishApp(resource_func)
        assert webtest.TestApp(A).get('/').body == 'resource_func'

    def test_func_not_traversable(self):
        A = app.RestishApp(resource_func)
        webtest.TestApp(A).get('/foo', status=404)
        

if __name__ == '__main__':
    unittest.main()

