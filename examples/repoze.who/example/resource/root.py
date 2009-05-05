import logging
from restish import http, page, resource, templating

from example import who
from example.lib import guard


log = logging.getLogger(__name__)


class Root(page.Page):

    @resource.child()
    def login(self, request, segments):
        return Login()

    @resource.child()
    @guard.guard(guard.authenticated)
    def secret(self, request, segments):
        return Secret()

    @resource.GET()
    @templating.page('root.html')
    def html(self, request):
        return {}


class Secret(page.Page):

    @resource.GET()
    @templating.page('secret.html')
    def html(self, request):
        return {}


class Login(page.Page):

    @resource.GET()
    @templating.page('login.html')
    def html(self, request):
        return {'came_from': request.GET.get('came_from')}

