"""
Test resource behaviour.
"""

import unittest
import webob

from restish import app, http, resource
from restish.test.util import wsgi_out


class TestChildren(unittest.TestCase):

    def test_child_factory(self):
        class FooResource(resource.Resource):
            @resource.GET()
            def text(self, request):
                return http.ok([('Content-Type', 'text/plain')], 'Foo')
        class Resource(resource.Resource):
            @resource.child('foo')
            def foo(self, request):
                return FooResource()
        A = app.RestishApp(Resource())
        R = wsgi_out(A, webob.Request.blank('/foo').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'Foo'


class TestContentNegotiation(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()

