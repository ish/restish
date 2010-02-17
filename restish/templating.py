"""
Templating support.
"""

from restish import http, url, util
from restish.page import Element


class Templating(object):
    
    def __init__(self, renderer):
        self.renderer = renderer or _missing_renderer

    def render(self, request, template, args=None, encoding=None):
        """
        Render the template and args, optionally encoding to a byte string.
        """
        return self.renderer(template, args, encoding=encoding)

    def args(self, request):
        """
        Return a dict of args that should always be present.
        """
        return {'urls': url.URLAccessor(request)}

    def element_args(self, request, element):
        """
        Return a dict of args that should be present when rendering elements.
        """
        def page_element(name):
            E = element.element(request, name)
            if isinstance(E, Element):
                E = util.RequestBoundCallable(E, request)
            return E
        args = self.args(request)
        args['element'] = page_element
        return args

    def page_args(self, request, page):
        """
        Return a dict of args that should be present when rendering pages.
        """
        return self.element_args(request, page)


def render(request, template, args={}, encoding=None):
    """
    Render the template and args using the configured templating engine.

    :arg request:
        Request instance.
    :arg template:
        Name of the template file.
    :arg args:
        Dictionary of args to pass to the template renderer.
    :arg encoding:
        Optional output encoding, defaults to None, i.e. output will be
        unicode (or unicode-safe).
    """
    # Lookup the templating implementation.
    templating = request.environ['restish.templating']
    # Combine common args with those passed in.
    args_ = templating.args(request)
    args_.update(args)
    # Return the rendered template.
    return templating.render(request, template, args_, encoding=encoding)


def render_element(request, element, template, args={}):
    """
    Render a page element using the template and args.

    :arg request:
        Request instance.
    :arg element:
        Element being rendered (hint, it's often self).
    :arg template:
        Name of the template file.
    :arg args:
        Dictionary of args to pass to the template renderer.
    """
    # Lookup the templating implementation.
    templating = request.environ['restish.templating']
    # Combine common element args with those passed in.
    args_ = templating.element_args(request, element)
    args_.update(args)
    # Return the rendered template.
    return templating.render(request, template, args=args_)


def render_page(request, page, template, args={}, encoding='utf-8'):
    """
    Render a page using the template and args.

    :arg request:
        Request instance.
    :arg page:
        Page being rendered (hint, it's often self).
    :arg template:
        Name of the template file.
    :arg args:
        Dictionary of args to pass to the template renderer.
    :arg encoding:
        Optional encoding of output, default to 'utf-8'.
    """
    # Lookup the templating implementation.
    templating = request.environ['restish.templating']
    # Combine common page args with those passed in.
    args_ = templating.page_args(request, page)
    args_.update(args)
    # Return the rendered template.
    return templating.render(request, template, args=args_, encoding=encoding)


def render_response(request, page, template, args={},
                    type='text/html', encoding='utf-8',
                    headers=[]):
    """
    Render a page, using the template and args, and return a '200 OK'
    response.  The response's Content-Type header will be constructed from
    the type and encoding.

    :arg request:
        Request instance.
    :arg page:
        Page being rendered (hint, it's often self).
    :arg template:
        Name of the template file.
    :arg args:
        Dictionary of args to pass to the template renderer.
    :arg type:
        Optional mime type of content, defaults to 'text/html'
    :arg encoding:
        Optional encoding of output, default to 'utf-8'.
    :arg headers:
        Optional extra HTTP headers for the output, default to []
    """
    # Copy the headers to avoid changing the arg default or the list passed by
    # the caller.
    headers = list(headers)
    headers.extend([('Content-Type', '%s; charset=%s' % (type, encoding))])
    return http.ok(headers,
                   render_page(request, page, template, args,
                               encoding=encoding))


def page(template, type='text/html', encoding='utf-8'):
    """
    Convenience decorator that calls render_response, passing the dict
    returned from calling the decorated method as the template 'args'.

    The decorated method's first argument must be a http.Request instance. All
    arguments (including the request) are passed on as-is.

    The decorated method must return a dict that will be passed to the
    render_response method as the args parameter.

    Note: if the decorator does not allow full control consider calling
    render_response directly.

    :arg template:
        Name of the template file.
    :arg type:
        Optional mime type of content, defaults to 'text/html'
    :arg encoding:
        Optional encoding of output, default to 'utf-8'.
    """
    def decorator(func):
        def decorated(page, request, *a, **k):
            result = func(page, request, *a, **k)
            # The returned value can be either a (headers, args) tuple or just
            # an args dict.
            if isinstance(result, tuple):
                headers, args = result
            else:
                headers, args = [], result
            return render_response(request, page, template, args, type=type,
                                   encoding=encoding, headers=headers)
        return decorated
    return decorator


def element(template):
    """
    Convenience decorator that calls render_element, passing the dict
    returned from calling the decorated method as the template 'args'.

    The decorated method's first argument must be a http.Request instance. All
    arguments (including the request) are passed on as-is.

    The decorated method must return a dict that will be passed to the
    render_element methods as the args parameter.

    :arg template:
        Name of the template file.
    """
    def decorator(func):
        def decorated(element, request, *a, **k):
            args = func(element, request, *a, **k)
            return render_element(request, element, template, args)
        return decorated
    return decorator


def _missing_renderer(*a, **k):
    """
    Dummy renderer used to provide a nice error message when the templating
    has not been configured.
    """
    raise TypeError("Please configure templating with a renderer before "
                    "using it.")

