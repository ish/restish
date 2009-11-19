*****************
Restish Resources
*****************

Our project resource
====================

The root resource in your project looks like this

.. code-block:: python

    import logging
    from restish import http, resource

    log = logging.getLogger(__name__)

    class Root(resource.Resource):

        @resource.GET()
        def html(self, request):
            return http.ok([('Content-Type', 'text/html')],
                "<p>Hello from myproject!</p>")

This is just an example to get you going. Lets take a look at what it does.

Logging
-------

.. code-block:: python

    import logging
    log = logging.getLogger(__name__)

We think you should be using proper logging in your application so restish
makes a logger available at the top of the sample resource. You don't need to
use this but we've found good logging to be incredibly useful.

So what is a resource?
----------------------

At it's most basic, a restish Resource is anything callable that returns http
content. However, restish provides a base class that allows resources to have
children and to negotiate what content type to return. 

Restish handles urls by first breaking them into segments. It then passes this
list of segments to the root
Resource. 

The root resource uses its ``resource_child`` method to see if there are any
segments it can 'consume'. Once it has consumed segments (or not) it calls
another resource and the process continues.

The process stops when a resource is called with no more segments to
process.Content is then returned based on request method and content headers
(i.e. ``accept``).

We'll look at the URL handling to begin with


Resource URL Handling
=====================

The restish resource class implements a ``resource_child`` method which
checks a set of ``matchers`` to see if any of them are successful. If they are
not, then None is returned (which is the same as a 404 response).

A matchers is any callable that returns a resource and a list of remaining
segments (or an empty list if there are no segments left). 

Most applications will not use ``resource_child`` however as there is a 'child'
decorator on the resource base class. This child decorator has various ways of
matching parts of urls and dispatching to other resources that we will discuss
now.

.. note:: The segments argument that is passed to a child function contains the remaining segments **after** the child match has been removed. 

Implicitly named child
----------------------

this takes its segment match from the decorated method's name and only consumes
one segment.

For instance, this code will match a segment named ``thanks`` and ignore any
remaining segments. So if this were a root resource, it would match ``/thanks``
and ``/thanks/foo/bar``, amongst others. 

.. code-block:: python

    def thank_you(self, request):
        return http.ok( [('Content-Type','text/html')], 'thank you' )
        
    @resource.child()
    def thanks(self, request, segments):
        return self.thank_you

If we wanted to pass the remaining segments onto another resource, we would use
the following.

.. code-block:: python

    @resource.child()
    def thanks(self, request, segments):
        return Thanks()

    class Thanks(restish.Resource):
        """ see later for content docs """
      
The Thanks resource would then have to process any remaining segments if there
were any, and if not then the Thanks resource would provide content). 
    
Explicitly named child
----------------------

Obviously this won't work where you have urls with non-python method name
characters (for example any file-like name with a period character). For this
you can pass an explicit child name to the ``resource.child`` decorator.


.. code-block:: python

    @resource.child('styles.css')
    def styles(self, request, segments):
        return http.ok( [('Content-Type','text/css')], 'body { color: red; }' )


Chaining Resources
------------------

Most applications will handle nested resources.

We're showing a contrived example where the url ``/blog/entries/28`` get's
passed down from resource to resource.

.. code-block:: python

    class Root(resource.Resource):

        @resource.child()
        def blog(self, request, segments):
            return Blog()

    class Blog(resource.Resource):

        @resource.child()
        def entries(self, request, segments):
            # 'segments' contains everything below /blog/entries
            # Pass the first segment through to Entry (should be entry id) 
            # The empty list says pass no more segments to Entry
            return Entry(segments[0]), []

    class Entry(resource.Resource):

        def __init__(self, id):
            self.id = id
        
        @resource.GET()
        @templating.page('entry.html')
        def entry(self, request):
            blogcontent = db.get(self.id)
            return {'content': blogcontent}

.. note:: If you want to stop further url traversal, explicitly return no further segments (e.g. ``return Entry(segments[0]), []`` in the Blog example above)

Handling it yourself
--------------------

If you want to handle the url matching yourself then you can use the resource.any matcher. This literally matches any pattern and consumes nothing. This means you have to work out what path segments you want to pass on to the next child. (in this case ``, segments[1:]``)

.. code-block:: python

    class Root(resources.Resource):

        @resource.child(resource.any)
        def child(self, request, segments):
            # At his point segments contains all the segments
            if segments[0] == 'mymatchingsegment':
                # now I've matched a segment, I need to return the rest as follows
                return MyMatchingResource(), segments[1:]




Template Resource Matchers
--------------------------

OK so that wasn't the most realistic example, for sites like blogger you would
want to pick up the year and month and then the blog entry name. We can do this
using the template style url matcher. We'll try that now..

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

        def __init__(self, year=None, month=None, entryid=None):
            self.entryid=entryid

        @resource.GET()
        @templating.page('Entry.html')
        def entry(self, request):
            blogcontent = db.get(self.entryid)
            return {'content': blogcontent}

This works because when we have more than one matcher, the Resource works out
which one to use based on a calculated 'specificity'; The more specific match
gets used.

Which child to use?
-------------------

Here are some examples from the unit tests.

.. code-block:: python

    @resource.child('a/b/c')
    @resource.child('a/b/{c}')
    @resource.child('a/{b}/c/{d}')
    @resource.child('a/b/{c}/{d}')
    @resource.child('a/{b}/{c}')
    @resource.child('a')
    @resource.child('{a}/b/c')
    @resource.child(resource.any)

We'll look at a few different matches to work out why they match

/a/b/c
^^^^^^

.. code-block:: python

    @resource.child('a/b/c')
    @resource.child('a/b/{c}')
    @resource.child('a/{b}/{c}')
    @resource.child('a')
    @resource.child('{a}/b/c')
    @resource.child(resource.any)

All of these resources match this url but we have an exact match so the first
wins.

/a/b/foo
^^^^^^^^

Only these match

.. code-block:: python

    @resource.child('a/b/{c}')
    @resource.child('a/{b}/{c}')
    @resource.child('a')
    @resource.child(resource.any)

The specifity is calculated to the top level matches are considered more
specific. In this case the first wins

/a/b/c/foo
^^^^^^^^^^

.. code-block:: python

    @resource.child('a/{b}/c/{d}')
    @resource.child('a/b/{c}/{d}')
    @resource.child(resource.any)

This has the same number of exact matches but the second has matches higher in
the url hierarchy so number two wins.


/a/foo/c/bar
^^^^^^^^^^^^

.. code-block:: python

    @resource.child('a/{b}/c/{d}')
    @resource.child('a/{b}/{c}')
    @resource.child('a')
    @resource.child(resource.any)

In this case, the first match has more exact matches and so wins.

/a/b/foo/bar
^^^^^^^^^^^^

.. code-block:: python

    @resource.child('a/b/{c}')
    @resource.child('a/b/{c}/{d}')
    @resource.child('a/{b}/{c}')
    @resource.child('a')
    @resource.child(resource.any)

This one is a little more difficult but because we have an exact match on the
number of segments, number 2 wins

Custom Matchers
---------------

You can pass your own matchers to the child method if you like. For instance,
let's process the following search url ``/search/python?u=foo``

.. code-block:: python

    def mymatcher(request, segments):
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
            ...



'Parse it all yourself' matcher
-------------------------------

Sometimes you might want to process all of the segments yourself

.. code-block:: python

    class Root(resource.Resource):

        @resource.child(resource.any)
        def process(self, request, segments):
            if 'blah' in segments[0]:
                return Matched(segments[0]), segments[1:]

The resource.any matcher does nothing and hence will pass all the segments into
the child resource and then it is up to you to do what you will.

You should return do whatever matching you want and then return a resource and
any remaining segments that you haven't used (i.e. that you wish your matched
resource to have available)

Request Handlers
================

At some point, all of the segments will have been consumed. The final resource
is then called in order to get the contents. If this resource is a restish
resource, a series of tests are done to find out which method to use.  Firstly
the request type is used to find out which handler to use. 

The resource class also carries most of our resource decorators and can be used
for url handling or http procesing. Here were are have decorated a method of
our Root resource with a resource.GET().  This tells the resource to use this
method for any GET responses. 


.. note:: Matt: add a bit about resource http handlers

Responses should always be either http response codes or a callable that will
generate a response.

.. note:: Matt: add a bit about http responses

In this case we have returned a http response with a content type of text/html.
Let's take a look at it.

.. code-block:: python

  http.ok( [ ('Content-Type', 'text/html') ], "<p>Hello from myproject!</p>")

The response is a list of tuples, each of which is a http header key and value.
This is followed by the data for the http response.

If we can work out the content type of the returned content from it's accept
header then we don't have to explicitly provide it. e.g.

.. code-block:: python

  http.ok( [], "<p>Hello from myproject!</p>")

Other HTTP Handlers
-------------------

Restish implements resource decorators to handle GET, POST, PUT and DELETE.

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

Resources can perform content negotiation in a few different ways. The example
above where ``GET()`` did not have any arguments accepts any (or no) content type. If we
wanted to explictly return different types of document depending on the accept
headers we can include this as a GET argument.

.. code-block:: python

    @resource.GET(accept='application/json')
    def json(self, request):
        return http.ok([('Content-Type', 'application/json')], "{}")

In this case, if the accept header was application/json, our empty json string
would be returned.

If we had our argument-less GET resource also, then this would act as a
'catch-all' where everything apart from 'application/json' would return html.
e.g.


.. code-block:: python

    @resource.GET()
    def catchall(self, request):
        return http.ok([('Content-Type', 'text/html')], "<strong>I'm HTML</strong>")

    @resource.GET(accept='application/json')
    def json(self, request):
        return http.ok([('Content-Type', 'application/json')], "{}")

We can also use file suffixes and let the mimetypes module work out what
content type to use. e.g. ``html``, ``xml``, ``pdf``. We've also added ``json``
as we think you might (should) be using this one a lot! If you want to respond
to multiple encodings, give it a list (e.g. GET(accept=['html','xml'])

Wildcard content type matching also works. e.g. ``text/*``

.. note:: Content negotiation within restish also honours the clients accept-quality scores. e.g. if a client sends ``text/html;q=0.4,text/plain;q=0.5`` text/plain will be preferred. See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html

We sometimes want to match lists of content types, for example where we would
like to use ``application/xhtml+xml``. This are honoured by restish. (See
test_resource.py in the unit tests for examples)

