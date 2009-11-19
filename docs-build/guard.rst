**************************
Access Control using Guard
**************************

Restish supplies a module called ``guard`` which makes applying access control easy to apply to resources or methods.

Basic Auth using repoze.who
---------------------------

A short example of implementing repoze.who as a guard using htpasswd files and basic http authentication.

Add the repoze line to the <project>.ini file

.. code-block:: ini

    [app:projectname]
    use = egg:projectname
    cache_dir = %(CACHE_DIR)s
    repoze.who.ini = %(here)s/who.ini

Add the repoze middle ware by adding these lines to wsgiapp.py

.. code-block:: python

    import repoze.who.config
    ...
    def make_app(global_conf, **app_conf):
        app = RestishApp(root.Root())
        app = repoze.who.config.make_middleware_with_config(app, global_conf, local_conf['who.ini'])
        app = setup_environ(app, global_conf, app_conf)
        return app

The default restish guard in ``{projectname}/lib`` includes an ``authenticated`` decorator that checks for a ``REMOTE_USER`` cookie. We can use this to decorate children or accept headers.

.. code-block:: python

    class Root(resource.Resource):

        @resource.GET()
        @guard.guard(guard.authenticated)
        def html(self, request):
            return http.ok([('Content-Type', 'text/html')],
                "<p>Hello from foo!</p>")

All that is left to do now is to configure repoze by creating a ``who.ini`` file..

The most basic configuration is 'basicauth' and 'htpasswd'. The configuration for this is shown below.

.. code-block:: ini

    [general]
    request_classifier = repoze.who.classifiers:default_request_classifier
    challenge_decider = repoze.who.classifiers:default_challenge_decider

    [identifiers]
    plugins = basicauth

    [authenticators]
    plugins = htpasswd

    [challengers]
    plugins = basicauth

    [plugin:basicauth]
    use = repoze.who.plugins.basicauth:make_plugin
    realm = 'sample'

    [plugin:htpasswd]
    use = repoze.who.plugins.htpasswd:make_plugin
    filename = %(here)s/passwd
    check_fn = repoze.who.plugins.htpasswd:crypt_check

The ``[general]`` block just sets up default classifiers and deciders which categorise the request type and decide which challenge to use (read the repoze.who docs to learn more). 

A list of prioritised plugins for each section need to be given and in this case basicauth can be used as an identifier and a challenger which needs configuring with a ``realm``. We're using htpasswd for the authenticator which needs a filename configuring and a check function (which we're defaulting to the built in).

All that is left is to create a ``passwd`` file using ``htpasswd``

.. code-block:: bash

  htpasswd -c passwd <username>

and you should now be able to run your project server and get a http challenge asking for username and password.









