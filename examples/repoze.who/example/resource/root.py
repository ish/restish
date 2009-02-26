import logging
from restish import http, resource, templating


log = logging.getLogger(__name__)


class Root(resource.Resource):

    @resource.GET(accept='html')
    @templating.page('root.html')
    def html(self, request):
        return {}

    @resource.child()
    def open(self, request, segments):
        return OpenResource()

    @resource.child()
    def closed(self, request, segments):
        return ClosedResource()


class OpenResource(resource.Resource):

    @resource.GET(accept='html')
    @templating.page('open.html')
    def html(self, request):
        return {}

    @resource.child()
    def another(self, request, segments):
        return AnotherResource('Open')


class ClosedResource(resource.Resource):

    @resource.GET(accept='html')
    @templating.page('closed.html')
    def html(self, request):
        return {}

    @resource.child()
    def another(self, request, segments):
        return AnotherResource('Closed')


class AnotherResource(resource.Resource):

    def __init__(self, child_of):
        self.child_of = child_of

    @resource.GET(accept='html')
    @templating.page('another.html')
    def html(self, request):
        return {'child_of': self.child_of}

