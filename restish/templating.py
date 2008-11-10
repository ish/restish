"""
Templating support.
"""

from restish import http, url, util


def _mako_renderer(lookup):
    """
    Create a Mako renderer that looks up the template in the given lookup
    instance.

    @param lookup:
        Mako TemplateLookup instance.
    """
    def render(template, args={}):
        t = lookup.get_template(template)
        return t.render(**args)
    return render


RENDERERS = {
        'mako': _mako_renderer,
        }


def renderer(config):
    """
    Create and return a template renderer from the provided config.

    The config is a dict that must include an 'engine' item whose value is a
    key in the RENDERERS dict of factories. 'engine' is removed from the config
    dict and any remaining items are passed as keyword args to the factory.

    @param config:
        Dict of templating configuration, including at least an 'engine' key.
    """
    config = dict(config)
    engine = config.pop('engine')
    return RENDERERS[engine](**config)


class Rendering(object):

    def render(self, request, template, args={}):
        """
        Render the template and args using the configured templating engine.

        @param request:
            Request instance.
        @param template:
            Name of the template file.
        @param args:
            Dictionary of args to pass to the template renderer.
        """
        templating = request.environ['restish.templating']
        args_ = self.args(request)
        args_.update(args)
        return renderer(templating)(template, args_)

    def page(self, template, content_type='text/html; charset=utf-8'):
        """
        Decorator that returns an HTTP response by rendering the returned dict of
        args using the template by calling render(request, template, args).

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
            def decorated(page, request, *a, **k):
                # Collect the args from the callable.
                args = func(page, request, *a, **k)
                # Add common args and overwrite with those returned by the
                # decorated object.
                args_ = self.page_args(request, page)
                args_.update(args)
                # Render the template and return a response.
                return http.ok(
                        [('Content-Type', content_type)],
                        render(request, template, args=args_)
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

        @param template:
            Name of the template file.
        @param content_type:
            Optional content type, defaults to 'text/html'
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
                return render(request, template, args=args_)
            return decorated
        return decorator

    def args(self, request):
        """
        Return a dict of args that should always be present.
        """
        return {'url': url.URLAccessor(request)}

    def element_args(self, request, element):
        """
        Return a dict of args that should be present when rendering elements.
        """
        def page_element(name):
            return util.RequestBoundCallable(
                    element.element(request, name),
                    request)
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

