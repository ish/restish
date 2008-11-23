"""
Test resource behaviour.
"""

import unittest
import webob

from restish import app, http, resource
from restish.test.util import wsgi_out


class TestResource(unittest.TestCase):

    def test_no_method_handler(self):
        res = resource.Resource()
        environ = webob.Request.blank('/').environ
        response = res(http.Request(environ))
        assert response.status.startswith("405")

    def test_methods(self):
        class Resource(resource.Resource):
            @resource.GET()
            def GET(self, request):
                return http.ok([], 'GET')
            @resource.POST()
            def POST(self, request):
                return http.ok([], 'POST')
            @resource.PUT()
            def PUT(self, request):
                return http.ok([], 'PUT')
            @resource.DELETE()
            def DELETE(self, request):
                return http.ok([], 'DELETE')
        for method in ['GET', 'POST', 'PUT', 'DELETE']:
            print "*", method
            environ = webob.Request.blank('/',
                    environ={'REQUEST_METHOD': method},
                    headers={'Accept': 'text/html'}).environ
            response = Resource()(http.Request(environ))
            print response.status, response.body
            assert response.status == "200 OK"
            assert response.body == method

    def test_child_factory(self):
        class ChildResource(resource.Resource):
            def __init__(self, name):
                self.name = name
            @resource.GET()
            def text(self, request):
                return http.ok([('Content-Type', 'text/plain')], self.name)
        class Resource(resource.Resource):
            @resource.child()
            def foo(self, request):
                return ChildResource('foo')
            @resource.child('bar')
            def bar_child(self, request):
                return ChildResource('bar')
        A = app.RestishApp(Resource())
        R = wsgi_out(A, webob.Request.blank('/foo').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'foo'
        R = wsgi_out(A, webob.Request.blank('/bar').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'bar'


class TestContentNegotiation(unittest.TestCase):

    def test_no_match(self):
        class Resource(resource.Resource):
            @resource.GET(accept='text/json')
            def html(self, request):
                return http.ok([], '<p>Hello!</p>')
        res = Resource()
        environ = webob.Request.blank('/', headers={'Accept': 'text/plain'}).environ
        response = res(http.Request(environ))
        print response.status
        assert response.status.startswith("406")

    def test_implicit_content_type(self):
        """
        Test that the content type is added automatically.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='text/html')
            def html(self, request):
                return http.ok([], '<p>Hello!</p>')
        res = Resource()
        environ = webob.Request.blank('/').environ
        response = res(http.Request(environ))
        assert response.headers['Content-Type'] == 'text/html'

    def test_implicit_content_type_not_on_partial_mimetype(self):
        """
        Test that a match on mime type group, e.g. */*, text/*, etc does not
        automatically add the content type.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='text/*')
            def html(self, request):
                return http.ok([], '<p>Hello!</p>')
        res = Resource()
        environ = webob.Request.blank('/').environ
        response = res(http.Request(environ))
        print response.headers.get('Content-Type')
        assert response.headers.get('Content-Type') is None

    def test_explicit_content_type(self):
        """
        Test that the content type is not added automatically if the resource
        sets it.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='text/html')
            def html(self, request):
                return http.ok([('Content-Type', 'text/plain')], '<p>Hello!</p>')
        res = Resource()
        environ = webob.Request.blank('/').environ
        response = res(http.Request(environ))
        assert response.headers['Content-Type'] == 'text/plain'

    def test_no_accept(self):
        """
        Test generic GET matches request from client that does not send an
        Accept header.
        """
        class Resource(resource.Resource):
            @resource.GET()
            def html(self, request):
                return http.ok([('Content-Type', 'text/html')], "<html />")
        res = Resource()
        environ = webob.Request.blank('/').environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/html'

    def test_accept_match(self):
        """
        Test that an accept'ing request is matched even if there's a generic
        handler.
        """
        class Resource(resource.Resource):
            @resource.GET()
            def html(self, request):
                return http.ok([('Content-Type', 'text/html')], "<html />")
            @resource.GET(accept='application/json')
            def json(self, request):
                return http.ok([('Content-Type', 'application/json')], "{}")
        res = Resource()
        environ = webob.Request.blank('/', headers=[('Accept', 'application/json')]).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"

    def test_accept_non_match(self):
        """
        Test that a non-accept'ing request is matched when there's an
        accept-ing handler too.
        """
        class Resource(resource.Resource):
            @resource.GET()
            def html(self, request):
                return http.ok([('Content-Type', 'text/html')], "<html />")
            @resource.GET(accept='application/json')
            def json(self, request):
                return http.ok([('Content-Type', 'application/json')], "{}")
        res = Resource()
        environ = webob.Request.blank('/', headers=[('Accept', 'text/html')]).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/html'

    def test_default_match(self):
        """
        Test that a client that does not send an Accept header gets a
        consistent response.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='html')
            def html(self, request):
                return http.ok([], '<p>Hello!</p>')
            @resource.GET(accept='json')
            def json(self, request):
                return http.ok([], '"Hello!"')
        res = Resource()
        environ = webob.Request.blank('/').environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/html'

    def test_no_subtype_match(self):
        """
        Test that something/* accept matches are found.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='text/*')
            def html(self, request):
                return http.ok([('Content-Type', 'text/plain')], 'Hello!')
        res = Resource()
        environ = webob.Request.blank('/', headers={'Accept': 'text/plain'}).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/plain'

    def test_quality(self):
        """
        Test that a client's accept quality is honoured.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='text/html')
            def html(self, request):
                return http.ok([('Content-Type', 'text/html')], '<p>Hello!</p>')
            @resource.GET(accept='text/plain')
            def plain(self, request):
                return http.ok([('Content-Type', 'text/plain')], 'Hello!')
        res = Resource()
        environ = webob.Request.blank('/', headers={'Accept': 'text/html;q=0.9,text/plain'}).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/plain'
        environ = webob.Request.blank('/', headers={'Accept': 'text/plain,text/html;q=0.9'}).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/plain'
        environ = webob.Request.blank('/', headers={'Accept': 'text/html;q=0.4,text/plain;q=0.5'}).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/plain'
        environ = webob.Request.blank('/', headers={'Accept': 'text/html;q=0.5,text/plain;q=0.4'}).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/html'

    def test_specificity(self):
        """
        Check that more specific mime types are matched in preference to *
        matches.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='html')
            def bbb(self, request):
                return http.ok([('Content-Type', 'text/html')], '')
            @resource.GET(accept='json')
            def aaa(self, request):
                return http.ok([('Content-Type', 'application/json')], '')
        res = Resource()
        environ = webob.Request.blank('/', headers={'Accept': '*/*, application/json, text/javascript'}).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        print response.headers['Content-Type']
        assert response.headers['Content-Type'] == 'application/json'

    # XXX skipped
    def _test_no_subtype_match_2(self):
        """
        Test that something/* accept matches are found, when there's also a
        '*/*' match,
        """
        class Resource(resource.Resource):
            @resource.GET()
            def anything(self, request):
                return http.ok([('Content-Type', 'text/html')], '<p>Hello!</p>')
            @resource.GET(accept='text/*')
            def html(self, request):
                return http.ok([('Content-Type', 'text/plain')], 'Hello!')
        res = Resource()
        environ = webob.Request.blank('/', headers={'Accept': 'text/plain'}).environ
        response = res(http.Request(environ))
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/plain'


class TestShortAccepts(unittest.TestCase):

    def test_single(self):
        """
        Check that short types known to Python's mimetypes module are expanded.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='html')
            def html(self, request):
                return http.ok([], "<html />")
        res = Resource()
        environ = webob.Request.blank('/', headers=[('Accept', 'text/html')]).environ
        response = res(http.Request(environ))
        print response.status
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/html'

    def test_extra(self):
        """
        Check that short types added by restish are expanded.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='json')
            def json(self, request):
                return http.ok([], "{}")
        res = Resource()
        environ = webob.Request.blank('/', headers=[('Accept', 'application/json')]).environ
        response = res(http.Request(environ))
        print response.status
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'application/json'

    def test_unknown(self):
        """
        Check that unknown short types are not expanded and are still used.
        """
        class Resource(resource.Resource):
            @resource.GET(accept='unknown')
            def unknown(self, request):
                return http.ok([], "{}")
        res = Resource()
        environ = webob.Request.blank('/').environ
        response = res(http.Request(environ))
        print response.status
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'unknown'


if __name__ == '__main__':
    unittest.main()

