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
            raise guard.GuardError("No authenticated user.")
        
"""

import decorator

from restish import http


class GuardError(Exception):
    """
    Guard check failure.
    """

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

    # Add a property for 'message' to hide Python 2.6 deprecation warnings.
    def _get_message(self): return self._message
    def _set_message(self, message): self._message = message
    message = property(_get_message, _set_message)


def guard(*checkers, **kwargs):
    """
    Decorator that guards a function by calling each checker function before
    calling the decorated function.

    The only requirement is that the decorated function takes the request as
    the first positional arg.
    """

    # Bah, silly Python doesn't (yet) support explicit positional vs keyword
    # args so we'll have to handle it ourselves for now.
    error_handler = kwargs.pop('error_handler', _default_error_handler)
    if kwargs:
        raise TypeError('guard() got unexpected keyword arguments %r' % ('.'.join(kwargs),))

    def call(func, obj, request, *a, **k):
        """ Iterate checkers accumulating errors """
        errors = _run_guard_checkers(checkers, request, obj, error_handler)
        if errors:
            return error_handler(request, obj, errors)
        return func(obj, request, *a, **k)

    return decorator.decorator(call)


class GuardResource(object):
    """
    Resource wrapper that guards access to a resource by calling each checker
    before calling the wrapped resource's methods.
    """

    def __init__(self, resource, *checkers, **kwargs):
        # Bah, silly Python doesn't (yet) support explicit positional vs keyword
        # args so we'll have to handle it ourselves for now.
        error_handler = kwargs.pop('error_handler', _default_error_handler)
        if kwargs:
            raise TypeError('guard() got unexpected' \
                       ' keyword arguments %r' % ('.'.join(kwargs),))
        self.resource = resource
        self.checkers = checkers
        self.error_handler = error_handler

    def resource_child(self, request, segments):
        """
        Check the guard methods and raise error handler if errors
        """
        errors = _run_guard_checkers(self.checkers, request, \
                                     self.resource, self.error_handler)
        if errors:
            return self.error_handler(request, self.resource, errors)
        return self.resource.resource_child(request, segments)

    def __call__(self, request):
        errors = _run_guard_checkers(self.checkers, request, \
                                     self.resource, self.error_handler)
        if errors:
            return self.error_handler(request, self.resource, errors)
        return self.resource(request)


def _run_guard_checkers(checkers, request, obj, error_handler):
    """
    Iterate through the checks, accumulating errors
    """
    errors = []
    for checker in checkers:
        try:
            checker(request, obj)
        except GuardError, e:
            errors.append(e.message)
    return errors


def _default_error_handler(request, obj, errors):
    """
    Standard error handler produced unauthorized http response
    """
    errors_text = '\n'.join(errors)
    raise http.UnauthorizedError(
            [('Content-Type', 'text/plain')],
            """401 Unauthorized\n\n%s\n"""%errors_text)

