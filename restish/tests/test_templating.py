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
            def render(self, request, template, args):
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


class TestPage(unittest.TestCase):

    def test_page_decorator(self):
        def renderer(template, args):
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


OUTPUT_DOC = """<div><p>urls.path_qs: /</p><p>&lt;strong&gt;unsafe&lt;/strong&gt;</p><p><strong>safe</strong></p></div>"""


class _TemplatingEngineTestCase(unittest.TestCase):

    renderer = None

    def test_templating(self):
        environ = {'restish.templating.renderer': self.renderer}
        request = http.Request.blank('/', environ=environ)
        doc = templating.render(request, 'who-cares.html', {
            'unsafe': '<strong>unsafe</strong>',
            'safe': '<strong>safe</strong>',
            })
        print doc
        assert doc == OUTPUT_DOC


try:
    import mako.template
    class TestMako(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = mako.template.Template("""<div><p>urls.path_qs: ${urls.path_qs|h}</p><p>${unsafe|h}</p><p>${safe}</p></div>""")
            return template.render(**args)
    class TestMakoAutoEscape(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = mako.template.Template("""<div><p>urls.path_qs: ${urls.path_qs}</p><p>${unsafe}</p><p>${safe|n}</p></div>""", default_filters=['h'])
            return template.render(**args)
except ImportError:
    print "Skipping Mako tests"


try:
    import genshi.template
    class TestGenshi(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = genshi.template.MarkupTemplate("""<div><p>urls.path_qs: ${urls.path_qs}</p><p>${unsafe}</p><p>${Markup(safe)}</p></div>""")
            return template.generate(**args).render('html')
except ImportError:
    print "Skipping Genshi tests"


try:
    import jinja2
    class TestJinja2(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = jinja2.Template("""<div><p>urls.path_qs: {{ urls.path_qs|e }}</p><p>{{ unsafe|e }}</p><p>{{ safe }}</p></div>""")
            return template.render(**args)
    class TestJinja2AutoEscape(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = jinja2.Template("""<div><p>urls.path_qs: {{ urls.path_qs }}</p><p>{{ unsafe }}</p><p>{{ safe|safe }}</p></div>""", autoescape=True)
            return template.render(**args)
except ImportError:
    print "Skipping Jinja2 tests"


if __name__ == '__main__':
    unittest.main()

