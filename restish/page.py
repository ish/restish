"""
Page resource.
"""

import inspect
from webhelpers.html import literal

from restish import http, resource, templating


_RESTISH_ELEMENT = 'restish_element'


def element(name):
    def decorator(func):
        setattr(func, _RESTISH_ELEMENT, name)
        return func
    return decorator


class _metaPage(resource._metaResource):

    def __new__(cls, name, bases, clsattrs):
        cls = resource._metaResource.__new__(cls, name, bases, clsattrs)
        _gather_element_factories(cls, clsattrs)
        return cls


class _metaElement(type):
    def __new__(cls, name, bases, clsattrs):
        cls = type.__new__(cls, name, bases, clsattrs)
        _gather_element_factories(cls, clsattrs)
        return cls


def _gather_element_factories(cls, clsattrs):
    """
    Find the methods marked as element factories and return them as a mapping
    of name to callable.
    """
    cls.element_factories = dict(getattr(cls, 'element_factories', {}))
    for (name, callable) in clsattrs.iteritems():
        if not inspect.isroutine(callable):
            continue
        element = getattr(callable, _RESTISH_ELEMENT, None)
        if element is None:
            continue
        cls.element_factories[name] = callable


class LocateElementMixin(object):
    def page_element(self, request, segments):
        factory = self.element_factories[segments[0]]
        element = factory(self, request)
        return element


class Page(LocateElementMixin, resource.Resource):
    __metaclass__ = _metaPage


class Element(LocateElementMixin, object):
    __metaclass__ = _metaElement


def template(template, content_type='text/html; charset=utf-8'):
    """
    Decorator that renders renders the returned dict of args using the
    template by calling render(request, template, args).

    The decorated method's first argument must be a http.Request instance. All
    arguments (including the request) are passed on as-is.

    The decorated method must return a dict that will be passed to the
    render(request, template, args) function.

    @param template:
        Name of the template file.
    @param content_type:
        Optional content type, defaults to 'text/html'
    """
    def decorator(func):
        def decorated(self, request, *a, **k):
            # Collect the args from the callable.
            args = func(self, request, *a, **k)
            # Add common tags.
            args.update(_tags(request, self))
            # Render the template and return a response.
            return http.ok(
                    [('Content-Type', content_type)],
                    templating.render(request, template, args=args)
                    )
        return decorated
    return decorator


def _tags(request, resource):
    """
    Return a dictionary of tags useful for templating.
    """
    def page_element(name):
        return RequestBoundCallable(resource.element_child(request, name.split('.')), request)
    return {'element': page_element}


class RequestBoundCallable(object):

    def __init__(self, callable, request):
        self.callable = callable
        self.request = request

    def __call__(self, *a, **k):
        return literal(self.callable(self.request, *a, **k))

