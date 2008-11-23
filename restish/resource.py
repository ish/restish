import inspect
import mimetypes

from restish import http, _mimeparse as mimeparse


_RESTISH_CHILD = "restish_child"
_RESTISH_METHOD = "restish_method"
_RESTISH_MATCH = "restish_match"


SHORT_CONTENT_TYPE_EXTRA = {
        'json': 'application/json',
        }


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
        # Get the dispatchers for the request method.
        dispatchers = self.request_dispatchers.get(request.method)
        # No dispatchers for method, send 405 with list of allowed methods.
        if dispatchers is None:
            print "* method_not_allowed"
            return http.method_not_allowed(', '.join(self.request_dispatchers))
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
        # No match, send 406
        return http.not_acceptable([('Content-Type', 'text/plain')], '406 Not Acceptable')


def _best_dispatcher(dispatchers, request):
    """
    Find the best dispatcher for the request.
    """
    # Use content negotation to filter the dispatchers to an ordered list of
    # only those that match.
    if 'accept' in request.headers:
        dispatchers = _filter_dispatchers_on_accept(dispatchers, request)
    # Return the best match or None
    return dispatchers[0] if dispatchers else None


def _filter_dispatchers_on_accept(dispatchers, request):
    # Build an ordered list of the accept matches
    supported = [d[1]['accept'] for d in dispatchers]
    # Find the best accept type
    best_match = mimeparse.best_match(supported, str(request.accept))
    #print "****", request.url, request.accept, supported, best_match
    # Return the matching dispatchers
    return [d for d in dispatchers if d[1]['accept'] == best_match]


class NotFound(Resource):

    def __call__(self, request):
        return http.not_found([('Content-Type', 'text/plain')], "404 Not Found")


def child(name=None):
    def decorator(func):
        setattr(func, _RESTISH_CHILD, name or func.__name__)
        return func
    return decorator


class MethodDecorator(object):

    method = None

    def __init__(self, accept='*/*'):
        if '/' not in accept:
            accept = _real_mimetype(accept)
        self.match = {'accept': accept}

    def __call__(self, func):
        setattr(func, _RESTISH_METHOD, self.method)
        setattr(func, _RESTISH_MATCH, self.match)
        return func
        

class DELETE(MethodDecorator):
    method = 'DELETE'


class GET(MethodDecorator):
    method = 'GET'


class POST(MethodDecorator):
    method = 'POST'


class PUT(MethodDecorator):
    method = 'PUT'


def _real_mimetype(short):
    # Try mimetypes module, by extension.
    real = mimetypes.guess_type('.%s'%short)[0]
    if real is not None:
        return real
    # Try extra extension mapping.
    real = SHORT_CONTENT_TYPE_EXTRA.get(short)
    if real is not None:
        return real
    # Oh well.
    return short

