from restism import http


class Resource(object):

    def __init__(self):
        pass

    def resource_child(self, request, segments):
        return None, segments

    def __call__(self, request):
        return None


class NotFound(Resource):

    def __call__(self, request):
        return http.not_found([], "404")

