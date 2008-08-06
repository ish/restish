"""
Templating support.
"""

from restish import http, util


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


def render(request, template, args={}):
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
    return renderer(templating)(template, args)


def page(template, content_type='text/html; charset=utf-8'):
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
        def decorated(self, request, *a, **k):
            # Collect the args from the callable.
            args = func(self, request, *a, **k)
            # Add common tags.
            args.update(_tags(request, self))
            # Render the template and return a response.
            return http.ok(
                    [('Content-Type', content_type)],
                    render(request, template, args=args)
                    )
        return decorated
    return decorator


def element(template):
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
        def decorated(self, request, *a, **k):
            # Collect the args from the callable.
            args = func(self, request, *a, **k)
            # Add common tags.
            args.update(_tags(request, self))
            # Render the template and return a response.
            return render(request, template, args=args)
        return decorated
    return decorator


def _tags(request, resource):
    """
    Return a dictionary of tags useful for templating.
    """
    def page_element(name):
        return util.RequestBoundCallable(
                resource.element(request, name),
                request)
    return {'element': page_element}

