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

We can also return a whole range of http responses. 

.. note:: Returning ``None`` from a resource is equivalent to a 404

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


Content Negotiation
===================

Resources can perform content negotiation in a few different ways. The example above where ``GET()`` had not arguments accepts any (or no) content type. If we wanted to explictly return different types of document depending on the accept headers we can include this as a GET argument.

.. code-block:: python

    @resource.GET(accept='application/json')
    def json(self, request):
        return http.ok([('Content-Type', 'application/json')], "{}")

In this case, if the accept header was application/json, our empty json string would be returned.

If we had our argument-less GET resource also, then this would act as a 'catch-all' where everything apart from 'application/json' would return html. e.g.


.. code-block:: python

    @resource.GET()
    def catchall(self, request):
        return http.ok([('Content-Type', 'text/html')], "<strong>I'm HTML</strong>")

    @resource.GET(accept='application/json')
    def json(self, request):
        return http.ok([('Content-Type', 'application/json')], "{}")

We can use shorten ``text/html`` and ``text/json`` to just ``html`` and ``json``.

Wildcard content type matching also works. e.g. ``text/*``

.. note:: Content negotiation within restish also honours the clients accept-quality scores. e.g. if a client sends ``text/html;q=0.4,text/plain;q=0.5`` text/plain will be preferred. See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html

We sometimes want to match lists of content types, for example where we would like to use ``application/xhtml+xml``. This are honoured by restish. (See test_resource.py in the unit tests for examples)


Resource URL Handling
=====================

Restish implements a ``resource_child`` method on each resource which checks it's registered ``matchers`` to see if they are successful. If they are not, then None is returned (which is the same as a 404 response).

Matchers are any callable that returns another resource and a list of remaining segments. 

As far as most applications are concerned, they need not implement anything beyond the included matcher which is wired by default into the ``resource.child`` decorator. The uses of this method are described in the following sections.

Implicitly named child
----------------------

This takes it's segment matching from the method name. For instance, this code will match a segment named ``thanks`` and ignore any remaining segments. So if this were a root resource, it would match ``/thanks`` and ``/thanks/foo/bar``, amongst others.

.. code-block:: python

    @resource.child()
    def thanks(self, request, segments):
        return http.ok( [('Content-Type','text/html')], 'thanks' )

    
Explicitly named child
----------------------
Obviously this won't work where you have urls with non-python method name characters (for example a stylesheet). For this you can pass an explicit child name to the ``resource.child`` decorator.


.. code-block:: python

    @resource.child('styles.css')
    def styles(self, request, segments):
        return http.ok( [('Content-Type','text/css')], 'body { color: red; }' )

For any non-trivial application, you would want to handle a segment and pass everything below it to the next resource. 

Chaining Resources
------------------

We're showing a contrived example where the url ``/blog/entries/28`` get's passed down from resource to resource.

.. code-block:: python

    class Root(resource.Resource):

        @resource.child()
        def blog(self, request, segments):
            return Blog(), segments

    class Blog(resource.Resource):

        @resource.child()
        def entries(self, request, segments):
            return Entry(), segments

    class Entries(resource.Resource):
        
        @resource.GET()
        @templating.page('entry.html')
        def entry(self, request):
            blogcontent = db.get(self.segments[0])
            return {'content': blogcontent}


Template Resource Matchers
--------------------------

OK so that wasn't the most realistic example, for sites like blogger you would want to pick up the year and month and then the blog entry name. We can do this using the template style url matcher. We'll try that now..

.. code-block:: python

    class Root(resource.Resource):

        @resource.child('{year}/{month}')
        def blog_month_entries(self, request, segments, **kw):
            return BlogList(**kw), segments

        @resource.child('{year}/{month}/{entryid}')
        def blog(self, request, segments, **kw):
            return BlogPost(**kw), segments

    class BlogList(resource.Resource):

        def __init__(self, year=None, month=None):
            self.year = year
            self.month = month
        
        @resource.GET()
        @templating.page('EntryList.html')
        def entrylist(self, request):
            entries = db.get(year=self.year, month=self.month)
            return {'entries': entries}


    class BlogPost(resource.Resource):

        def __init__(self, entryid=None):
            self.entryid=entryid

        @resource.GET()
        @templating.page('entry.html')
        def entry(self, request):
            blogcontent = db.get(self.entryid)
            return {'content': blogcontent}

Custom Matchers
---------------

You can pass your own matchers to the child method if you like. For instance, let's process the following search url ``/search/python?u=foo``

.. code-block:: python

    def mymatcher(page, segments):
        if len(segments) >2 and segments[0] == 'search':
            category = segments[1]
            search_string = request.GET.get('u',None)
        return {'category': category, 'search_string': search_string}, ()
  
    class Root(resource.Resource):

        @resource.child(mymatcher)
        def search(self, request, segments, **kw):
            return SearchResults(**kw)

    class SearchResults(resource.Resource):

        def __init__(self, **kw):
            self.category=kw.get('category')
            self.search_string=kw.get('search_string')
        
        @resource.GET()
        def html(self, request):
            results = indexer.get(category=self.category, search_term=self.search_term)






1) Other methods

   -  PUT, DELETE

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

9) Using formish within restish

   - Typical pattern
   - multiple forms
