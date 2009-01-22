"""
Genshi templating renderer than uses a Genshi TemplateLoader to find the
template to render.

An instance of a GenshiRenderer can be used as the restish.templating.renderer
in the WSGI environ.

Recommended setup:

  * load templates from a directory of data files inside the application
    package

e.g.

    environ['restish.templating.renderer'] = GenshiRenderer(
        genshi.template.loader.package('yourpackage', 'templates')
        )

Note: this may be too simplistic as it does not allow the final rendering
method ("xml", "xhtml", "html", "text", etc) to be specified. Think carefully
before using this class.
"""

from genshi.template.loader import TemplateLoader


class GenshiRenderer(object):

    def __init__(self, *a, **k):
        self.loader = TemplateLoader(*a, **k)

    def __call__(self, template, args={}, encoding=None):
        return self.loader.load(template).generate(**args).render(encoding=encoding)

