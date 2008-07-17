from restism import http, resource


class RootResource(resource.Resource):

    def __call__(self, request):
        return http.ok([('Content-Type', 'text/plain')], "I'm a RootResource!")

    def resource_child(self, request, segments):
        if segments[0] == 'foo':
            return FooResource(), segments[1:]


class FooResource(resource.Resource):

    def __call__(self, request):
        return http.ok([('Content-Type', 'text/html')], "<p>I'm a <strong>FooResource</strong>!</p>")

