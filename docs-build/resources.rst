*****************
Restish Resources
*****************

Our project resource
====================

The root resource you get in your project looks like this

.. code-block:: python

    import logging
    from restish import http, resource

    log = logging.getLogger(__name__)

    class Root(resource.Resource):

        @resource.GET()
        def html(self, request):
            return http.ok([('Content-Type', 'text/html')],
                "<p>Hello from myproject!</p>")

Logging
-------

We think you should be using proper logging in your application for word go so restish makes a logger available at the top of the sample resource. You don't need to use this but we've found it a lot better than print statements.

``resource.Resource``
---------------------

.. note:: Matt to write a little note on resource.Resource

``@resource.GET()``
--------------------

resource also carries most of our resource decorators and can be used for url handling or http procesing. Here were are have decorated a method of our Root resource with a resource.GET().  This tells the resource to use this method for any GET responses. 

.. note:: Matt: add a bit about resource http handlers

Responses should always be either http response codes or a callable that will generate a response.

.. note:: Matt: add a bit about http responses

In this case we have returned a http response with a content type of text/html. Let's take a look at it.

.. code-block:: python

  http.ok( [ ('Content-Type', 'text/html') ], "<p>Hello from myproject!</p>")

The response is a list of tuples, each of which is a http header key and value. This is followed by the data for the http response.

Other restish http response codes
---------------------------------

We can also return a whole range of http responses. .

.. autofunction:: restish.http.ok
.. autofunction:: restish.http.created
.. autofunction:: restish.http.moved_permanently
.. autofunction:: restish.http.found
.. autofunction:: restish.http.see_other
.. autofunction:: restish.http.not_modified
.. autofunction:: restish.http.bad_request
.. autofunction:: restish.http.unauthorized
.. autofunction:: restish.http.forbidden
.. autofunction:: restish.http.not_found
.. autofunction:: restish.http.method_not_allowed
.. autofunction:: restish.http.not_acceptable
.. autofunction:: restish.http.conflict


So is that it? What else can it do for me?
------------------------------------------

To answer this, it is probably a good idea to go through a few examples. We'll work with Mako templates in this case so set up your make_renderer in lib/templating.py file to look like the following

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


Here is a syllabus of restish things to cover

1) Templating
    - using explicitly
    - using the templating.page decorator
    - adding your own global templating variables

2) handling GET and POST

   - resource.GET(
     resource.POST(
     PUT, DELETE
   - accept mimetypes handling

3) Simple Child methods

  - function name children
  - explicit one deep
  - explicit multi depth
  - any matcher

4) Using urls

   - constructing urls
   - urls in templates
    - path parameters?

5) example of a cookie wsgi app

   - Building the app
   - installing the app

6) example of a flashmessage wsgi app

   - Building the app
   - installing the app

7) Implementing guards

   - using a basic guard
   - using repoze.who

8) Examples

   - A rest api server
   - 

9) Using formish within restish

   - Typical pattern
   - multiple forms
