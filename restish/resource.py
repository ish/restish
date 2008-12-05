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
            return http.method_not_allowed(', '.join(self.request_dispatchers))
        # Look up the best dispatcher
        dispatcher = _best_dispatcher(dispatchers, request)
        if dispatcher is not None:
            (callable, match) = dispatcher
            response = callable(self, request)
            # Try to autocomplete the content-type header if not set
            # explicitly.
            # If there's no accept from the client and there's only one
            # possible type from the match then use that as the best match.
            # Otherwise use mimeparse to work out what the best match was. If
            # the best match if not a wildcard then we know what content-type
            # should be.
            if isinstance(response, http.Response) and \
                    not response.headers.get('content-type'):
                accept = str(request.accept)
                if not accept and len(match['accept']) == 1:
                    best_match = match['accept'][0]
                else:
                    best_match = mimeparse.best_match(match['accept'], accept)
                if '*' not in best_match:
                    response.headers['content-type'] = best_match
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
    supported = []
    for d in dispatchers:
        supported.extend(d[1]['accept'])
    # Find the best accept type
    best_match = mimeparse.best_match(supported, str(request.accept))
    # Return the matching dispatchers
    return [d for d in dispatchers if best_match in d[1]['accept']]


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
        if not isinstance(accept, list):
            accept = [accept]
        accept = [_normalise_mimetype(a) for a in accept]
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


def _normalise_mimetype(mimetype):
    if '/' in mimetype:
        return mimetype
    # Try mimetypes module, by extension.
    real = mimetypes.guess_type('filename.%s'%mimetype)[0]
    if real is not None:
        return real
    # Try extra extension mapping.
    real = SHORT_CONTENT_TYPE_EXTRA.get(mimetype)
    if real is not None:
        return real
    # Oh well.
    return mimetype

