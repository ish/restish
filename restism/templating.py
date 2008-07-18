def mako_renderer(lookup):
    def render(template, args={}):
        t = lookup.get_template(template)
        return t.render(**args)
    return render


RENDERERS = {
        'mako': mako_renderer,
        }


def renderer(config):
    config = dict(config)
    engine = config.pop('engine')
    return RENDERERS[engine](**config)


def render(request, template, args={}):
    templates = request.environ['restism.templating']
    return renderer(templates)(template, args)

