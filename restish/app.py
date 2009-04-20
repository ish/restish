"""
Core wsgi application
"""
from restish import error, http, url


class RestishApp(object):

    def __init__(self, root_resource):
        self.root = root_resource

    def __call__(self, environ, start_response):
        # Create a request object.
        request = http.Request(environ)
        try:
            # Locate the resource and convert it to a response.
            resource_or_response = self.locate_resource(request)
            response = self.get_response(request, resource_or_response)
        except error.HTTPError, e:
            response = e.make_response()
        # Send the response to the WSGI parent.
        start_response(response.status, response.headerlist)
        return response.app_iter

    def locate_resource(self, request):
        """
        Locate the resource at the path in request URL by traversing the
        resource hierarchy.
        """
        # Calculate the path segments relative to the application,
        # special-casing requests for the the root segment (because we already
        # have a reference to the root resource).
        segments = url.split_path(request.environ['PATH_INFO'])
        if segments == ['']:
            segments = []
        # Recurse into the resource hierarchy until we run out of segments or
        # find a Response.
        resource = self.root
        while segments and not isinstance(resource, http.Response):
            resource_child = getattr(resource, 'resource_child', None)
            # No resource_child method? 404.
            if resource_child is None:
                raise http.NotFoundError()
            result = resource_child(request, segments)
            # No result returned? 404.
            if result is None:
                raise http.NotFoundError()
            # Either a (resource, remaining segments) tuple or an object to
            # forward the lookup to is acceptable.
            if isinstance(result, tuple):
                resource, segments = result
            else:
                resource = result
        return resource

    def get_response(self, request, resource_or_response):
        """
        Resolve the resource/response until we get a response.

        The resource_or_response arg may be either an http.Response instance or
        a callable resource. A callable resource may return another callable to
        use in its place.
        """
        while not isinstance(resource_or_response, http.Response):
            resource_or_response = resource_or_response(request)
        return resource_or_response

