"""
Templating support.
"""

from restish import http, url, util
from restish.page import Element


class Rendering(object):
    """
    Rendering helper class, used to generate content from templates.
    """

    def render(self, request, template, args={}, encoding=None):
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
        renderer = request.environ['restish.templating.renderer']
        args_ = self.args(request)
        args_.update(args)
        return renderer(template, args_, encoding=encoding)

    def page(self, template, type='text/html', encoding='utf-8'):
        """
        Decorator that returns an HTTP response by rendering the returned dict of
        args using the template by calling render(request, template, args). The
        response's Content-Type header will be constructed from the type and
        encoding.

        The decorated method's first argument must be a http.Request instance. All
        arguments (including the request) are passed on as-is.

        The decorated method must return a dict that will be passed to the
        render(request, template, args) function.

        :arg template:
            Name of the template file.
        :arg type:
            Optional mime type of content, defaults to 'text/html'
        :arg encoding:
            Optional encoding of output, default to 'utf-8'.
        """
        def decorator(func):
            def decorated(page, request, *a, **k):
                # Collect the args from the callable.
                args = func(page, request, *a, **k)
                # Add common args and overwrite with those returned by the
                # decorated object.
                args_ = self.page_args(request, page)
                args_.update(args)
                # Render the template and return a response.
                return http.ok(
                        [('Content-Type', "%s; charset=%s"%(type, encoding))],
                        self.render(request, template, args=args_,
                                    encoding=encoding)
                        )
            return decorated
        return decorator

    def element(self, template):
        """
        Decorator that renders the returned dict of args using the template by
        calling render(request, template, args).

        The decorated method's first argument must be a http.Request instance. All
        arguments (including the request) are passed on as-is.

        The decorated method must return a dict that will be passed to the
        render(request, template, args) function.

        :arg template:
            Name of the template file.
        """
        def decorator(func):
            def decorated(element, request, *a, **k):
                # Collect the args from the callable.
                args = func(element, request, *a, **k)
                # Add common args and overwrite with those returned by the
                # decorated object.
                args_ = self.element_args(request, element)
                args_.update(args)
                # Render the template and return a response.
                return self.render(request, template, args=args_)
            return decorated
        return decorator

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


_rendering = Rendering()
render = _rendering.render
page = _rendering.page
element = _rendering.element

