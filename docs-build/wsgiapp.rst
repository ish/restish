Whats in the wsgiapp?
---------------------

The wsgiapp is shown below. make_app is set up to define the restish app by passing the root resource to it. The restish app is then passed to the setup_environ function which can be used to set any attributes on the ennviron you may wish. In this case templating is setup by calling 'make_renderer'.

.. code-block:: python

    from restish.app import RestishApp

    from myproject.resource import root


    def make_app(global_conf, **app_conf):
        """
        PasteDeploy WSGI application factory.

        Called by PasteDeply (or a compatable WSGI application host) to create the
        myproject WSGI application.
        """
        app = RestishApp(root.Root())
        app = setup_environ(app, global_conf, app_conf)
        return app


    def setup_environ(app, global_conf, app_conf):
        """
        WSGI application wrapper factory for extending the WSGI environ with
        application-specific keys.
        """

        # Create any objects that should exist for the lifetime of the application
        # here. Don't forget to actually include them in the environ below!
        from myproject.lib import templating
        renderer = templating.make_renderer(app_conf)

        def application(environ, start_response):

            # Add additional keys to the environ here.
            environ['restish.templating.renderer'] = renderer

            return app(environ, start_response)

        return application

