"""
Base Resource class and associates methods for children and content negotiation
"""

import mimetypes
import re
import mimeparse

from restish import http


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
    Gather any request handler -annotated methods and add them to the class's
    request_dispatchers attribute.
    """
    # Collect the request handlers that *this* class adds first.
    request_dispatchers = {}
    for wrapper in _find_annotated_funcs(clsattrs, _RESTISH_METHOD):
        method = getattr(wrapper, _RESTISH_METHOD, None)
        match = getattr(wrapper, _RESTISH_MATCH)
        request_dispatchers.setdefault(method, []).append((wrapper.func, match))
    # Append any handlers that were added by base classes.
    for method, dispatchers in getattr(cls, 'request_dispatchers', {}).iteritems():
        request_dispatchers.setdefault(method, []).extend(dispatchers)
    # Set the handlers on the class.
    cls.request_dispatchers = request_dispatchers



def _gather_child_factories(cls, clsattrs):
    """
    Gather any 'child' annotated methods and add them to the class's
    child_factories attribute.
    """
    # Copy the super class's 'child_factories' list (if any) to this class.
    cls.child_factories = list(getattr(cls, 'child_factories', []))
    # Extend child_factories to include the ones found on this class.
    child_factories = _find_annotated_funcs(clsattrs, _RESTISH_CHILD)
    cls.child_factories.extend((getattr(f, _RESTISH_CHILD), f) \
                               for f in child_factories)
    # Sort the child factories by score.
    cls.child_factories = sorted(cls.child_factories, \
                                 key=lambda i: i[0].score, reverse=True)


def _find_annotated_funcs(clsattrs, annotation):
    """
    Return a (generated) list of methods that include the given annotation.
    """
    funcs = (func for func in clsattrs.itervalues() \
             if getattr(func, annotation, None) is not None)
    return funcs


class MethodDecorator(object):
    """
    content negotition decorator base class. See DELETE, GET, PUT, POST
    """

    method = None

    def __init__(self, accept='*/*', content_type='*/*'):
        if not isinstance(accept, list):
            accept = [accept]
        if not isinstance(content_type, list):
            content_type = [content_type]
        accept = [_normalise_mimetype(a) for a in accept]
        content_type = [_normalise_mimetype(a) for a in content_type]
        self.match = {'accept': accept, 'content_type': content_type}

    def __call__(self, func):
        wrapper = ResourceMethodWrapper(func)
        setattr(wrapper, _RESTISH_METHOD, self.method)
        setattr(wrapper, _RESTISH_MATCH, self.match)
        return wrapper


class ResourceMethodWrapper(object):
    """
    Wraps a @resource.GET etc -decorated function to ensure the function is
    only called with a matching request. If the request does not match then an
    HTTP error response is returned.

    Implementation note: The wrapper class is always added to decorated
    functions. However, the wrapper is discarded for Resource methods at the
    time the annotated methods are collected by the metaclass. This is because
    the Resource._call__ is already doing basicall the same work, only it has a
    whole suite of dispatchers to worry about.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self, request):
        # Extract annotations.
        method = getattr(self, _RESTISH_METHOD)
        match = getattr(self, _RESTISH_MATCH)
        # Check for correct method.
        if request.method != method:
            return http.method_not_allowed([method])
        # Look for a dispatcher.
        dispatcher = _best_dispatcher([(self.func, match)], request)
        if dispatcher is not None:
            return _dispatch(request, match, self.func)
        # No dispatcher.
        return http.not_acceptable([('Content-Type', 'text/plain')], \
                                   '406 Not Acceptable')

def _normalise_mimetype(mimetype):
    """
    Expand any shortcut mimetype names into a full mimetype
    """
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


class DELETE(MethodDecorator):
    """ http DELETE method """
    method = 'DELETE'


class GET(MethodDecorator):
    """ http GET method """
    method = 'GET'


class HEAD(MethodDecorator):
    """ http HEAD method """
    method = 'HEAD'


class POST(MethodDecorator):
    """ http POST method """
    method = 'POST'


class PUT(MethodDecorator):
    """ http PUT method """
    method = 'PUT'


class Resource(object):
    """
    Base class for additional resource types.

    Provides the basic API required of a resource (resource_child(request,
    segments) and __call__(request)), possibly dispatching to annotated methods
    of the class (using metaclass magic).
    """

    __metaclass__ = _metaResource

    def resource_child(self, request, segments):
        for matcher, func in self.child_factories:
            match = matcher(request, segments)
            if match is not None:
                break
        else:
            return None
        match_args, match_kwargs, segments = match
        result = func(self, request, segments, *match_args, **match_kwargs)
        if result is None:
            return None
        elif isinstance(result, tuple):
            return result
        else:
            return result, segments

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
            return _dispatch(request, match, lambda r: callable(self, r))
        # No match, send 406
        return http.not_acceptable([('Content-Type', 'text/plain')], \
                                   '406 Not Acceptable')

    @HEAD()
    def head(self, request):
        """
        Handle a HEAD request by calling the resource again as if a GET was
        sent and then discarding the content.

        This default HEAD behaviour works very well for dynamically generated
        content. However, it is not suitable for static content where the size
        is already known, e.g. large blobs stored in a database.

        In that scenario add a HEAD-decorated method to the application
        resource's class that includes a Content-Length header but no body.
        """
        request.method = 'GET'
        response = self(request)
        content_length = response.headers.get('content-length')
        response.body = ''
        if content_length is not None:
            response.headers['content-length'] = content_length
        return response


def _dispatch(request, match, func):
    response = func(request)
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


def _best_dispatcher(dispatchers, request):
    """
    Find the best dispatcher for the request.
    """
    # Use content negotation to filter the dispatchers to an ordered list of
    # only those that match.
    content_type = request.headers.get('content-type')
    if content_type:
        dispatchers = _filter_dispatchers_on_content_type(dispatchers, str(content_type))
    accept = request.headers.get('accept')
    if accept:
        dispatchers = _filter_dispatchers_on_accept(dispatchers, str(accept))
    # Return the best match or None
    if dispatchers:
        return dispatchers[0]
    else:
        return None

def _filter_dispatchers_on_content_type(dispatchers, content_type):
    # Build an ordered list of the supported types.
    supported = []
    for d in dispatchers:
        supported.extend(d[1]['content_type'])
    # Find the best type.
    best_match = mimeparse.best_match(supported, content_type)
    # Return the matching dispatchers
    return [d for d in dispatchers if best_match in d[1]['content_type']]


def _filter_dispatchers_on_accept(dispatchers, accept):
    # Build an ordered list of the supported types.
    supported = []
    for d in dispatchers:
        supported.extend(d[1]['accept'])
    # Find the best accept type
    best_match = mimeparse.best_match(supported, accept)
    # Return the matching dispatchers
    return [d for d in dispatchers if best_match in d[1]['accept']]


def child(matcher=None):
    """ Child decorator used for finding child resources """
    def decorator(func, matcher=matcher):
        # No matcher? Use the function name.
        if matcher is None:
            matcher = func.__name__
        # If the matcher is a string then create a TemplateChildMatcher in its
        # place.
        if isinstance(matcher, basestring):
            matcher = TemplateChildMatcher(matcher)
        # Annotate the function.
        setattr(func, _RESTISH_CHILD, matcher)
        # Return the function (unwrapped).
        return func
    return decorator


class TemplateChildMatcher(object):
    """
    A @child matcher that parses a template in the form /fixed/{dynamic}/fixed,
    extracting segments inside {} markers.
    """

    def __init__(self, pattern):
        self.pattern = pattern
        self._calc_score()
        self._compile()

    def _calc_score(self):
        """ Return the score for this element """
        def score(segment):
            if len(segment) >= 2 and segment[0] == '{' and segment[-1] == '}':
                return 0
            return 1
        segments = self.pattern.split('/')
        self.score = tuple(score(segment) for segment in segments)

    def _compile(self):
        """ compile the regexp to match segments """
        def re_segments(segments):
            for segment in segments:
                if len(segment) >= 2 and \
                   segment[0] == '{' and segment[-1] == '}':
                    yield '(?P<%s>.*?)' % segment[1:-1]
                else:
                    yield re.escape(segment)
        segments = self.pattern.split('/')
        self._count = len(segments)
        self._regex = re.compile('^' + '\\/'.join(re_segments(segments)) + '$')

    def __call__(self, request, segments):
        match_segments, remaining_segments = \
                segments[:self._count], segments[self._count:]
        # Note: no need to use the url module to join the path segments here
        # because we want the unquoted and decoded segments.
        match_path = '/'.join(match_segments)
        match = self._regex.match(match_path)
        if not match:
            return None
        return [], match.groupdict(), remaining_segments


class AnyChildMatcher(object):
    """
    A @child matcher that will always match, returning to match args and the
    list of segments unchanged.
    """

    score = ()

    def __call__(self, request, segments):
        return [], {}, segments


any = AnyChildMatcher()
