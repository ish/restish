import unittest
import webtest


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = webtest.TestApp('config:test.ini', relative_to='.')

