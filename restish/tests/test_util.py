import unittest
import webtest

from restish import app, http, util


def wsgi_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return 'SCRIPT_NAME: %(SCRIPT_NAME)s, PATH_INFO: %(PATH_INFO)s' % environ


class TestWSGI(unittest.TestCase):

    def test_wsgi(self):
        request = http.Request.blank('/foo/bar', environ={'REQUEST_METHOD': 'GET'})
        response = util.wsgi(request, wsgi_app, [u'foo', u'bar'])
        assert response.status == '200 OK'
        assert response.headers['Content-Type'] == 'text/plain'
        assert response.body == 'SCRIPT_NAME: , PATH_INFO: /foo/bar'
        response = util.wsgi(request, wsgi_app, [u'bar'])
        assert response.status == '200 OK'
        assert response.headers['Content-Type'] == 'text/plain'
        assert response.body == 'SCRIPT_NAME: /foo, PATH_INFO: /bar'

    def test_root_wsgi_resource(self):
        """
        Test a WSGIResource that is the root resource.
        """
        testapp = webtest.TestApp(app.RestishApp(util.WSGIResource(wsgi_app)))
        response = testapp.get('/foo/bar', status=200)
        assert response.headers['Content-Type'] == 'text/plain'
        assert response.body == 'SCRIPT_NAME: , PATH_INFO: /foo/bar'

    def test_child_wsgi_resource(self):
        """
        Test a WSGIResource that is a child of the root resource.
        """
        class Root(object):
            def resource_child(self, request, segments):
                return util.WSGIResource(wsgi_app), segments[1:]
        testapp = webtest.TestApp(app.RestishApp(Root()))
        response = testapp.get('/foo/bar', status=200)
        assert response.headers['Content-Type'] == 'text/plain'
        assert response.body == 'SCRIPT_NAME: /foo, PATH_INFO: /bar'

