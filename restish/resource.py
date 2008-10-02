import inspect

from restish import http


_RESTISH_CHILD = "restish_child"
_RESTISH_METHOD = "restish_method"
_RESTISH_MATCH = "restish_match"


class _metaResource(type):
    """
    Resource meta class that gathers all annotations for easy access.
    """
    def __new__(cls, name, bases, clsattrs):
        cls = type.__new__(cls, name, bases, clsattrs)
        _gather_request_dispatchers(cls, clsattrs)
        _gather_child_factories(cls, clsattrs)
        return cls


def _gather_request_dispatchers(cls, clsattrs):
    """
    Find the methods marked as request dispatchers and return them as a mapping
    of name to (callable, match) tuples.
    """
    cls.request_dispatchers = dict(getattr(cls, 'request_dispatchers', {}))
    for (name, callable) in clsattrs.iteritems():
        if not inspect.isroutine(callable):
            continue
        method = getattr(callable, _RESTISH_METHOD, None)
        if method is None:
            continue
        match = getattr(callable, _RESTISH_MATCH)
        cls.request_dispatchers.setdefault(method, []).append((callable, match))


def _gather_child_factories(cls, clsattrs):
    """
    Find the methods marked as child factories and return them as a mapping of
    name to callable.
    """
    cls.child_factories = dict(getattr(cls, 'child_factories', {}))
    for (name, callable) in clsattrs.iteritems():
        if not inspect.isroutine(callable):
            continue
        child = getattr(callable, _RESTISH_CHILD, None)
        if child is None:
            continue
        cls.child_factories[child] = callable


class Resource(object):
    """
    Base class for additional resource types.

    Provides the basic API required of a resource (resource_child(request,
    segments) and __call__(request)), possibly dispatching to annotated methods
    of the class (using metaclass magic).
    """

    __metaclass__ = _metaResource

    def resource_child(self, request, segments):
        factory = self.child_factories.get(segments[0])
        if factory is not None:
            return factory(self, request), segments[1:]
        return None, segments

    def __call__(self, request):
        dispatchers = self.request_dispatchers.get(request.method)
        if dispatchers is not None:
            # Look up the best dispatcher
            dispatcher = _best_dispatcher(dispatchers, request)
            if dispatcher is not None:
                (callable, match) = dispatcher
                response = callable(self, request)
                # If we matched an 'Accept' header and the content type has not
                # been set explicitly then fill it in on behalf of the
                # application.
                if match.get('accept') and response.headers.get('content-type') is None:
                    response.headers['Content-Type'] = match['accept']
                return response
        # No dispatcher, return the list of allowed methods.
        return http.method_not_allowed(', '.join(self.request_dispatchers))


def _best_dispatcher(dispatchers, request):
    """
    Find the best dispatcher for the request.
    """
    dispatchers = _best_accept_dispatchers(dispatchers, request)
    dispatchers = list(dispatchers)
    if dispatchers:
        return dispatchers[0]
    return None


def _best_accept_dispatchers(dispatchers, request):
    """
    Return a (generate) list of dispatchers that match the request's accept
    header, ordered by the client's preferrence.
    """
    for accept in request.accept.best_matches():
        for (callable, match) in dispatchers:
            match_accept = match.get('accept')
            if match_accept is None or match_accept == accept:
                yield (callable, match)


class NotFound(Resource):

    def __call__(self, request):
        return http.not_found([('Content-Type', 'text/plain')], "404 Not Found")


def child(name):
    def decorator(func):
        setattr(func, _RESTISH_CHILD, name)
        return func
    return decorator


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

