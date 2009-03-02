"""
A typical application has a set of fixed or canonical URLs for its resources.
ApplicationURLAccessor is designed to be added as a templating arg and will
expose all "public" URL creation functions in a module. 

The intended use is to define a module in your application that provides
functions to build a canonical URLs. The functions can be as simple or as
complex as necessary.

    def news(request):
        return request.application_path.child('news')

    def news_item(request, id):
        return news(request).child(str(id))


The functions can obviously be used directly from an application's resource
code. By adding an ApplicationURLAccessor to the Templating args the same
functions can also be made easily available to templates.

    from somepackage import urls

    class Templating(templating.Templating):
        def args(self, request):
            args = super(Templating, self).args(request)
            args['app_urls'] = ApplicationURLAccessor(request, urls)
            return args


Since the request is bound to the call (templates don't have access to the
request by default anyway) the template does not need to pass a request to the
function, e.g.
                                        
    <a href="{{app_urls.news_item(3)}}">News item #3</a>.

"""


class ApplicationURLAccessor(object):
    """
    Expose a module of URL factory functions as partial functions with the
    request bound to the call.

    Every "public" function in the module will be available as a partial that
    will call the original function with the request as the first positional
    arg.  Any additional args will be passed through as-is.

    A "public" function is any function that:

        * does not start with _ (an underscore),
        * is listed in the module's __all__, if present.
    """

    def __init__(self, request, module):
        self.request = request
        self.module = module

    def __getattr__(self, name):
        # Don't call functions that begin with an underscore.
        if name.startswith('_'):
            raise AttributeError()
        # Don't call functions not explicitly listed in __all__ if present.
        all = getattr(self.module, '__all__', None)
        if all is not None and name not in all:
            raise AttributeError()
        # Return a partial function that will call the original function with
        # the request as the 1st positional arg.
        func = getattr(self.module, name)
        return lambda *args, **kwargs: func(self.request, *args, **kwargs)

