"""
Resource and method guards (the basis of access control).

This module consists of a decorator (guard) and a resource wrapper
(GuardResource) that iterate through a list of checker functions before
allowing access to the application.

A checker function is a callable that takes the request and the object being
protected as the two positional arguments. The checker function should raise an
HTTP exception to block access.

For example, the following checker tests if the request contains the name of an
authenticated user as the REMOTE_USER:

    def authenticated_checker(request, obj):
        if request.environ.get('REMOTE_USER') is None:
            raise http.UnauthorizedError()
        
"""

import decorator


def guard(*checkers):
    """
    Decorator that guards a function by calling each checker function before
    calling the decorated function.

    The only requirement is that the decorated function takes the request as
    the first positional arg.
    """
    def call(func, obj, request, *a, **k):
        _run_guard_checkers(checkers, request, obj)
        return func(obj, request, *a, **k)
    return decorator.decorator(call)


class GuardResource(object):
    """
    Resource wrapper that guards access to a resource by calling each checker
    before calling the wrapped resource's methods.
    """

    def __init__(self, resource, *checkers):
        self.resource = resource
        self.checkers = checkers

    def resource_child(self, request, segments):
        _run_guard_checkers(self.checkers, request, self.resource)
        return self.resource.resource_child(request, segments)

    def __call__(self, request):
        _run_guard_checkers(self.checkers, request, self.resource)
        return self.resource(request)


def _run_guard_checkers(checkers, request, obj):
    for checker in checkers:
        checker(request, obj)

