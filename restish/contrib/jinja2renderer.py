"""
Jinja2 templating renderer than uses a Jinja2 "Environment" to find the
template to render.

An instance of a Jinja2Renderer can be used as the restish.templating.renderer
in the WSGI environ.

Recommended setup:

  * load templates from a directory of data files inside the application package
  * variable substitutions are converted to unicode instances and automatically
    HTML escaped.

e.g.

    environ['restish.templating.renderer'] = Jinja2Renderer(
        loader=jinja2.PackageLoader('yourpackage', 'templates'),
        autoescape=True)
"""

import jinja2


class Jinja2Renderer(object):

    def __init__(self, *a, **k):
        self.environment = jinja2.Environment(*a, **k)

    def __call__(self, template, args={}, encoding=None):
        template = self.environment.get_template(template)
        if encoding is None:
            return template.render(**args)
        return template.render(**args).encode(encoding)

