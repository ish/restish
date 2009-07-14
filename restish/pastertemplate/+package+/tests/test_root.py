import unittest
import webtest


class TestRoot(unittest.TestCase):

    def test_get(self):
        app = webtest.TestApp('config:test.ini', relative_to='.')
        app.get('/')

