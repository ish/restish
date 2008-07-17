from restism import app, http, resource, pattern


class Foo(resource.Resource):

    def __call__(self, request):
        return http.ok([], "I'm a foo!")


class Resource(resource.Resource):

    def __init__(self, segments=[]):
        self.segments = segments

    def resource_child(self, request, segments):
        if segments[0] == "foo":
            return Foo(), segments[1:]
        return Resource(self.segments + [segments[0]]), segments[1:]

    def __call__(self, request):
        return http.ok([], repr(self.segments))


def root_func(request):
    return http.ok([], "Yay!")


root = Resource([])
app = app.RestismApp(root)

