import unittest

from restish import http, url


def make_environ(path='/bar', base_url='http://localhost:1234/foo', **k):
    return http.Request.blank(path, **k).environ


class TestCreation(unittest.TestCase):

    def test_init(self):
        template = http.Request.blank('/').environ
        assert http.Request(template).environ == template

    def test_blank(self):
        assert isinstance(http.Request.blank('/'), http.Request)


class TestAttributes(unittest.TestCase):

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

