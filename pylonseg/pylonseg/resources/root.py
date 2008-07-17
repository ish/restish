from restism import http, resource


class RootResource(resource.Resource):

    def __call__(self, request):
        return http.ok([('Content-Type', 'text/plain')], 'Yay!')

