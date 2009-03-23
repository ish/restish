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
        self.assertTrue(isinstance(request.application_path, url.URL))
        self.assertTrue(isinstance(request.path_url, url.URL))
        self.assertTrue(isinstance(request.url, url.URL))
        self.assertTrue(isinstance(request.path, url.URL))
        self.assertTrue(isinstance(request.path_qs, url.URL))

    def test_application_path(self):
        r = http.Request.blank('/')
        self.assertEquals(r.application_path, '')
        r = http.Request.blank('/', base_url='/foo')
        self.assertEquals(r.application_path, '/foo')
        r = http.Request.blank('/', base_url='/foo/')
        self.assertEquals(r.application_path, '/foo/')


class TestResponseCreation(unittest.TestCase):

    def test_init_with_bytes(self):
        return http.Response('200 OK', [('Content-Type', 'text/plain')], "bytes")

    def test_init_with_iter(self):
        def gen():
            yield ''
        return http.Response('200 OK', [('Content-Type', 'text/plain')], gen())

    def test_init_with_none(self):
        return http.Response('200 OK', [], None)

    def test_no_implicit_headers(self):
        r = http.Response('200 OK', [], None)
        assert r.headers == {'Content-Length': '0'}


class TestSuccessResponseFactories(unittest.TestCase):

    def test_ok(self):
        r = http.ok([('Content-Type', 'text/plain')], 'Yay!')
        assert r.status.startswith('200')
        assert r.headers['Content-Type'] == 'text/plain'
        assert r.body == 'Yay!'

    def test_created(self):
        location = 'http://localhost/abc'
        r = http.created(location, location, [('Content-Type', 'text/plain')])
        assert r.status.startswith('201')
        assert r.headers['Content-Type'] == 'text/plain'
        assert r.headers['Location'] == location
        assert r.body == location

    def test_moved_permanently(self):
        location = 'http://localhost/abc'
        r = http.moved_permanently(location)
        assert r.status.startswith('301')
        assert r.headers['Location'] == location

    def test_found(self):
        location = 'http://localhost/abc'
        r = http.found(location)
        assert r.status.startswith('302')
        assert r.headers['Location'] == location

    def test_see_other(self):
        location = 'http://localhost/abc'
        r = http.see_other(location)
        assert r.status.startswith('303')
        assert r.headers['Location'] == location

    def test_not_modified(self):
        r = http.not_modified()
        assert r.status.startswith('304')
        r = http.not_modified([('ETag', '123')])
        assert r.status.startswith('304')
        assert r.headers['ETag'] == '123'


class TestServerErrorResponseFactories(unittest.TestCase):

    tests = [
        (http.internal_server_error, http.InternalServerError, [], {}, '500'),
        (http.bad_gateway, http.BadGatewayError, [], {}, '502'),
        (http.service_unavailable, http.ServiceUnavailableError, [], {}, '503'),
        (http.gateway_timeout, http.GatewayTimeoutError, [], {}, '504'),
    ]

    def test_responses(self):
        for func, cls, a, k, status in self.tests:
            r = func(*a, **k)
            assert r.status.startswith(status)
            assert r.headers['Content-Type'] == 'text/plain'
            assert r.body.startswith(status)


if __name__ == '__main__':
    unittest.main()

