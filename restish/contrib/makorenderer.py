"""
Mako templating renderer than uses Mako's template lookup to find the template
to render.

A MakoRenderer instance can be used as the renderer passed to the
templating.Templating instance that is added to the WSGI environ.

Recommended setup:

  * load templates from a directory of data files inside the application package
  * the disk templates and generated content are UTF-8 encoded
  * variable substitutions are converted to unicode instances and automatically
    HTML escaped.

e.g.

    environ['restish.templating'] = templating.Templating(
        MakoRenderer(
            directories=[pkg_resources.resource_filename('yourpackage', 'templates')],
            module_directory=os.path.join(cache_dir, 'templates'),
            input_encoding='utf-8', output_encoding='utf-8',
            default_filters=['unicode', 'h']
            )
        )
"""

from mako.lookup import TemplateLookup


class MakoRenderer(object):

    def __init__(self, *a, **k):
        self.lookup = TemplateLookup(*a, **k)

    def __call__(self, template, args={}, encoding=None):
        template = self.lookup.get_template(template)
        # Use render_unicode for if no encoding.
        if encoding is None:
            return template.render_unicode(**args)
        # If the encoding is different to the template's configured (via the
        # lookup) encoding then do the encoding manually. Otherwise, let Mako
        # encode the output.
        if encoding != template.output_encoding:
            return template.render_unicode(**args).encode(encoding)
        else:
            return template.render(**args)

