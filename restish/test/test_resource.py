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

    def test_explicit_content_type(self):
        """
        Test that the content type is added automatically.
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
        Test generic GET matches request from client that does not send an Accept header.
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


class TestShortAccepts(unittest.TestCase):

    def test_single(self):
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


if __name__ == '__main__':
    unittest.main()

