"""
Templating support.
"""

from restism import http


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
    templating = request.environ['restism.templating']
    return renderer(templating)(template, args)


def template(template, content_type='text/html'):
    """
    Decorator that renders renders the returned dict of args using the
    template by calling render(request, template, args).

    The decorator can only be used on methods with a (self, request) signature
    where request is an http.Request instance.

    The decorated method must return a dict that will be passed to the
    render(request, template, args) function.

    @param template:
        Name of the template file.
    @param content_type:
        Optional content type, defaults to 'text/html'
    """
    def decorator(func):
        def decorated(self, request):
            args = func(self, request)
            return http.ok(
                    [('Content-Type', content_type)],
                    render(request, template, args=args)
                    )
        return decorated
    return decorator

