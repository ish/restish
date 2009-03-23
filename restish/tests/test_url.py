# -*- coding: utf-8

# Copyright (c) 2004-2007 Divmod.
# See LICENSE for details.

import unittest

from restish import http, url

POUND = '£'.decode('utf-8')

theurl = "http://www.foo.com:80/a/nice/path/?zot=23&zut"

# RFC1808 relative tests. Not all of these pass yet.
rfc1808_relative_link_base='http://a/b/c/d;p?q#f'
rfc1808_relative_link_tests = [
    # "Normal"
    ('g:h', 'g:h'),
    ('g', 'http://a/b/c/g'),
    ('./g', 'http://a/b/c/g'),
    ('g/', 'http://a/b/c/g/'),
    ('/g', 'http://a/g'),
    ('//g', 'http://g'),
    ('?y', 'http://a/b/c/d;p?y'),
    ('g?y', 'http://a/b/c/g?y'),
    ('g?y/./x', 'http://a/b/c/g?y/./x'),
    ('#s', 'http://a/b/c/d;p?q#s'),
    ('g#s', 'http://a/b/c/g#s'),
    ('g#s/./x', 'http://a/b/c/g#s/./x'),
    ('g?y#s', 'http://a/b/c/g?y#s'),
    #(';x', 'http://a/b/c/d;x'),
    ('g;x', 'http://a/b/c/g;x'),
    ('g;x?y#s', 'http://a/b/c/g;x?y#s'),
    ('.', 'http://a/b/c/'),
    ('./', 'http://a/b/c/'),
    ('..', 'http://a/b/'),
    ('../', 'http://a/b/'),
    ('../g', 'http://a/b/g'),
    #('../..', 'http://a/'),
    #('../../', 'http://a/'),
    ('../../g', 'http://a/g'),

    # "Abnormal"
    ('', 'http://a/b/c/d;p?q#f'),
    #('../../../g', 'http://a/../g'),
    #('../../../../g', 'http://a/../../g'),
    #('/./g', 'http://a/./g'),
    #('/../g', 'http://a/../g'),
    ('g.', 'http://a/b/c/g.'),
    ('.g', 'http://a/b/c/.g'),
    ('g..', 'http://a/b/c/g..'),
    ('..g', 'http://a/b/c/..g'),
    ('./../g', 'http://a/b/g'),
    ('./g/.', 'http://a/b/c/g/'),
    ('g/./h', 'http://a/b/c/g/h'),
    ('g/../h', 'http://a/b/c/h'),
    #('http:g', 'http:g'),          # Not sure whether the spec means
    #('http:', 'http:'),            # these two are valid tests or not.
    ]


class TestUtils(unittest.TestCase):

    def test_split_path(self):
        self.assertEquals(url.split_path(''), [])
        self.assertEquals(url.split_path('/'), [''])
        self.assertEquals(url.split_path('//'), ['', ''])
        self.assertEquals(url.split_path('/foo'), ['foo'])
        self.assertEquals(url.split_path('/foo/bar'), ['foo', 'bar'])
        self.assertEquals(url.split_path('/%2F'), ['/'])
        self.assertEquals(url.split_path('/%C2%A3'), [POUND])

    def test_join_path(self):
        self.assertEquals(url.join_path([]), '')
        self.assertEquals(url.join_path(['']), '/')
        self.assertEquals(url.join_path(['', '']), '//')
        self.assertEquals(url.join_path(['foo']), '/foo')
        self.assertEquals(url.join_path(['foo', 'bar']), '/foo/bar')
        self.assertEquals(url.join_path(['/']), '/%2F')
        self.assertEquals(url.join_path([POUND]), '/%C2%A3')

    def test_split_query(self):
        self.assertEquals(url.split_query(''), [])
        self.assertEquals(url.split_query('a=1&b=2'), [('a', '1'), ('b', '2')])
        self.assertEquals(url.split_query('a&b=2'), [('a', None), ('b', '2')])
        self.assertEquals(url.split_query('a'), [('a', None)])
        self.assertEquals(url.split_query('=1'), [('', '1')])
        self.assertEquals(url.split_query('a=1=2'), [('a', '1=2')])
        self.assertEquals(url.split_query('a=%3F'), [('a', '?')])
        self.assertEquals(url.split_query('%C2%A3=%C2%A3'), [(POUND, POUND)])

    def test_join_query(self):
        self.assertEquals(url.join_query([]), '')
        self.assertEquals(url.join_query([('a', '1')]), 'a=1')
        self.assertEquals(url.join_query([('a', '1'), ('b', '2')]), 'a=1&b=2')
        self.assertEquals(url.join_query([('a', None)]), 'a')
        self.assertEquals(url.join_query([('', '1')]), '=1')
        self.assertEquals(url.join_query([('a', '==1')]), 'a===1')
        self.assertEquals(url.join_query([('a', '?')]), 'a=%3F')
        self.assertEquals(url.join_query([(POUND, POUND)]), '%C2%A3=%C2%A3')


class TestURL(unittest.TestCase):

    def test_properties(self):
        u = url.URL("http://localhost:1234/a/b/c?d&e=f#g")
        self.assertEquals(u.scheme, 'http')
        self.assertEquals(u.netloc, 'localhost:1234')
        self.assertEquals(u.path, '/a/b/c')
        self.assertEquals(u.path_segments, ['a', 'b', 'c'])
        self.assertEquals(u.query, 'd&e=f')
        self.assertEquals(u.query_list, [('d', None), ('e', 'f')])
        self.assertEquals(u.fragment, 'g')

    def test_roundtrip(self):
        tests = (
            "http://localhost",
            "http://localhost/",
            "http://localhost/foo",
            "http://localhost/foo/",
            "http://localhost/foo!!bar/",
            "http://localhost/foo%20bar/",
            "http://localhost/foo%2Fbar/",
            "http://localhost/foo?n",
            "http://localhost/foo?n=v",
            "http://localhost/foo?n=%2Fa%2Fb",
            "http://example.com/foo!%40%24bar?b!%40z=123",
            "http://localhost/asd?a=asd%20sdf%2F345",
            "http://localhost/#%7F",
            )
        for test in tests:
            result = url.URL(test)
            self.assertEquals(test, result)


    def test_equality(self):
        urlpath = url.URL(theurl)
        self.failUnlessEqual(urlpath, url.URL(theurl))
        self.failIfEqual(urlpath, url.URL('ftp://www.anotherinvaliddomain.com/foo/bar/baz/?zot=21&zut'))


    def test_fragmentEquality(self):
        """
        An URL created with the empty string for a fragment compares equal
        to an URL created with C{None} for a fragment.
        """
        self.assertEqual(url.URL('http://localhost:1234/#'), url.URL('http://localhost:1234/'))


    def test_query_equality(self):
        self.assertEqual(url.URL('http://localhost/?'), url.URL('http://localhost/'))


    def test_parent(self):
        urlpath = url.URL(theurl)
        self.assertEquals("http://www.foo.com:80/a/nice/path",
                          urlpath.parent())
        self.assertEquals(url.URL('http://localhost/').parent(), 'http://localhost')
        self.assertRaises(IndexError, url.URL('http://localhost').parent)


    def test_path(self):
        """
        L{URL.path} should be a C{str} giving the I{path} portion of the URL
        only.  Certain bytes should not be quoted.
        """
        urlpath = url.URL("http://example.com/foo/bar?baz=quux#foobar")
        self.assertEqual(urlpath.path, "/foo/bar")
        urlpath = url.URL("http://example.com/foo%2Fbar?baz=quux#foobar")
        self.assertEqual(urlpath.path, "/foo%2Fbar")
        urlpath = url.URL("http://example.com/-_.!*'()?baz=quux#foo")
        self.assertEqual(urlpath.path, "/-_.!*'()")

    def test_path_url(self):
        """
        Test that URL.path is, itself, a URL.
        """
        self.assertTrue(isinstance(url.URL('http://localhost/a/b').path, url.URL))
        self.assertEquals(url.URL('http://localhost/a/b').path.child('c'), '/a/b/c')

    def test_root(self):
        self.assertEqual(url.URL("http://example.com/foo/barr").root(), "http://example.com/")

    def test_child(self):
        urlpath = url.URL(theurl)
        self.assertEquals("http://www.foo.com:80/a/nice/path/gong",
                          urlpath.child('gong'))
        self.assertEquals("http://www.foo.com:80/a/nice/path/gong%2F",
                          urlpath.child('gong/'))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/gong%2Fdouble",
            urlpath.child('gong/double'))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/gong%2Fdouble%2F",
            urlpath.child('gong/double/'))

    def test_childs(self):
        self.assertEquals(url.URL('http://localhost/foo').child('bar'), 'http://localhost/foo/bar')
        self.assertEquals(url.URL('http://localhost/foo').child('bar', 'woo'), 'http://localhost/foo/bar/woo')
        self.assertEquals(url.URL('http://localhost/').child('foo', 'bar'), 'http://localhost/foo/bar')
        self.assertEquals(url.URL('http://localhost').child('foo', 'bar'), 'http://localhost/foo/bar')

    def test_child_init_tuple(self):
        self.assertEquals(
            "http://www.foo.com/a/b/c",
            url.URL("http://www.foo.com/a/b").child("c"))

    def test_child_init_root(self):
        self.assertEquals(
            "http://www.foo.com/c",
            url.URL("http://www.foo.com").child("c"))

    def test_sibling(self):
        urlpath = url.URL(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/sister",
            urlpath.sibling('sister'))
        # use an url without trailing '/' to check child removal
        theurl2 = "http://www.foo.com:80/a/nice/path?zot=23&zut"
        urlpath = url.URL(theurl2)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/sister",
            urlpath.sibling('sister'))


    def test_click(self):
        urlpath = url.URL(theurl)
        # a null uri should be valid (return here)
        self.assertEquals("http://www.foo.com:80/a/nice/path/?zot=23&zut",
                          urlpath.click(""))
        # a simple relative path remove the query
        self.assertEquals("http://www.foo.com:80/a/nice/path/click",
                          urlpath.click("click"))
        # an absolute path replace path and query
        self.assertEquals("http://www.foo.com:80/click",
                          urlpath.click("/click"))
        # replace just the query
        self.assertEquals("http://www.foo.com:80/a/nice/path/?burp",
                          urlpath.click("?burp"))

        # from a url with no query clicking a url with a query,
        # the query should be handled properly
        u = url.URL('http://www.foo.com:80/me/noquery')
        self.failUnlessEqual('http://www.foo.com:80/me/17?spam=158',
                             u.click('/me/17?spam=158'))

        # Clicking on a fragment URL keeps all other parts of the current URL.
        self.assertEquals(url.URL("http://www.foo.com:80/click?a=b").click('#frag'), "http://www.foo.com:80/click?a=b#frag")

        # Clicking on a fragment URL discards the current fragment.
        self.assertEquals(url.URL("http://www.foo.com:80/click#foo").click('#bar'), "http://www.foo.com:80/click#bar")

        # Check that everything from the path onward is removed when the click link
        # has no path.
        u = url.URL('http://localhost/foo?abc=def')
        self.failUnlessEqual(u.click('http://www.python.org'), 'http://www.python.org')


    def test_cloneUnchanged(self):
        """
        Verify that L{url.URL.cloneURL} doesn't change any of the arguments it
        is passed.
        """
        urlpath = url.URL('https://x:1/y?z=1#A')
        self.assertEqual(
            urlpath.clone(scheme=urlpath.scheme, netloc=urlpath.netloc,
                path=urlpath.path, query=urlpath.query, fragment=urlpath.fragment),
            urlpath)


    def test_clickCollapse(self):
        tests = [
            ['http://localhost/', '.', 'http://localhost/'],
            ['http://localhost/', '..', 'http://localhost/'],
            ['http://localhost/a/b/c', '.', 'http://localhost/a/b/'],
            ['http://localhost/a/b/c', '..', 'http://localhost/a/'],
            ['http://localhost/a/b/c', './d/e', 'http://localhost/a/b/d/e'],
            ['http://localhost/a/b/c', '../d/e', 'http://localhost/a/d/e'],
            ['http://localhost/a/b/c', '/./d/e', 'http://localhost/d/e'],
            ['http://localhost/a/b/c', '/../d/e', 'http://localhost/d/e'],
            ['http://localhost/a/b/c/', '../../d/e/', 'http://localhost/a/d/e/'],
            ['http://localhost/a/./c', '../d/e', 'http://localhost/d/e'],
            ['http://localhost/a/./c/', '../d/e', 'http://localhost/a/d/e'],
            ['http://localhost/a/b/c/d', './e/../f/../g', 'http://localhost/a/b/c/g'],
            ['http://localhost/a/b/c', 'd//e', 'http://localhost/a/b/d//e'],
            ]
        for start, click, result in tests:
            self.assertEquals(
                url.URL(start).click(click),
                result
                )

    def test_add_query(self):
        urlpath = url.URL(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp",
            urlpath.add_query("burp"))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp=xxx",
            urlpath.add_query("burp", "xxx"))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp=xxx&zing",
            urlpath.add_query("burp", "xxx").add_query("zing"))
        # note the inversion!
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&zing&burp=xxx",
            urlpath.add_query("zing").add_query("burp", "xxx"))
        # note the two values for the same name
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp=xxx&zot=32",
            urlpath.add_query("burp", "xxx").add_query("zot", 32))

    def test_add_noquery(self):
        # from_string is a different code path, test them both
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?foo=bar",
            url.URL("http://www.foo.com:80/a/nice/path/")
                .add_query("foo", "bar"))
        self.assertEquals(
            "http://www.foo.com?foo=bar",
            url.URL("http://www.foo.com").add_query("foo", "bar"))

    def test_add_queries(self):
        U = url.URL("http://localhost/")
        self.assertEquals(U.add_queries([('a', 'b'), ('c', 'd')]), "http://localhost/?a=b&c=d")

    def test_remove_query(self):
        U = url.URL("http://localhost/foo?a=b&c=d")
        self.assertEquals(U.remove_query('a'), "http://localhost/foo?c=d")

    def test_replace_query(self):
        urlpath = url.URL(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=32&zut",
            urlpath.replace_query("zot", 32))
        # replace name without value with name/value and vice-versa
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot&zut=itworked",
            urlpath.replace_query("zot").replace_query("zut", "itworked"))
        # Q: what happens when the query has two values and we replace?
        # A: we replace both values with a single one
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=32&zut",
            urlpath.add_query("zot", "xxx").replace_query("zot", 32))

    def test_fragment(self):
        urlpath = url.URL(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut#hiboy",
            urlpath.anchor("hiboy"))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut",
            urlpath.anchor())
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut",
            urlpath.anchor(''))

    def test_clear_queries(self):
        urlpath = url.URL(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zut",
            urlpath.clear_queries("zot"))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23",
            urlpath.clear_queries("zut"))
        # something stranger, query with two values, both should get cleared
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zut",
            urlpath.add_query("zot", 1971).clear_queries("zot"))
        # two ways to clear the whole query
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/",
            urlpath.clear_queries("zut").clear_queries("zot"))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/",
            urlpath.clear_queries())

    def test_secure(self):
        self.assertEquals(url.URL('http://localhost/').secure(), 'https://localhost/')
        self.assertEquals(url.URL('http://localhost/').secure(True), 'https://localhost/')
        self.assertEquals(url.URL('https://localhost/').secure(), 'https://localhost/')
        self.assertEquals(url.URL('https://localhost/').secure(False), 'http://localhost/')
        self.assertEquals(url.URL('http://localhost/').secure(False), 'http://localhost/')
        self.assertEquals(url.URL('http://localhost/foo').secure(), 'https://localhost/foo')
        self.assertEquals(url.URL('http://localhost/foo?bar=1').secure(), 'https://localhost/foo?bar=1')
        self.assertEquals(url.URL('http://localhost/').secure(port=443), 'https://localhost/')
        self.assertEquals(url.URL('http://localhost:8080/').secure(port=8443), 'https://localhost:8443/')
        self.assertEquals(url.URL('https://localhost:8443/').secure(False, 8080), 'http://localhost:8080/')


    def test_eq_same(self):
        u = url.URL('http://localhost/')
        self.failUnless(u == u, "%r != itself" % u)

    def test_eq_similar(self):
        u1 = url.URL('http://localhost/')
        u2 = url.URL('http://localhost/')
        self.failUnless(u1 == u2, "%r != %r" % (u1, u2))

    def test_eq_different(self):
        u1 = url.URL('http://localhost/a')
        u2 = url.URL('http://localhost/b')
        self.failIf(u1 == u2, "%r != %r" % (u1, u2))

    def test_eq_apples_vs_oranges(self):
        u = url.URL('http://localhost/')
        self.failIf(u == 42, "URL must not equal a number.")
        self.failIf(u == object(), "URL must not equal an object.")

    def test_ne_same(self):
        u = url.URL('http://localhost/')
        self.failIf(u != u, "%r == itself" % u)

    def test_ne_similar(self):
        u1 = url.URL('http://localhost/')
        u2 = url.URL('http://localhost/')
        self.failIf(u1 != u2, "%r == %r" % (u1, u2))

    def test_ne_different(self):
        u1 = url.URL('http://localhost/a')
        u2 = url.URL('http://localhost/b')
        self.failUnless(u1 != u2, "%r == %r" % (u1, u2))

    def test_ne_apples_vs_oranges(self):
        u = url.URL('http://localhost/')
        self.failUnless(u != 42, "URL must differ from a number.")
        self.failUnless(u != object(), "URL must be differ from an object.")

    def test_parseEqualInParamValue(self):
        S = 'http://localhost/?=x=x=x'
        u = url.URL(S)
        self.failUnless(u.query == '=x=x=x')
        self.failUnless(u.query_list == [('', 'x=x=x')])
        self.failUnless(u == S)
        self.failUnless(u.clone() == S)
        S = 'http://localhost/?foo=x=x=x&bar=y'
        u = url.URL(S)
        self.failUnless(u.query == 'foo=x=x=x&bar=y')
        self.failUnless(u.query_list == [('foo', 'x=x=x'), ('bar', 'y')])
        self.failUnless(u == S)
        self.failUnless(u.clone() == S)

    def test_path_qs(self):
        path_qs = url.URL('http://localhost:1234/foo?a=b#c').path_qs
        assert isinstance(path_qs, url.URL)
        assert path_qs == '/foo?a=b#c'


class Serialization(unittest.TestCase):

    def test_strangeSegs(self):
        base = 'http://localhost/'
        tests = (
            (r'/foo/', '%2Ffoo%2F'),
            (r'c:\foo\bar bar', 'c%3A%5Cfoo%5Cbar%20bar'),
            (r'&<>', '%26%3C%3E'),
            (u'!"\N{POUND SIGN}$%^&*()_+'.encode('utf-8'), '!%22%C2%A3%24%25%5E%26*()_%2B'),
            )
        for test, result in tests:
            u = url.URL(base).child(test)
            self.assertEquals(u, base+result)


#    def test_rfc1808(self):
#        """Test the relative link resolving stuff I found in rfc1808 section 5.
#        """
#        base = url.URL(rfc1808_relative_link_base)
#        for link, result in rfc1808_relative_link_tests:
#            print link
#            self.failUnlessEqual(result, base.click(link))
#    test_rfc1808.todo = 'Many of these fail miserably at the moment; often with a / where there shouldn\'t be'


class TestURLAccessor(unittest.TestCase):

    def setUp(self):
        self.host_url = url.URL("http://localhost:1234")
        self.application_url = self.host_url.child('app')
        self.url = self.application_url.child('resource').add_query('foo', 'bar')
        self.request = http.Request.blank('/resource?foo=bar', base_url=self.application_url)
        self.url_accessor = url.URLAccessor(self.request)

    def test_host_url(self):
        self.assertEquals(self.url_accessor.host_url, self.request.host_url)
        self.assertEquals(self.url_accessor.host_url, self.host_url)
        self.assertTrue(isinstance(self.url_accessor.host_url, url.URL))

    def test_application_path(self):
        self.assertEquals(self.url_accessor.application_path, '/app')
        self.assertTrue(isinstance(self.url_accessor.application_path, url.URL))

    def test_path_url(self):
        self.assertEquals(self.url_accessor.path_url, self.request.path_url)
        self.assertTrue(isinstance(self.url_accessor.path_url, url.URL))

    def test_url(self):
        self.assertEquals(self.url_accessor.url, self.request.url)
        self.assertEquals(self.url_accessor.url, self.url)
        self.assertTrue(isinstance(self.url_accessor.url, url.URL))

    def test_path(self):
        self.assertEquals(self.url_accessor.path, self.request.path)
        self.assertTrue(isinstance(self.url_accessor.path, url.URL))

    def test_path_qs(self):
        self.assertEquals(self.url_accessor.path_qs, self.request.path_qs)
        self.assertTrue(isinstance(self.url_accessor.path_qs, url.URL))

    def test_new(self):
        u = self.url_accessor.new('http://localhost:1234/a/b/c')
        assert u == 'http://localhost:1234/a/b/c' 
        self.assertTrue(isinstance(u, url.URL))

if __name__ == '__main__':
    unittest.main()
