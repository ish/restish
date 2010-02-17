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


class TestArgs(unittest.TestCase):

    def test_args(self):
        """
        Test that common rendering args are correct.
        """
        T = templating.Templating(None)
        request = http.Request.blank('/')
        args = T.args(request)
        assert set(['urls']) == set(args)

    def test_element_args(self):
        """
        Test that element rendering args are correct.
        """
        T = templating.Templating(None)
        request = http.Request.blank('/')
        args = T.element_args(request, None)
        assert set(['urls', 'element']) == set(args)

    def test_page_args(self):
        """
        Test that page rendering args are correct.
        """
        T = templating.Templating(None)
        request = http.Request.blank('/')
        args = T.page_args(request, None)
        assert set(['urls', 'element']) == set(args)

    def test_args_chaining(self):
        """
        Test that an extra common arg is also available to elements and pages.
        """
        class Templating(templating.Templating):
            def args(self, request):
                args = super(Templating, self).args(request)
                args['extra'] = None
                return args
        T = Templating(None)
        request = http.Request.blank('/')
        assert set(['urls', 'extra']) == set(T.args(request))
        assert set(['urls', 'element', 'extra']) == set(T.element_args(request, None))
        assert set(['urls', 'element', 'extra']) == set(T.element_args(request, None))

    def test_overloading(self):
        class Templating(templating.Templating):
            def render(self, request, template, args=None, encoding=None):
                return repr(args)
            def args(self, request):
                args = super(Templating, self).args(request)
                args['extra_arg'] = None
                return args
            def element_args(self, request, element):
                args = super(Templating, self).element_args(request, element)
                args['extra_element_arg'] = None
                return args
            def page_args(self, request, page):
                args = super(Templating, self).page_args(request, page)
                args['extra_page_arg'] = None
                return args
        T = Templating(None)
        # Check that the overloaded args are all present.
        args = T.args(None)
        element_args = T.element_args(None, None)
        page_args = T.page_args(None, None)
        for t in [args, element_args, page_args]:
            assert 'extra_arg' in t
        for t in [element_args, page_args]:
            assert 'extra_element_arg' in t
        assert 'extra_page_arg' in page_args
        # Check that the args all get through to the render() method.
        @templating.page(None)
        def page(page, request):
            return {}
        @templating.element(None)
        def element(element, request):
            return {}
        request = http.Request.blank('/', environ={'restish.templating': T})
        for name in ['extra_arg', 'extra_element_arg', 'extra_page_arg']:
            assert name in page(None, request).body
        for name in ['extra_arg', 'extra_element_arg']:
            assert name in element(None, request)


class TestRendering(unittest.TestCase):

    def test_unconfigured(self):
        try:
            templating.Templating(None).render(http.Request.blank('/'),
                                               'foo.html')
        except TypeError, e:
            assert 'renderer' in unicode(e)

    def test_render(self):
        def renderer(template, args, encoding=None):
            return "%s %r" % (template, sorted(args))
        request = http.Request.blank('/', environ={'restish.templating': templating.Templating(renderer)})
        assert templating.render(request, 'render') == "render ['urls']"

    def test_render_element(self):
        def renderer(template, args, encoding=None):
            return "%s %r" % (template, sorted(args))
        request = http.Request.blank('/', environ={'restish.templating': templating.Templating(renderer)})
        assert templating.render_element(request, None, 'element') == "element ['element', 'urls']"

    def test_render_page(self):
        def renderer(template, args, encoding=None):
            return "%s %r" % (template, sorted(args))
        request = http.Request.blank('/', environ={'restish.templating': templating.Templating(renderer)})
        assert templating.render_page(request, None, 'page') == "page ['element', 'urls']"

    def test_render_response(self):
        def renderer(template, args, encoding=None):
            return "%s %r" % (template, sorted(args))
        request = http.Request.blank('/', environ={'restish.templating': templating.Templating(renderer)})
        response = templating.render_response(request, None, 'page')
        assert response.status == "200 OK"
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert response.body == "page ['element', 'urls']"

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
        request = http.Request.blank('/', environ={'restish.templating': templating.Templating(renderer)})
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
        environ = {'restish.templating': templating.Templating(renderer)}
        request = http.Request.blank('/', environ=environ)
        response = Resource({})(request)
        assert response.status.startswith('200')
        assert response.body == '<p>test.html {}</p>'
        response = Resource({'foo': 'bar'})(request)
        assert response.status.startswith('200')
        assert response.body == '<p>test.html {\'foo\': \'bar\'}</p>'
    
    def test_page_decorator_with_custom_headers(self):
        def renderer(template, args, encoding=None):
            return args['body']
        
        class Resource(resource.Resource):
            @resource.GET()
            @templating.page('page')
            def get(self, request):
                # See this link for the following use case:
                # http://sites.google.com/a/snaplog.com/wiki/short_url
                return [('Link', '<http://sho.rt/1>; rel=shorturl'),
                        ('X-Foo', 'Bar')], \
                       {'body': 'Hello World!'}

        environ = {'restish.templating': templating.Templating(renderer)}
        request = http.Request.blank('/', environ=environ)
        response = Resource()(request)
        assert response.status.startswith('200')
        assert response.body == 'Hello World!'
        assert response.headers.get('Link') == '<http://sho.rt/1>; rel=shorturl'
        assert response.headers.get('X-Foo') == 'Bar'


if __name__ == '__main__':
    unittest.main()

