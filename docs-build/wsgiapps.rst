**************************
How to work with WSGI Apps
**************************

This isn't a guide to how wsgi works but should help you if you want to plug wsgi stuff into a restish app.

Whats in the wsgiapp.py?
========================

The wsgiapp is shown below.

``make_app`` is set up to define the restish app by passing the root resource to it. The restish app is then passed to the setup_environ function

``setup_environ`` can be used to set any attributes on the environ you may wish. In this case templating is setup by creating a Templating instance.

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
        from myproject.lib.templating import Templating
        templating = Templating(app_conf)

        def application(environ, start_response):

            # Add additional keys to the environ here.
            environ['restish.templating'] = templating

            return app(environ, start_response)

        return application

Adding a WSGI app to our project
================================

To add your own middleware, include it in the appropriate place in the make_app (after setup_environ usually)

For an example, here is the cookies middleware being included

.. code-block:: python

    def make_app(global_conf, **app_conf):

        # Application "middleware", including environ setup
        app = RestishApp(root.Root())
        app = setup_environ(app, global_conf, app_conf)

        # General "middleware".
        app = cookies.cookies_middleware_factory(app)

        return app

Can I see an example of middleware please?
==========================================

OK, we'll take a look at an example we've developed while working with Restish

Cookies
-------

Most projects will end up using cookies in one way or another. We've built a middleware app to help with this.

Out cookie application will store any cookies changes on the environ and then when a response header is on it's way through the cookie middleware, it will apply the cookies onto the Set-Cookie header (handling deletion by setting a cookie to blank).

Firstly we'll create an application that can store the cookie changes..

.. code-block:: python

    class Cookies(object):

        def __init__(self, environ):
            self.environ = environ
            self.headers = []

        def set_cookie(self, cookie):
            if isinstance(cookie, str):
                pass
            elif isinstance(cookie, tuple):
                name, value = cookie
                cookie = SimpleCookie()
                cookie[name] = value or ''
                cookie[name]['path'] = self.environ['SCRIPT_NAME'] or '/'
                if value is None:
                    cookie[name]['expires'] = 0
                    cookie[name]['max-age'] = 0
                cookie = cookie.output(header='').strip()
            else:
                cookie = cookie.output(header='').strip()
            self.headers.append(cookie)

        def delete_cookie(self, cookie_name):
            self.set_cookie((cookie_name, None))

We have a ``Cookies`` manager that can set a cookie (by using python's built in Cookie module) and delete a cookie. Cookies are stored on the ``headers`` attribute.

Next we'll add a couple of utility functions make it simple to add cookies from our project code.

.. code-block:: python

    def set_cookie(environ, cookie):
        """
        Set a cookie using the Cookies in the WSGI environ.
        """
        return get_cookies(environ).set_cookie(cookie)


    def delete_cookie(environ, cookie_name):
        """
        Delete a cookie using the Cookies in the WSGI environ.
        """
        return get_cookies(environ).delete_cookie(cookie_name)


    def get_cookies(environ):
        """
        Find the Cookies instance from the WSGI environ.
        """
        return environ[ENVIRON_KEY]

We can now get, set and delete cookies by passing an environ to the cookie module

Finally we need to know how to wire this into the application. We create a middleware factory that can wrap an application with out new middleware

.. code-block:: python

    def cookies_middleware_factory(app):
        """
        Create a cookie middleware WSGI application around the given WSGI
        application.
        """
        def middleware(environ, start_response):
            def _start_response(status, response_headers, exc_info=None):
                # Extend the headers with cookie setting headers.
                cutter = environ[ENVIRON_KEY]
                response_headers.extend(('Set-Cookie', header) for header in cutter.headers)
                # Call wrapped app's start_response.
                return start_response(status, response_headers, exc_info)
            environ[ENVIRON_KEY] = Cookies(environ)
            return app(environ, _start_response)
        return middleware

If we pass an application to this factory, it returns the application wrapped with the cookies middleware.

The middleware adds an instance of our Cookie manager onto the environ (our ``ENVIRON_KEY`` is set to ``wsgiapptools.cookies`` at the top of our code) and implements a start response.

The start response gets the Cookie manager from the environ and iterates through it's headers, adding them to the response headers.

Take a look at the full code in the ``wsgiapptools`` package. 


