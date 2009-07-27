"""
Django templating renderer. Uses the django.template package to render
templates.

A DjangoRenderer instance can be used as the renderer passed to the
templating.Templating instance that is added to the WSGI environ.

Since Django relies on global configuration, and this module has no way to know
how the develop wants to use Django templates, the developer is responsible for
ensuring that django.conf.settings is available before the first template is
rendered. There are two ways to achieve this:

1. Set a DJANGO_SETTINGS_MODULE environment variable before starting the
   process. DJANGO_SETTINGS_MODULE should be the full module name of a Django
   configuration module.
2. Call django.settings.configure early on in the process's lifetime.

Recommended setup:

  * Load templates from a directory of data files inside the application
    package

e.g.

    import pkg_resources
    from django.conf import settings
    from restish.contrib.djangorenderer import DjangoRenderer
    settings.configure()
    settings.TEMPLATE_DIRS = [pkg_resources.resource_filename('yourpackage', 'template')]
    environ['restish.templating'] = templating.Templating(DjangoRenderer())
"""

from django.template import loader, Context


class DjangoRenderer(object):

    def __call__(self, template, args={}, encoding=None):
        content = loader.get_template(template).render(Context(args))
        if encoding is None:
            return  content
        return content.encode(encoding)

