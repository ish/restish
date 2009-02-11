import cStringIO
import StringIO
import os
import tempfile
import unittest

from restish import app, http, resource
from restish.tests.util import wsgi_out


class Resource(resource.Resource):
    def __init__(self, body):
        self.body = body
    def __call__(self, request):
        return http.ok([], self.body)


class TestStreaming(unittest.TestCase):

    def test_string(self):
        R = wsgi_out(app.RestishApp(Resource('string')),
                     http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'string'

    def test_stringio(self):
        R = wsgi_out(app.RestishApp(Resource(StringIO.StringIO('stringio'))),
                     http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'stringio'

    def test_cstringio(self):
        R = wsgi_out(app.RestishApp(Resource(cStringIO.StringIO('cstringio'))),
                     http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'cstringio'

    def test_file(self):
        def file_closing_iter(f):
            try:
                while True:
                    data = f.read(100)
                    if not data:
                        return
                    yield data
            finally:
                f.close()
        (fd, filename) = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        f.write('file')
        f.close()
        f = open(filename)
        R = wsgi_out(app.RestishApp(Resource(file_closing_iter(f))),
                     http.Request.blank('/').environ)
        assert R['status'].startswith('200')
        assert R['body'] == 'file'
        assert f.closed
        os.remove(filename)

