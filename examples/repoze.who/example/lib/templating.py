"""
Templating support library and renderer configuration.
"""

from restish import templating


class Templating(templating.Templating):
    """
    Application-specific templating implementation.

    Overriding "args" methods makes it trivial to push extra, application-wide
    data to the templates without any assistance from the resource.
    """

    def __init__(self, app_conf):
        renderer = make_renderer(app_conf)
        templating.Templating.__init__(self, renderer)


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

