import unittest

from restish import http, resource, templating


class TestModule(unittest.TestCase):

    def test_exports(self):
        """
        Test that default rendering methods are available at module scope.
        """
        keys = dir(templating)
        assert 'render' in keys
        assert 'page' in keys
        assert 'element' in keys


class TestRendering(unittest.TestCase):

    def test_args(self):
        """
        Test that common rendering args are correct.
        """
        rendering = templating.Rendering()
        request = http.Request.blank('/')
        args = rendering.args(request)
        assert set(['urls']) == set(args)

    def test_element_args(self):
        """
        Test that element rendering args are correct.
        """
        rendering = templating.Rendering()
        request = http.Request.blank('/')
        args = rendering.element_args(request, None)
        assert set(['urls', 'element']) == set(args)

    def test_page_args(self):
        """
        Test that page rendering args are correct.
        """
        rendering = templating.Rendering()
        request = http.Request.blank('/')
        args = rendering.page_args(request, None)
        assert set(['urls', 'element']) == set(args)

    def test_args_chaining(self):
        """
        Test that an extra common arg is also available to elements and pages.
        """
        class Rendering(templating.Rendering):
            def args(self, request):
                args = super(Rendering, self).args(request)
                args['extra'] = None
                return args
        rendering = Rendering()
        request = http.Request.blank('/')
        assert set(['urls', 'extra']) == set(rendering.args(request))
        assert set(['urls', 'element', 'extra']) == set(rendering.element_args(request, None))
        assert set(['urls', 'element', 'extra']) == set(rendering.element_args(request, None))

    def test_overloading(self):
        class Rendering(templating.Rendering):
            def render(self, request, template, args, encoding=None):
                return repr(args)
            def args(self, request):
                args = super(Rendering, self).args(request)
                args['extra_arg'] = None
                return args
            def element_args(self, request, element):
                args = super(Rendering, self).element_args(request, element)
                args['extra_element_arg'] = None
                return args
            def page_args(self, request, page):
                args = super(Rendering, self).page_args(request, page)
                args['extra_page_arg'] = None
                return args
        rendering = Rendering()
        # Check that the overloaded args are all present.
        args = rendering.args(None)
        element_args = rendering.element_args(None, None)
        page_args = rendering.page_args(None, None)
        for t in [args, element_args, page_args]:
            assert 'extra_arg' in t
        for t in [element_args, page_args]:
            assert 'extra_element_arg' in t
        assert 'extra_page_arg' in page_args
        # Check that the args all get through to the render() method.
        @rendering.page(None)
        def page(page, request):
            return {}
        @rendering.element(None)
        def element(element, request):
            return {}
        for name in ['extra_arg', 'extra_element_arg', 'extra_page_arg']:
            assert name in page(None, None).body
        for name in ['extra_arg', 'extra_element_arg']:
            assert name in element(None, None)

    def test_encoding(self):
        """
        Check that only a rendered page encoded output by default.
        """
        def renderer(template, args, encoding=None):
            return str(encoding)
        @templating.element('element')
        def element(element, request):
            return {}
        @templating.page('page')
        def page(page, request):
            return {}
        request = http.Request.blank('/', environ={'restish.templating.renderer': renderer})
        assert templating.render(request, 'render') == 'None'
        assert element(None, request) == 'None'
        assert page(None, request).body == 'utf-8'


class TestPage(unittest.TestCase):

    def test_page_decorator(self):
        def renderer(template, args, encoding=None):
            args.pop('urls')
            args.pop('element')
            return '<p>%s %r</p>' % (template, args)
        class Resource(resource.Resource):
            def __init__(self, args):
                self.args = args
            @resource.GET()
            @templating.page('test.html')
            def html(self, request):
                return self.args
        environ = {'restish.templating.renderer': renderer}
        request = http.Request.blank('/', environ=environ)
        response = Resource({})(request)
        assert response.status.startswith('200')
        assert response.body == '<p>test.html {}</p>'
        response = Resource({'foo': 'bar'})(request)
        assert response.status.startswith('200')
        assert response.body == '<p>test.html {\'foo\': \'bar\'}</p>'


if __name__ == '__main__':
    unittest.main()

