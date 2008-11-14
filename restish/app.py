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
            response = self.call_resource(request, resource)
        except error.HTTPClientError, e:
            response = e.make_response()
        # Send the response to the WSGI parent.
        start_response(response.status, response.headerlist)
        return response.body

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
            resource_child = getattr(resource, "resource_child", None)
            if resource_child is not None:
                resource, segments = resource_child(request, segments)
            else:
                resource = None
            if resource is None:
                return self.not_found_factory()
        return resource

    def call_resource(self, request, the_resource):
        # Recursively call the resource to get a response. A resource is
        # allowed to return another resource to be used in its place.
        while True:
            response = the_resource(request)
            if not isinstance(response, resource.Resource):
                break
            the_resource = response
        return response

