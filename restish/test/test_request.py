import unittest
import webob

from restish import http, url


def make_environ(path='/bar', base_url='http://localhost:1234/foo', **k):
    return webob.Request.blank(path, **k).environ


class TestRequest(unittest.TestCase):

    def test_composition(self):
        request = http.Request(make_environ())
        self.assertTrue(request.environ)

    def test_url_types(self):
        request = http.Request(make_environ())
        self.assertTrue(isinstance(request.host_url, url.URL))
        self.assertTrue(isinstance(request.application_url, url.URL))
        self.assertTrue(isinstance(request.path_url, url.URL))
        self.assertTrue(isinstance(request.url, url.URL))


if __name__ == '__main__':
    unittest.main()

