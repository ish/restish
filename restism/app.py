from restism import http, resource


class RestismApp(object):

    not_found_factory = resource.NotFound

    def __init__(self, root_resource):
        self.root = root_resource

    def __call__(self, environ, start_response):
        request = http.Request(environ)
        resource = self.locate_resource(request)
        response = resource(request)
        start_response(response.status, response.headers)
        return response.content

    def locate_resource(self, request):
        segments = request.path_segments()
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

