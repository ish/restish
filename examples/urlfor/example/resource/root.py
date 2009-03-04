import logging
from restish import http, resource

from restish.ext.urlfor import *


log = logging.getLogger(__name__)


class ResourceBase(resource.Resource):
    @resource.GET(accept='html')
    def html(self, request):
        def content():
            yield '<h1>%s</h1>' % (self.name,)
            yield '<ul>'
            for cls in [Root, Blog, Blag, Blig]:
                yield '<li><a href="%s">%s</a></li>' % (url_for(request, cls), cls.name)
            yield '</ul>'
        return http.ok([], content())


class Blig(ResourceBase):
    name = 'blig'


class Blag(ResourceBase):
    name = 'blag'
    blig = child('blig', Blig)


class Blog(ResourceBase):
    name = 'blog'
    blag = child('blag', Blag)


class Root(ResourceBase):
    name = 'root'
    blog = child('blog', Blog)

