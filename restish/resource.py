import inspect

from restish import http


_RESTISH_METHOD = "restish_method"
_RESTISH_MATCH = "restish_match"


class _metaResource(type):
    def __init__(cls, name, bases, clsattrs):
        cls.__classinit__(clsattrs)


class Resource(object):

    __metaclass__ = _metaResource

    request_dispatchers = {}

    @classmethod
    def __classinit__(cls, clsattrs):
        for (name, callable) in inspect.getmembers(cls, inspect.ismethod):
            method = getattr(callable, _RESTISH_METHOD, None)
            if method is None:
                continue
            match = getattr(callable, _RESTISH_MATCH)
            cls.request_dispatchers.setdefault(method, []).append((callable, match))

    def resource_child(self, request, segments):
        return None, segments

    def __call__(self, request):
        dispatchers = self.request_dispatchers.get(request.method)
        if dispatchers is not None:
            callable = _best_dispatcher(dispatchers, request)
            if callable is not None:
                return callable(self, request)
        return http.method_not_allowed(', '.join(self.dispatchers))


def _best_dispatcher(dispatchers, request):
    """
    Find the best dispatcher for the request.
    """
    dispatcher = _best_accept_dispatcher(dispatchers, request)
    if dispatcher:
        return dispatcher[0]
    return None


def _best_accept_dispatcher(dispatchers, request):
    """
    Find the best dispatcher that matches an Accept header item.
    """
    for accept in request.accept.best_matches():
        for (callable, match) in dispatchers:
            if match.get('accept') == accept:
                return (callable, match)
    return None


class NotFound(Resource):

    def __call__(self, request):
        return http.not_found([], "404")


class MethodDecorator(object):

    def __init__(self, method):
        self.method = method

    def __call__(self, **match):
        def decorator(func):
            setattr(func, _RESTISH_METHOD, self.method)
            setattr(func, _RESTISH_MATCH, match)
            return func
        return decorator
        

DELETE = MethodDecorator('DELETE')
GET = MethodDecorator('GET')
POST = MethodDecorator('POST')
PUT = MethodDecorator('PUT')

