import unittest

from restish import http, url


def make_environ(path='/bar', base_url='http://localhost:1234/foo', **k):
    return http.Request.blank(path, **k).environ


class TestRequestCreation(unittest.TestCase):

    def test_init(self):
        template = http.Request.blank('/').environ
        assert http.Request(template).environ == template

    def test_blank(self):
        assert isinstance(http.Request.blank('/'), http.Request)


class TestRequestAttributes(unittest.TestCase):

    def test_composition(self):
        request = http.Request(make_environ())
        self.assertTrue(request.environ)

    def test_url_types(self):
        request = http.Request(make_environ())
        self.assertTrue(isinstance(request.host_url, url.URL))
        self.assertTrue(isinstance(request.application_url, url.URL))
        self.assertTrue(isinstance(request.path_url, url.URL))
        self.assertTrue(isinstance(request.url, url.URL))
        self.assertTrue(isinstance(request.path, url.URL))
        self.assertTrue(isinstance(request.path_qs, url.URL))


class TestResponseCreation(unittest.TestCase):

    def test_init_with_bytes(self):
        return http.Response('200 OK', [('Content-Type', 'text/plain')], "bytes")

    def test_init_with_iter(self):
        def gen():
            yield ''
        return http.Response('200 OK', [('Content-Type', 'text/plain')], gen())


if __name__ == '__main__':
    unittest.main()

