# ~*~ coding: utf-8

import unittest

from restish import http, templating


TEST_STRING = "A '£' symbol often breaks web pages.".decode('utf-8')


class RendererTests(object):

    def test_render(self):
        request = http.Request.blank('/', environ={
            'restish.templating.renderer': self.renderer})
        assert templating.render(request, 'whatever') == TEST_STRING

    def test_render_different_encoding(self):
        request = http.Request.blank('/', environ={
            'restish.templating.renderer': self.renderer})
        assert templating.render(request, 'whatever', encoding='iso-8859-1') == TEST_STRING.encode('iso-8859-1')

    def test_element(self):
        @templating.element('whatever')
        def element(element, request):
            return {}
        request = http.Request.blank('/', environ={
            'restish.templating.renderer': self.renderer})
        assert element(None, request) == TEST_STRING

    def test_page(self):
        @templating.page('whatever')
        def page(page, request):
            return {}
        request = http.Request.blank('/', environ={
            'restish.templating.renderer': self.renderer})
        assert page(None, request).body == TEST_STRING.encode('utf-8')


try:
    from restish.contrib import makorenderer
except ImportError:
    pass
else:
    class MockMakoTemplateLookup(object):
        def get_template(self, name):
            return MockMakoTemplate()
    class MockMakoTemplate(object):
        output_encoding = 'utf-8'
        def render(self, **kw):
            return TEST_STRING.encode('utf-8')
        def render_unicode(self, **kw):
            return TEST_STRING
    class MockMakoRenderer(makorenderer.MakoRenderer):
        def __init__(self):
            self.lookup = MockMakoTemplateLookup()
    class TestMakoRenderer(RendererTests, unittest.TestCase):
        renderer = MockMakoRenderer()


try:
    from restish.contrib import jinja2renderer
except ImportError:
    pass
else:
    class MockJinja2Environment(object):
        def get_template(self, name):
            return MockJinja2Template()
    class MockJinja2Template(object):
        def render(self, **kw):
            return TEST_STRING
    class MockJinja2Renderer(jinja2renderer.Jinja2Renderer):
        def __init__(self):
            self.environment = MockJinja2Environment()
    class TestJinja2Renderer(RendererTests, unittest.TestCase):
        renderer = MockJinja2Renderer()


try:
    from restish.contrib import genshirenderer
except ImportError:
    pass
else:
    class MockGenshiTemplateLoader(object):
        def load(self, name):
            return MockGenshiTemplate()
    class MockGenshiTemplate(object):
        def generate(self, **k):
            # I'll pretend to be the stream, too.
            return self
        def render(self, encoding='utf-8'):
            if encoding is None:
                return TEST_STRING
            return TEST_STRING.encode(encoding)
    class MockGenshiRenderer(genshirenderer.GenshiRenderer):
        def __init__(self):
            self.loader = MockGenshiTemplateLoader()
    class TestGenshiRenderer(RendererTests, unittest.TestCase):
        renderer = MockGenshiRenderer()


if __name__ == '__main__':
    unittest.main()

