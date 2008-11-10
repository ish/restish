import unittest
from webob import Request

from restish import templating


class TestModule(unittest.TestCase):

    def test_exports(self):
        """
        Test that default rendering methods are available at module scope.
        """
        keys = dir(templating)
        assert 'render' in keys
        assert 'page' in keys
        assert 'element' in keys


class TestRenderingArgs(unittest.TestCase):

    def test_args(self):
        """
        Test that common rendering args are correct.
        """
        rendering = templating.Rendering()
        request = Request.blank('/')
        args = rendering.args(request)
        assert set(['url']) == set(args)

    def test_element_args(self):
        """
        Test that element rendering args are correct.
        """
        rendering = templating.Rendering()
        request = Request.blank('/')
        args = rendering.element_args(request, None)
        assert set(['url', 'element']) == set(args)

    def test_page_args(self):
        """
        Test that page rendering args are correct.
        """
        rendering = templating.Rendering()
        request = Request.blank('/')
        args = rendering.page_args(request, None)
        assert set(['url', 'element']) == set(args)

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
        request = Request.blank('/')
        assert set(['url', 'extra']) == set(rendering.args(request))
        assert set(['url', 'element', 'extra']) == set(rendering.element_args(request, None))
        assert set(['url', 'element', 'extra']) == set(rendering.element_args(request, None))


if __name__ == '__main__':
    unittest.main()

