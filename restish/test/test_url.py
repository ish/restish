# Copyright (c) 2004-2007 Divmod.
# See LICENSE for details.

"""
Tests for L{nevow.url}.
"""

import urlparse, urllib
from restish import url
import unittest

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

class _IncompatibleSignatureURL(url.URL):
    """
    A test fixture for verifying that subclasses which override C{cloneURL}
    won't be copied by any other means (e.g. constructing C{self.__class___}
    directly).  It accomplishes this by having a constructor signature which
    is incompatible with L{url.URL}'s.
    """
    def __init__(
        self, magicValue, scheme, netloc, pathsegs, querysegs, fragment):
        url.URL.__init__(self, scheme, netloc, pathsegs, querysegs, fragment)
        self.magicValue = magicValue


    def cloneURL(self, scheme, netloc, pathsegs, querysegs, fragment):
        """
        Override the base implementation to pass along C{self.magicValue}.
        """
        return self.__class__(
            self.magicValue, scheme, netloc, pathsegs, querysegs, fragment)

class TestURL(unittest.TestCase):
    def test_fromString(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals(theurl, str(urlpath))

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
            result = str(url.URL.fromString(test))
            self.assertEquals(test, result)


    def test_equality(self):
        urlpath = url.URL.fromString(theurl)
        self.failUnlessEqual(urlpath, url.URL.fromString(theurl))
        self.failIfEqual(urlpath, url.URL.fromString('ftp://www.anotherinvaliddomain.com/foo/bar/baz/?zot=21&zut'))


    def test_fragmentEquality(self):
        """
        An URL created with the empty string for a fragment compares equal
        to an URL created with C{None} for a fragment.
        """
        self.assertEqual(url.URL(fragment=''), url.URL(fragment=None))


    def test_parent(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals("http://www.foo.com:80/a/nice/path?zot=23&zut",
                          str(urlpath.parent()))


    def test_path(self):
        """
        L{URL.path} should be a C{str} giving the I{path} portion of the URL
        only.  Certain bytes should not be quoted.
        """
        urlpath = url.URL.fromString("http://example.com/foo/bar?baz=quux#foobar")
        self.assertEqual(urlpath.path, "foo/bar")
        urlpath = url.URL.fromString("http://example.com/foo%2Fbar?baz=quux#foobar")
        self.assertEqual(urlpath.path, "foo%2Fbar")
        urlpath = url.URL.fromString("http://example.com/-_.!*'()?baz=quux#foo")
        self.assertEqual(urlpath.path, "-_.!*'()")



    def test_parent_root(self):
        urlpath = url.URL.fromString('http://www.foo.com/')
        self.assertEquals("http://www.foo.com/",
                          str(urlpath.parent()))
        self.assertEquals("http://www.foo.com/",
                          str(urlpath.parent().parent()))

    def test_child(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals("http://www.foo.com:80/a/nice/path/gong?zot=23&zut",
                          str(urlpath.child('gong')))
        self.assertEquals("http://www.foo.com:80/a/nice/path/gong%2F?zot=23&zut",
                          str(urlpath.child('gong/')))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/gong%2Fdouble?zot=23&zut",
            str(urlpath.child('gong/double')))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/gong%2Fdouble%2F?zot=23&zut",
            str(urlpath.child('gong/double/')))

    def test_child_init_tuple(self):
        self.assertEquals(
            "http://www.foo.com/a/b/c",
            str(url.URL(netloc="www.foo.com",
                        pathsegs=['a', 'b']).child("c")))

    def test_child_init_root(self):
        self.assertEquals(
            "http://www.foo.com/c",
            str(url.URL(netloc="www.foo.com").child("c")))

    def test_sibling(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/sister?zot=23&zut",
            str(urlpath.sibling('sister')))
        # use an url without trailing '/' to check child removal
        theurl2 = "http://www.foo.com:80/a/nice/path?zot=23&zut"
        urlpath = url.URL.fromString(theurl2)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/sister?zot=23&zut",
            str(urlpath.sibling('sister')))


    def test_click(self):
        urlpath = url.URL.fromString(theurl)
        # a null uri should be valid (return here)
        self.assertEquals("http://www.foo.com:80/a/nice/path/?zot=23&zut",
                          str(urlpath.click("")))
        # a simple relative path remove the query
        self.assertEquals("http://www.foo.com:80/a/nice/path/click",
                          str(urlpath.click("click")))
        # an absolute path replace path and query
        self.assertEquals("http://www.foo.com:80/click",
                          str(urlpath.click("/click")))
        # replace just the query
        self.assertEquals("http://www.foo.com:80/a/nice/path/?burp",
                          str(urlpath.click("?burp")))

        # from a url with no query clicking a url with a query,
        # the query should be handled properly
        u = url.URL.fromString('http://www.foo.com:80/me/noquery')
        self.failUnlessEqual('http://www.foo.com:80/me/17?spam=158',
                             str(u.click('/me/17?spam=158')))

        # Check that everything from the path onward is removed when the click link
        # has no path.
        u = url.URL.fromString('http://localhost/foo?abc=def')
        self.failUnlessEqual(str(u.click('http://www.python.org')), 'http://www.python.org/')


    def test_cloneUnchanged(self):
        """
        Verify that L{url.URL.cloneURL} doesn't change any of the arguments it
        is passed.
        """
        urlpath = url.URL.fromString('https://x:1/y?z=1#A')
        self.assertEqual(
            urlpath.cloneURL(urlpath.scheme,
                             urlpath.netloc,
                             urlpath._qpathlist,
                             urlpath._querylist,
                             urlpath.fragment),
            urlpath)


    def _makeIncompatibleSignatureURL(self, magicValue):
        return _IncompatibleSignatureURL(magicValue, '', '', None, None, '')


    def test_clickCloning(self):
        """
        Verify that L{url.URL.click} uses L{url.URL.cloneURL} to construct its
        return value.
        """
        urlpath = self._makeIncompatibleSignatureURL(8789)
        self.assertEqual(urlpath.click('/').magicValue, 8789)


    def test_clickCloningScheme(self):
        """
        Verify that L{url.URL.click} uses L{url.URL.cloneURL} to construct its
        return value, when the clicked url has a scheme.
        """
        urlpath = self._makeIncompatibleSignatureURL(8031)
        self.assertEqual(urlpath.click('https://foo').magicValue, 8031)


    def test_addCloning(self):
        """
        Verify that L{url.URL.add} uses L{url.URL.cloneURL} to construct its
        return value.
        """
        urlpath = self._makeIncompatibleSignatureURL(8789)
        self.assertEqual(urlpath.add_query('x').magicValue, 8789)


    def test_replaceCloning(self):
        """
        Verify that L{url.URL.replace} uses L{url.URL.cloneURL} to construct
        its return value.
        """
        urlpath = self._makeIncompatibleSignatureURL(8789)
        self.assertEqual(urlpath.replace_query('x').magicValue, 8789)


    def test_removeCloning(self):
        """
        Verify that L{url.URL.remove} uses L{url.URL.cloneURL} to construct
        its return value.
        """
        urlpath = self._makeIncompatibleSignatureURL(8789)
        self.assertEqual(urlpath.remove_query('x').magicValue, 8789)


    def test_clearCloning(self):
        """
        Verify that L{url.URL.clear} uses L{url.URL.cloneURL} to construct its
        return value.
        """
        urlpath = self._makeIncompatibleSignatureURL(8789)
        self.assertEqual(urlpath.clear_queries().magicValue, 8789)


    def test_anchorCloning(self):
        """
        Verify that L{url.URL.anchor} uses L{url.URL.cloneURL} to construct
        its return value.
        """
        urlpath = self._makeIncompatibleSignatureURL(8789)
        self.assertEqual(urlpath.anchor().magicValue, 8789)


    def test_secureCloning(self):
        """
        Verify that L{url.URL.secure} uses L{url.URL.cloneURL} to construct its
        return value.
        """
        urlpath = self._makeIncompatibleSignatureURL(8789)
        self.assertEqual(urlpath.secure().magicValue, 8789)


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
                str(url.URL.fromString(start).click(click)),
                result
                )

    def test_add_query(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp",
            str(urlpath.add_query("burp")))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp=xxx",
            str(urlpath.add_query("burp", "xxx")))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp=xxx&zing",
            str(urlpath.add_query("burp", "xxx").add_query("zing")))
        # note the inversion!
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&zing&burp=xxx",
            str(urlpath.add_query("zing").add_query("burp", "xxx")))
        # note the two values for the same name
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut&burp=xxx&zot=32",
            str(urlpath.add_query("burp", "xxx").add_query("zot", 32)))

    def test_add_noquery(self):
        # fromString is a different code path, test them both
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?foo=bar",
            str(url.URL.fromString("http://www.foo.com:80/a/nice/path/")
                .add_query("foo", "bar")))
        self.assertEquals(
            "http://www.foo.com/?foo=bar",
            str(url.URL(netloc="www.foo.com").add_query("foo", "bar")))

    def test_replace_query(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=32&zut",
            str(urlpath.replace_query("zot", 32)))
        # replace name without value with name/value and vice-versa
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot&zut=itworked",
            str(urlpath.replace_query("zot").replace_query("zut", "itworked")))
        # Q: what happens when the query has two values and we replace?
        # A: we replace both values with a single one
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=32&zut",
            str(urlpath.add_query("zot", "xxx").replace_query("zot", 32)))

    def test_fragment(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut#hiboy",
            str(urlpath.anchor("hiboy")))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut",
            str(urlpath.anchor()))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23&zut",
            str(urlpath.anchor('')))

    def test_clear_queries(self):
        urlpath = url.URL.fromString(theurl)
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zut",
            str(urlpath.clear_queries("zot")))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zot=23",
            str(urlpath.clear_queries("zut")))
        # something stranger, query with two values, both should get cleared
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/?zut",
            str(urlpath.add_query("zot", 1971).clear_queries("zot")))
        # two ways to clear the whole query
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/",
            str(urlpath.clear_queries("zut").clear_queries("zot")))
        self.assertEquals(
            "http://www.foo.com:80/a/nice/path/",
            str(urlpath.clear_queries()))

    def test_secure(self):
        self.assertEquals(str(url.URL.fromString('http://localhost/').secure()), 'https://localhost/')
        self.assertEquals(str(url.URL.fromString('http://localhost/').secure(True)), 'https://localhost/')
        self.assertEquals(str(url.URL.fromString('https://localhost/').secure()), 'https://localhost/')
        self.assertEquals(str(url.URL.fromString('https://localhost/').secure(False)), 'http://localhost/')
        self.assertEquals(str(url.URL.fromString('http://localhost/').secure(False)), 'http://localhost/')
        self.assertEquals(str(url.URL.fromString('http://localhost/foo').secure()), 'https://localhost/foo')
        self.assertEquals(str(url.URL.fromString('http://localhost/foo?bar=1').secure()), 'https://localhost/foo?bar=1')
        self.assertEquals(str(url.URL.fromString('http://localhost/').secure(port=443)), 'https://localhost/')
        self.assertEquals(str(url.URL.fromString('http://localhost:8080/').secure(port=8443)), 'https://localhost:8443/')
        self.assertEquals(str(url.URL.fromString('https://localhost:8443/').secure(False, 8080)), 'http://localhost:8080/')


    def test_eq_same(self):
        u = url.URL.fromString('http://localhost/')
        self.failUnless(u == u, "%r != itself" % u)

    def test_eq_similar(self):
        u1 = url.URL.fromString('http://localhost/')
        u2 = url.URL.fromString('http://localhost/')
        self.failUnless(u1 == u2, "%r != %r" % (u1, u2))

    def test_eq_different(self):
        u1 = url.URL.fromString('http://localhost/a')
        u2 = url.URL.fromString('http://localhost/b')
        self.failIf(u1 == u2, "%r != %r" % (u1, u2))

    def test_eq_apples_vs_oranges(self):
        u = url.URL.fromString('http://localhost/')
        self.failIf(u == 42, "URL must not equal a number.")
        self.failIf(u == object(), "URL must not equal an object.")

    def test_ne_same(self):
        u = url.URL.fromString('http://localhost/')
        self.failIf(u != u, "%r == itself" % u)

    def test_ne_similar(self):
        u1 = url.URL.fromString('http://localhost/')
        u2 = url.URL.fromString('http://localhost/')
        self.failIf(u1 != u2, "%r == %r" % (u1, u2))

    def test_ne_different(self):
        u1 = url.URL.fromString('http://localhost/a')
        u2 = url.URL.fromString('http://localhost/b')
        self.failUnless(u1 != u2, "%r == %r" % (u1, u2))

    def test_ne_apples_vs_oranges(self):
        u = url.URL.fromString('http://localhost/')
        self.failUnless(u != 42, "URL must differ from a number.")
        self.failUnless(u != object(), "URL must be differ from an object.")

    def test_parseEqualInParamValue(self):
        u = url.URL.fromString('http://localhost/?=x=x=x')
        self.failUnless(u.query == ['=x=x=x'])
        self.failUnless(str(u) == 'http://localhost/?=x%3Dx%3Dx')
        u = url.URL.fromString('http://localhost/?foo=x=x=x&bar=y')
        self.failUnless(u.query == ['foo=x=x=x', 'bar=y'])
        self.failUnless(str(u) == 'http://localhost/?foo=x%3Dx%3Dx&bar=y')

class Serialization(unittest.TestCase):

    def testQuoting(self):
        scheme = 'http'
        loc = 'localhost'
        path = ('baz', 'buz', '/fuzz/')
        query = [("foo", "bar"), ("baz", "=quux"), ("foobar", "?")]
        fragment = 'futz'
        u = url.URL(scheme, loc, path, query, fragment)
        s = str(url.URL(scheme, loc, path, query, fragment))

        parsedScheme, parsedLoc, parsedPath, parsedQuery, parsedFragment = urlparse.urlsplit(s)

        self.assertEquals(scheme, parsedScheme)
        self.assertEquals(loc, parsedLoc)
        self.assertEquals('/' + '/'.join(map(lambda p: urllib.quote(p,safe=''),path)), parsedPath)
        self.assertEquals(query, url.unquerify(parsedQuery))
        self.assertEquals(fragment, parsedFragment)



   
    def test_strangeSegs(self):
        base = 'http://localhost/'
        tests = (
            (r'/foo/', '%2Ffoo%2F'),
            (r'c:\foo\bar bar', 'c%3A%5Cfoo%5Cbar%20bar'),
            (r'&<>', '%26%3C%3E'),
            (u'!"\N{POUND SIGN}$%^&*()_+'.encode('utf-8'), '!%22%C2%A3%24%25%5E%26*()_%2B'),
            )
        for test, result in tests:
            u = url.URL.fromString(base).child(test)
            self.assertEquals(str(u), base+result)





    #def test_rfc1808(self):
        #"""Test the relative link resolving stuff I found in rfc1808 section 5.
        #"""
        #base = url.URL.fromString(rfc1808_relative_link_base)
        #for link, result in rfc1808_relative_link_tests:
            ##print link
            #self.failUnlessEqual(result, str(base.click(link)))
    #test_rfc1808.todo = 'Many of these fail miserably at the moment; often with a / where there shouldn\'t be'


    def test_unicode(self):
        """
        L{URLSerializer} should provide basic IRI (RFC 3987) support by
        encoding Unicode to UTF-8 before percent-encoding.
        """
        iri = u'http://localhost/expos\xe9?doppelg\xe4nger=Bryan O\u2019Sullivan#r\xe9sum\xe9'
        uri = 'http://localhost/expos%C3%A9?doppelg%C3%A4nger=Bryan%20O%E2%80%99Sullivan#r%C3%A9sum%C3%A9'
        self.assertEquals(str(url.URL.fromString(iri)), uri)


