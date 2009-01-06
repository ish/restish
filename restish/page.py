"""
Page resource.
"""

import inspect

from restish import resource


_RESTISH_ELEMENT = 'restish_element'


def element(name):
    """
    Decorator to mark a method as an element factory.
    """
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


class ElementMixin(object):
    """
    Mixin to allow the use of element lookups on the resource
    """

    element_name = None

    def element(self, request, name):
        """
        Locate an element by name.

        The element is cached for the duration of the request to ensure that
        the same object is returned if the element is located again later.
        """
        cache = _element_cache(request, self)
        try:
            element = cache[name]
        except KeyError:
            try:
                factory = self.element_factories[name]
            except KeyError:
                raise ElementNotFound(name)
            element = cache[name] = factory(self, request)
        element.element_name = _element_name(self.element_name, name)
        return element


class Page(ElementMixin, resource.Resource):
    """ Define a base Page type that includes elements """
    __metaclass__ = _metaPage


class Element(ElementMixin, object):
    """ Define a base Element type that is just an element """
    __metaclass__ = _metaElement


class ElementNotFound(Exception):
    pass


def _element_name(parent_name, child_name):
    """
    Return the new, abosolute element name
    """
    if parent_name is None:
        element_name = child_name
    else:
        element_name = '%s.%s' % (parent_name, child_name)
    return element_name


def _element_cache(request, parent):
    """
    Return the element cache for the parent.
    """
    cache = request.environ.setdefault('restish.page.element_cache', {})
    return cache.setdefault(parent, {})

