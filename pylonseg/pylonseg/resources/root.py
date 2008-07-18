from restish import http, resource, templating


class RootResource(resource.Resource):

    def __call__(self, request):
        return http.ok([('Content-Type', 'text/html')], templating.render(
            request, 'root.html', args={'message': "I'm a RootResource"}))

    def resource_child(self, request, segments):
        if segments[0] == 'foo':
            return FooResource(), segments[1:]
        elif segments[0] == 'bang-bang':
            bang
        elif segments[0] == 'bang':
            def f(request):
                bang
            return f, segments[1:]
        return None, segments


class FooResource(resource.Resource):

    def __call__(self, request):
        return http.ok([('Content-Type', 'text/html')], "<p>I'm a <strong>FooResource</strong>!</p>")

