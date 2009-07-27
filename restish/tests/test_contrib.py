# ~*~ coding: utf-8

import os.path
import shutil
import tempfile
import unittest
import warnings

from restish import http, templating
from restish.contrib import appurl


class TestApplicationURLAccessor(unittest.TestCase):

    def test_getattr(self):
        class Module(object):
            def news(self, request):
                return request.application_path.child('news')
        app_urls = appurl.ApplicationURLAccessor(http.Request.blank('/'),
                                                 Module())
        self.assertTrue(app_urls.news)
        self.assertEquals(app_urls.news(), '/news')

    def test_args(self):
        class Module(object):
            def args(self, request, foo, bar):
                return request.application_path.child(foo, bar)
        app_urls = appurl.ApplicationURLAccessor(http.Request.blank('/'),
                                                 Module())
        self.assertEquals(app_urls.args('foo', bar='bar'), '/foo/bar')

    def test_private(self):
        class Module(object):
            def _private(self, request):
                return request.application_path.child('_private')
        app_urls = appurl.ApplicationURLAccessor(http.Request.blank('/'),
                                                 Module())
        self.assertRaises(AttributeError, app_urls.__getattr__, '_private')

    def test_all(self):
        class Module(object):
            __all__ = ['public']
            def public(self, request):
                return request.application_path.child('public')
            def private(self, request):
                return request.application_path.child('private')
            def _private(self, request):
                return request.application_path.child('_private')
        app_urls = appurl.ApplicationURLAccessor(http.Request.blank('/'),
                                                 Module())
        self.assertTrue(AttributeError, app_urls.public)
        self.assertRaises(AttributeError, app_urls.__getattr__, 'private')
        self.assertRaises(AttributeError, app_urls.__getattr__, '_private')


class RendererTestMixin(object):
    """
    Mixin class for any templating engine -specific tests we can run (depends on
    imports).

    XXX This is written as a mixin-style thingy to stop the standard unittest
    test collector picking it up as a TestCase.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.add_content('static', "<p>A '£' symbol often breaks web pages.</p>".decode('utf-8'))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def add_content(self, name, content):
        f = file(os.path.join(self.tmpdir, name), 'w')
        f.write(content.encode('utf-8'))
        f.close()

    def content(self, name, encoding=None):
        f = file(os.path.join(self.tmpdir, name))
        content = f.read().decode('utf-8')
        if encoding:
            content = content.encode(encoding)
        f.close()
        return content

    def test_render(self):
        request = http.Request.blank('/', environ={
            'restish.templating': templating.Templating(self.renderer)})
        assert templating.render(request, 'static') == self.content('static')

    def test_render_vars(self):
        request = http.Request.blank('/', environ={
            'restish.templating': templating.Templating(self.renderer)})
        assert templating.render(request, 'dynamic', {'foo': 'bar'}) == '<p>bar</p>'

    def test_render_different_encoding(self):
        request = http.Request.blank('/', environ={
            'restish.templating': templating.Templating(self.renderer)})
        assert templating.render(request, 'static', encoding='iso-8859-1') == self.content('static', 'iso-8859-1')

    def test_element(self):
        @templating.element('static')
        def element(element, request):
            return {}
        request = http.Request.blank('/', environ={
            'restish.templating': templating.Templating(self.renderer)})
        assert element(None, request) == self.content('static')

    def test_page(self):
        @templating.page('static')
        def page(page, request):
            return {}
        request = http.Request.blank('/', environ={
            'restish.templating': templating.Templating(self.renderer)})
        assert page(None, request).body == self.content('static', 'utf-8')


try:
    from restish.contrib import makorenderer
    class TestMakoRenderer(RendererTestMixin, unittest.TestCase):
        def setUp(self):
            super(TestMakoRenderer, self).setUp()
            self.renderer = makorenderer.MakoRenderer(
                directories=self.tmpdir, input_encoding='utf-8')
            self.add_content('dynamic', '<p>${foo}</p>')
except ImportError:
    warnings.warn('Skipping MakoRenderer tests due to missing packages.', RuntimeWarning)


try:
    from restish.contrib import jinja2renderer
    import jinja2
    class TestJinja2Renderer(RendererTestMixin, unittest.TestCase):
        def setUp(self):
            super(TestJinja2Renderer, self).setUp()
            self.renderer = jinja2renderer.Jinja2Renderer(
                loader=jinja2.FileSystemLoader(self.tmpdir))
            self.add_content('dynamic', '<p>{{foo}}</p>')
except ImportError:
    warnings.warn('Skipping Jinja2Renderer tests due to missing packages.', RuntimeWarning)


try:
    from restish.contrib import genshirenderer
    from genshi.template import loader
    class TestGenshiRenderer(RendererTestMixin, unittest.TestCase):
        def setUp(self):
            super(TestGenshiRenderer, self).setUp()
            self.renderer = genshirenderer.GenshiRenderer(
                loader.directory(self.tmpdir))
            self.add_content('dynamic', '<p>${foo}</p>')
except ImportError:
    warnings.warn('Skipping GenshiRenderer tests due to missing packages.', RuntimeWarning)


try:
    from restish.contrib import tempitarenderer
    class TestTempitaRenderer(RendererTestMixin, unittest.TestCase):
        def setUp(self):
            super(TestTempitaRenderer, self).setUp()
            self.renderer = tempitarenderer.TempitaRenderer(
                tempitarenderer.TempitaFileSystemLoader(self.tmpdir))
            self.add_content('dynamic', '<p>{{foo}}</p>')
except ImportError:
    warnings.warn('Skipping TempitaRenderer tests due to missing packages.', RuntimeWarning)


try:
    from restish.contrib import djangorenderer
    from django.conf import settings
    class TestDjangoRenderer(RendererTestMixin, unittest.TestCase):
        def setUp(self):
            super(TestDjangoRenderer, self).setUp()
            self.renderer = djangorenderer.DjangoRenderer()
            self.add_content('dynamic', '<p>{{ foo }}</p>')
            # Configure Django's global config a bit. Yuck, yuck, yuck!
            if not settings.configured:
                settings.configure(
                    TEMPLATE_LOADERS=['django.template.loaders.filesystem.load_template_source'],
                )
            # Configure the per-test settings.
            settings.TEMPLATE_DIRS = [self.tmpdir]
except ImportError:
    warnings.warn('Skipping DjangoRenderer tests due to missing packages.', RuntimeWarning)


if __name__ == '__main__':
    unittest.main()

