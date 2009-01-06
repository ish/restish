import unittest

from restish import guard, http


def make_checker(allow, checker_num=1):
    def checker(request, obj):
        if not allow:
            raise guard.GuardError("checker #%d failed"%checker_num)
    return checker


class TestGuard(unittest.TestCase):

    def test_decorator(self):
        """
        Check the decorator is passing or failing in the correct manner.
        """

        class Resource(object):
            @guard.guard(make_checker(True))
            def allowed(self, request):
                pass
            @guard.guard(make_checker(False))
            def denied(self, request):
                pass

        request = http.Request.blank('/')
        Resource().allowed(request)
        self.assertRaises(http.UnauthorizedError, Resource().denied, request)

    def test_standard_failure(self):
        """
        Check that guard raises an UnauthorizedError by default.
        """
        class Resource(object):
            @guard.guard(make_checker(False))
            def denied(self, request):
                pass
        request = http.Request.blank('/')
        try:
            Resource().denied(request)
        except http.UnauthorizedError, e:
            response = e.make_response()
            assert response.headers['Content-Type'] == 'text/plain'
            assert response.body == """401 Unauthorized\n\nchecker #1 failed\n"""
        else:
            self.fail()

    def test_custom_failure(self):
        """
        Check that guard's response to a failure can be customised.
        """
        UNAUTHORIZED = object()
        def error_handler(request, resource, errors):
            return UNAUTHORIZED
        class Resource(object):
            @guard.guard(make_checker(False), error_handler=error_handler)
            def __call__(self, request):
                pass
        request = http.Request.blank('/')
        assert Resource()(request) is UNAUTHORIZED

    def test_multiple_failures(self):
        """
        Check that error messages from all checkers are in the default
        response.
        """
        class Resource(object):
            @guard.guard(make_checker(False, 1), make_checker(False, 2))
            def __call__(self, request):
                pass
        try:
            Resource()(http.Request.blank('/'))
        except http.UnauthorizedError, e:
            response = e.make_response()
            assert response.headers['Content-Type'] == 'text/plain'
            assert response.body == """401 Unauthorized\n\nchecker #1 failed\nchecker #2 failed\n"""
        else:
            self.fail()

    def test_wrapper(self):
        """
        Check the guard resource wrapper handles success and failure correctly.
        """

        class Resource(object):
            def resource_child(self, request, segments):
                return Resource(), segments[1:]
            def __call__(self, request):
                pass

        request = http.Request.blank('/')
        guard.GuardResource(Resource(), make_checker(True))(request)
        guard.GuardResource(Resource(), make_checker(True)).resource_child(request, ['foo'])
        self.assertRaises(http.UnauthorizedError, guard.GuardResource(Resource(), make_checker(False)), request)
        self.assertRaises(http.UnauthorizedError, guard.GuardResource(Resource(), make_checker(False)).resource_child, request, ['foo'])


class TestArgs(unittest.TestCase):
    """
    Check explicit keyword args handling.
    """

    def test_decorator(self):
        guard.guard()
        guard.guard(error_handler=lambda: None)
        self.assertRaises(TypeError, guard.guard, bad_arg=None)

    def test_resource(self):
        guard.GuardResource(None)
        guard.GuardResource(None, error_handler=lambda: None)
        self.assertRaises(TypeError, guard.GuardResource, None, bad_arg=None)


if __name__ == '__main__':
    unittest.main()

