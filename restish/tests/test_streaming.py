import cStringIO
import StringIO
import os
import tempfile
import unittest
import webtest

from restish import app, http, resource


class Resource(resource.Resource):
    def __init__(self, body):
        self.body = body
    def __call__(self, request):
        return http.ok([('Content-Type', 'text/plain')], self.body)


class TestStreaming(unittest.TestCase):

    def test_string(self):
        R = webtest.TestApp(app.RestishApp(Resource('string'))).get('/')
        assert R.status.startswith('200')
        assert R.body == 'string'

    def test_stringio(self):
        R = webtest.TestApp(app.RestishApp(Resource(StringIO.StringIO('stringio')))).get('/')
        assert R.status.startswith('200')
        assert R.body == 'stringio'

    def test_cstringio(self):
        R = webtest.TestApp(app.RestishApp(Resource(cStringIO.StringIO('cstringio')))).get('/')
        assert R.status.startswith('200')
        assert R.body == 'cstringio'

    def test_file(self):
        class FileStreamer(object):
            def __init__(self, f):
                self.f = f
            def __iter__(self):
                return self
            def next(self):
                data = self.f.read(100)
                if data:
                    return data
                raise StopIteration()
            def close(self):
                self.f.close()
        (fd, filename) = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        f.write('file')
        f.close()
        f = open(filename)
        R = webtest.TestApp(app.RestishApp(Resource(FileStreamer(f)))).get('/')
        assert R.status.startswith('200')
        assert R.body == 'file'
        assert f.closed
        os.remove(filename)

