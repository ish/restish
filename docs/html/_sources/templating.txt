*********************
Templating in Restish
*********************

Restish does not imply the use of any particular templating engine. Instead, we have provided stubs that can be used with some of the more popular templating engines which can be enabled by uncommenting a section within the wsgiapp.py.


Configuring a templating language within lib/templating.py
==========================================================

Here is an example of the uncommented code that enables the mako renderer.

.. code-block:: python

    def make_renderer(app_conf):
        """
        Create and return a restish.templating "renderer".
        """

        import pkg_resources
        import os.path
        from restish.contrib.makorenderer import MakoRenderer
        return MakoRenderer(
                directories=[
                    pkg_resources.resource_filename('myproject', 'templates')
                    ],
                module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
                input_encoding='utf-8', output_encoding='utf-8',
                default_filters=['unicode', 'h']
                )

The mako renderer configures the project template directory, a cache directory, our default encoding and a default filter (unicode, which is mako default, and html escaping, which we felt is safest).

Explicit templating
===================

You can call the templating engine explicity by using ``restish.templating``. e.g.

.. code-block:: python

    class Root(resource.Resource):

        @resource.GET()
        def html(self, request):
            content = templating.render(request, 'mytemplate.html', {'name': 'Tim'})
            return http.ok( [('Content-Type','text/html')], content )

Templating decorator
====================

However it is a lot easier to use the templating decorator. By adding this decorator, 

.. code-block:: python

    class Root(resource.Resource):

        @resource.GET()
        @templating.page('mytemplate.html')
        def html(self, request):
            return {'name': 'Tim'}

templating.page uses the content type passed in by the request so all you need
to do is provide a template in the decorator and the arguments for the template in the return dictionary.

Template Default Variables
==========================

Quite often you will write your own functions or want supply default variables to
use within your template (possibly a set of site urls). This can be set up
within the ``<project>/lib/templating.py`` by overriding the args method of the
Templating class.

.. code-block:: python

    class Templating(templating.Templating):

        def args(self, request):
            # Call the super class to get the basic set of args.
            args = super(Templating, self).args(request)
            # Push to the args and return them.
            args['myurldict'] = {'about': '/about', 'contact':'/contact'}
            return args

A better way of dealing with URLs
=================================

Using strings for urls isn't particularly safe in a lot of cases and sometimes
you might want a little more flexibility with your url handling. Also, some
urls are application specific and the template has no way of finding out what
the current url is. Restish automatically includes a ``urls`` arg which is a
``URLAccessor`` based on the current request.

.. note:: These attributes are the same as the attributes on the webob request object. See http://pythonpaste.org/webob/

.. autoattribute:: restish.url.URLAccessor.url
.. autoattribute:: restish.url.URLAccessor.path
.. autoattribute:: restish.url.URLAccessor.path_qs
.. autoattribute:: restish.url.URLAccessor.host_url
.. autoattribute:: restish.url.URLAccessor.path_url
.. autoattribute:: restish.url.URLAccessor.application_url

Let's see what these look like for an example url ``http://restish.com/tickets/search?u=foo#first`` which is a wsgi app mounted at ``/tickets``

===================================  =================================================
Template var                         Output
===================================  =================================================
``${urls.url}``                      ``http://restish.com/tickets/search?u=foo#first``
``${urls.path}``                     ``/tickets/search``
``${urls.path_qs}``                  ``/tickets/search?u=foo#first``
``${urls.host_url}``                 ``http://restish.com``
``${urls.path_url}``                 ``http://restish.com/tickets/search``
``${urls.application_url}``          ``http://restish.com/tickets``
===================================  =================================================

There is also a ``urls.new()`` method which allows you to create your own urls from scratch. Once you have one of these urls (or a new one) you can use some of the utility methods on them to create modified urls. e.g.

======================================================   ===================================================
Template var                                             Output
======================================================   ===================================================
``${urls.new('/').child('Tim Parkin')``                  ``/Tim%20Parkin``
``${urls.url.parent()}``                                 ``http://restish.com/tickets?u=foo#first``
``${urls.application_url.click('search?u=foo')``         ``/tickets/search?u=foo``
``${urls.url.sibling('help')}``                          ``http://restish.com/tickets/help?u=foo#first``
``${urls.url.sibling('help').path_qs}``                  ``/tickets/help?u=foo#first``
``${urls.path_qs.anchor()}``                             ``/tickets/search?u=foo``
``${urls.path_qs.anchor('last')}``                       ``/tickets/search?u=foo#last``
``${urls.path_qs.clear_queries()}``                      ``/tickets/search#last``
``${urls.path_qs.replace_query('u','bar')}``             ``/tickets/search?u=bar#first``
``${urls.path_qs.add_query('page','7')}``                ``/tickets/search?u=foo&page=7#first``
``${urls.url.secure()}``                                 ``https://restish.com/tickets/search?u=foo#first``
``${urls.path_qs.add_queries([('p','7'),('x','9')])}``   ``/tickets/search?u=foo&p=7&x=9#first``
======================================================   ===================================================

Here are the docstrings for the above methods/properties

.. automethod:: restish.url.URL.root
.. automethod:: restish.url.URL.sibling
.. automethod:: restish.url.URL.child
.. automethod:: restish.url.URL.parent
.. automethod:: restish.url.URL.click
.. automethod:: restish.url.URL.add_query
.. automethod:: restish.url.URL.add_queries
.. automethod:: restish.url.URL.replace_query
.. automethod:: restish.url.URL.remove_query
.. automethod:: restish.url.URL.clear_queries
.. automethod:: restish.url.URL.secure
.. automethod:: restish.url.URL.anchor

You can also filter particular parts of a url


.. autoattribute:: restish.url.URL.scheme
.. autoattribute:: restish.url.URL.netloc
.. autoattribute:: restish.url.URL.path
.. autoattribute:: restish.url.URL.path_qs
.. autoattribute:: restish.url.URL.path_segments
.. autoattribute:: restish.url.URL.query
.. autoattribute:: restish.url.URL.query_list
.. autoattribute:: restish.url.URL.fragment

Pages and Elements
==================

When more complex applications are developed, it is quite common to have resources that are used repeatedly on multiple pages. Restish includes two subclassses of resource called Page and Element. A Page is a resource that has a per request scoped registry of Elements (Where Elements are simple resources but which also have a registry of Elements to allow nested Elements).

An example of where this could be useful is where a login status is regularly included on pages throughout a site. 

.. code-block:: python

    class LoginStatusElement(page.Element):

        def __call__(self, request):
            return templating.render(request, 'login_status.html',{})

    class BasePage(page.Page):

        @page.element('login')
        def login_status(self, request):
            return auth.LoginStatusElement()

.. code-block:: html

    <div id="loginstatus"> ${element('login_status')()|n} </div>

