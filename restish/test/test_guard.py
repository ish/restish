import unittest
from webob import Request

from restish import guard, http


def make_checker(allow):
    def checker(request, obj):
        if not allow:
            raise http.UnauthorizedError()
    return checker


class TestGuard(unittest.TestCase):

    def test_decorator(self):

        class Resource(object):

            @guard.guard(make_checker(True))
            def allowed(self, request):
                pass

            @guard.guard(make_checker(False))
            def denied(self, request):
                pass

        request = Request.blank('/')
        Resource().allowed(request)
        self.assertRaises(http.UnauthorizedError, Resource().denied, request)

    def test_wrapper(self):

        class Resource(object):
            def resource_child(self, request, segments):
                return Resource(), segments[1:]
            def __call__(self, request):
                pass

        request = Request.blank('/')
        guard.GuardResource(Resource(), make_checker(True))(request)
        guard.GuardResource(Resource(), make_checker(True)).resource_child(request, ['foo'])
        self.assertRaises(http.UnauthorizedError, guard.GuardResource(Resource(), make_checker(False)), request)
        self.assertRaises(http.UnauthorizedError, guard.GuardResource(Resource(), make_checker(False)).resource_child, request, ['foo'])


if __name__ == '__main__':
    unittest.main()

