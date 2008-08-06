"""
Page resource.
"""

import inspect

from restish import resource


_RESTISH_ELEMENT = 'restish_element'


def _element_name(parent_name, child_name):
    if parent_name is None:
        element_name = child_name
    else:
        element_name = '%s.%s' % (parent_name, child_name)
    return element_name


def element(name):
    def decorator(func):
        def f(self, request, *a, **k):
            cache = element_cache(request, self)
            try:
                element = cache[name]
            except KeyError:
                element = cache[name] = func(self, request, *a, **k)
                element.element_name = _element_name(self.element_name, name)
            return element
        setattr(f, _RESTISH_ELEMENT, name)
        return f
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


def element_cache(request, parent):
    cache = request.environ.setdefault('restish.page.element_cache', {})
    return cache.setdefault(parent, {})


class ElementMixin(object):

    element_name = None

    def element_child(self, request, segments):
        if isinstance(segments, str):
            segments = segments.split('.')
        if not segments:
            raise ValueError('segments')
        factory = self.element_factories[segments[0]]
        return factory(self, request)


class Page(ElementMixin, resource.Resource):
    __metaclass__ = _metaPage


class Element(ElementMixin, object):
    __metaclass__ = _metaElement

