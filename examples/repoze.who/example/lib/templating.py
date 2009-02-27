"""
Templating support library and renderer configuration.
"""

from restish import templating


def make_templating(app_conf):
    renderer = make_renderer(app_conf)
    return Templating(renderer)


class Templating(templating.Templating):
    """
    Application-specific templating implementation.

    Overriding "args" methods makes it trivial to push extra, application-wide
    data to the templates without any assistance from the resource.
    """

    def args(self, request):
        args = super(Templating, self).args(request)
        args['remote_user'] = request.environ.get('REMOTE_USER')
        return args


def make_renderer(app_conf):
    """
    Create and return a restish.templating "renderer".
    """
    import pkg_resources
    from restish.contrib.tempitarenderer import TempitaRenderer, TempitaFileSystemLoader
    return TempitaRenderer(
            TempitaFileSystemLoader(
                pkg_resources.resource_filename('example', 'templates')
                )
            )

