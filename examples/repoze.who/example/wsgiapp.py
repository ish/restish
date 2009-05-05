"""
WSGI/PasteDeploy application bootstrap module.
"""

from restish.app import RestishApp
from repoze.who.config import make_middleware_with_config

from example.resource import root


def make_app(global_conf, **app_conf):
    """
    PasteDeploy WSGI application factory.

    Called by PasteDeply (or a compatable WSGI application host) to create the
    example WSGI application.
    """
    app = RestishApp(root.Root())
    app = make_middleware_with_config(app, global_conf, 'who.ini')
    app = setup_environ(app, global_conf, app_conf)
    return app


def setup_environ(app, global_conf, app_conf):
    """
    WSGI application wrapper factory for extending the WSGI environ with
    application-specific keys.
    """

    # Create any objects that should exist for the lifetime of the application
    # here. Don't forget to actually include them in the environ below!
    from example.lib.templating import make_templating
    templating = make_templating(app_conf)

    def application(environ, start_response):
        # Add additional keys to the environ here.
        environ['restish.templating'] = templating
        return app(environ, start_response)

    return application

