from restish import error, http, resource


class RestishApp(object):

    not_found_factory = resource.NotFound

    def __init__(self, root_resource):
        self.root = root_resource

    def __call__(self, environ, start_response):
        # Create a request object.
        request = http.Request(environ)
        try:
            # Locate the resource.
            resource = self.locate_resource(request)
            # Call the resource to render the page.
            response = self.get_response(request, resource)
        except error.HTTPClientError, e:
            response = e.make_response()
        # Send the response to the WSGI parent.
        start_response(response.status, response.headerlist)
        return response.app_iter

    def locate_resource(self, request):
        # Calculate the path segments relative to the application,
        # special-casing requests for the the root segment (because we already
        # have a reference to the root resource).
        segments = request.path_url.path_segments[len(request.application_url.path_segments):]
        if segments == ['']:
            segments = []
        # Recurse into the resource hierarchy until we run out of segments.
        resource = self.root
        while segments:
            resource_child = getattr(resource, 'resource_child', None)
            if resource_child is None:
                resource = None
            else:
                result = resource_child(request, segments)
                if isinstance(result, tuple):
                    # Result is a tuple of (resource, remaining segments).
                    resource, segments = result
                else:
                    # Result is another resource (probably).
                    resource = result
            if resource is None:
                return self.not_found_factory()
        return resource

    def get_response(self, request, resource):
        """
        Recursively call the resource until we get a response.
        
        A resource is allowed to return another resource to be used in its
        place. This method handles the recursive calling.
        """
        while True:
            response = resource(request)
            if isinstance(response, http.Response):
                break
            resource = response
        return response

