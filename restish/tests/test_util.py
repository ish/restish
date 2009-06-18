import unittest

from restish import http, util


class TestWSGI(unittest.TestCase):

    def test_wsgi(self):
        def wsgi_app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [environ['SCRIPT_NAME'], ' ', environ['PATH_INFO']]
        request = http.Request.blank('/foo/bar', environ={'REQUEST_METHOD': 'GET'})
        response = util.wsgi(request, wsgi_app, [u'foo', u'bar'])
        assert response.status == '200 OK'
        assert response.headers['Content-Type'] == 'text/plain'
        assert response.body == ' /foo/bar'
        response = util.wsgi(request, wsgi_app, [u'bar'])
        assert response.status == '200 OK'
        assert response.headers['Content-Type'] == 'text/plain'
        assert response.body == '/foo /bar'

