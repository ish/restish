import unittest
import webtest

from restish import app, http, resource, page, templating


def make_app(root):
    return webtest.TestApp(app.RestishApp(root))


class TestElement(unittest.TestCase):

    def test_rendering(self):
        def renderer(template, args, encoding=None):
            if template == 'page.html':
                element = args['element']
                return '<div>page.html%s</div>' % (element('foo')(),)
            elif template == 'element.html':
                return '<p>element.html</p>'
        class Element(page.Element):
            @templating.element('element.html')
            def __call__(self, request):
                return {}
        class Page(page.Page):
            @resource.GET()
            @templating.page('page.html')
            def html(self, request):
                return {}
            @page.element('foo')
            def foo(self, request):
                return Element()
        response = make_app(Page()).get('/', extra_environ={'restish.templating': templating.Templating(renderer)}, status=200)
        assert response.body == '<div>page.html<p>element.html</p></div>'

    def test_element_decorator(self):
        class Page(page.Page):
            @page.element('foo')
            def foo(self, request):
                return page.Element()
        request = http.Request.blank('/')
        assert Page().element(request, 'foo') is not None

    def test_dynamic_element(self):
        class Element(page.Element):
            def __init__(self, name):
                self.name = name
        class Page(page.Page):
            def element(self, request, name):
                return Element(name)
        request = http.Request.blank('/')
        assert Page().element(request, 'foo').name == 'foo'
        assert Page().element(request, 'bar').name == 'bar'

    def test_missing_element(self):
        request = http.Request.blank('/')
        self.assertRaises(page.ElementNotFound, page.Page().element, request, 'foo')

    def test_element_caching(self):
        """
        Check that the element is cached for the duration of a request but not
        across requests.
        """
        class Page(page.Page):
            @page.element('foo')
            def foo(self, request):
                return page.Element()
        P = Page()
        # During request
        request = http.Request.blank('/')
        assert P.element(request, 'foo') is P.element(request, 'foo')
        # Across requests
        request1 = http.Request.blank('/')
        request2 = http.Request.blank('/')
        assert P.element(request1, 'foo') is not P.element(request2, 'foo')


if __name__ == '__main__':
    unittest.main()

