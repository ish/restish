import urlparse
import urllib


def _uqf(query):
    for x in query.split('&'):
        if '=' in x:
            yield tuple( [urllib.unquote_plus(s) for s in x.split('=', 1)] )
        elif x:
            yield (urllib.unquote_plus(x), None)
unquerify = lambda query: list(_uqf(query))


SAFE = '-_.!*\'()~'

class URL(object):


    def __init__(self, scheme='http', netloc='localhost', pathsegs=None,
                 querysegs=None, fragment=None):
        self.scheme = scheme
        self.netloc = netloc
        if pathsegs is None:
            pathsegs = ['']
        self._qpathlist = pathsegs
        if querysegs is None:
            querysegs = []
        self._querylist = querysegs
        if fragment is None:
            fragment = ''
        self.fragment = fragment
        
    def path():
        def get(self):
            return '/'.join([
                    # Note that this set of safe things is pretty arbitrary.
                    # It is this particular set in order to match that used by
                    # nevow.flat.flatstan.StringSerializer, so that url.path
                    # will give something which is contained by flatten(url).
                    urllib.quote(seg, safe="-_.!*'()") for seg in self._qpathlist])
        doc = """
        The path portion of the URL.
        """
        return get, None, None, doc
    path = property(*path())

    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        for attr in ['scheme', 'netloc', '_qpathlist', '_querylist', 'fragment']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return not self.__eq__(other)

    query = property(
        lambda self: [y is None and x or '='.join((x,y))
            for (x,y) in self._querylist]
        )    

    def _pathMod(self, newpathsegs, newqueryparts):
        return self.cloneURL(self.scheme,
                             self.netloc,
                             newpathsegs,
                             newqueryparts,
                             self.fragment)


    def cloneURL(self, scheme, netloc, pathsegs, querysegs, fragment):
        """
        Make a new instance of C{self.__class__}, passing along the given
        arguments to its constructor.
        """
        return self.__class__(scheme, netloc, pathsegs, querysegs, fragment)    
    
    def fromString(cls, st):
        scheme, netloc, path, query, fragment = urlparse.urlsplit(st)
        u = cls(
            scheme, netloc,
            [urllib.unquote(seg) for seg in path.split('/')[1:]],
            unquerify(query), urllib.unquote(fragment))
        return u
    fromString = classmethod(fromString)
    
    ## path manipulations ##

    def pathList(self, unquote=False, copy=True):
        result = self._qpathlist
        if unquote:
            result = map(urllib.unquote, result)
        if copy:
            result = result[:]
        return result

    def sibling(self, path):
        """Construct a url where the given path segment is a sibling of this url
        """
        l = self.pathList()
        l[-1] = path
        return self._pathMod(l, self.queryList(0))

    def child(self, path):
        """Construct a url where the given path segment is a child of this url
        """
        l = self.pathList()
        if l[-1] == '':
            l[-1] = path
        else:
            l.append(path)
        return self._pathMod(l, self.queryList(0))

    def isRoot(self, pathlist):
        return (pathlist == [''] or not pathlist)

    def parent(self):
        """Pop a URL segment from this url.
        """
        l = self.pathList()
        if len(l) >1:
            l.pop()
        return self._pathMod(l, self.queryList(0))
    
    def click(self, href):
        """Build a path by merging 'href' and this path.

        Return a path which is the URL where a browser would presumably
        take you if you clicked on a link with an 'href' as given.
        """
        scheme, netloc, path, query, fragment = urlparse.urlsplit(href)

        if (scheme, netloc, path, query, fragment) == ('', '', '', '', ''):
            return self

        query = unquerify(query)

        if scheme:
            if path and path[0] == '/':
                path = path[1:]
            return self.cloneURL(
                scheme, netloc, path.split('/'), query, fragment)
        else:
            scheme = self.scheme

        if not netloc:
            netloc = self.netloc
            if not path:
                path = self.path
                if not query:
                    query = self._querylist
                    if not fragment:
                        fragment = self.fragment
            else:
                if path[0] == '/':
                    path = path[1:]
                else:
                    l = self.pathList()
                    l[-1] = path
                    path = '/'.join(l)

        path = normURLPath(path)
        return self.cloneURL(
            scheme, netloc, path.split('/'), query, fragment) 
    
    def queryList(self, copy=True):
        """Return current query as a list of tuples."""
        if copy:
            return self._querylist[:]
        return self._querylist
    
    def add_query(self, name, value=None):
        if value is not None:
            value = unicode(value)
        """Add a query argument with the given value
        None indicates that the argument has no value
        """
        q = self.queryList()
        q.append((name, value))
        return self._pathMod(self.pathList(copy=False), q)

    def replace_query(self, name, value=None):
        if value is not None:
            value = unicode(value)
        """
        Remove all existing occurrences of the query argument 'name', *if it
        exists*, then add the argument with the given value.

        C{None} indicates that the argument has no value.
        """
        ql = self.queryList(False)
        ## Preserve the original position of the query key in the list
        i = 0
        for (k, v) in ql:
            if k == name:
                break
            i += 1
        q = filter(lambda x: x[0] != name, ql)
        q.insert(i, (name, value))
        return self._pathMod(self.pathList(copy=False), q)

    def remove_query(self, name):
        """Remove all query arguments with the given name
        """
        return self._pathMod(
            self.pathList(copy=False),
            filter(
                lambda x: x[0] != name, self.queryList(False)))

    def clear_queries(self, name=None):
        """Remove all existing query arguments
        """
        if name is None:
            q = []
        else:
            q = filter(lambda x: x[0] != name, self.queryList(False))
        return self._pathMod(self.pathList(copy=False), q)    
    
    ## scheme manipulation ##

    def secure(self, secure=True, port=None):
        """Modify the scheme to https/http and return the new URL.

        @param secure: choose between https and http, default to True (https)
        @param port: port, override the scheme's normal port
        """

        # Choose the scheme and default port.
        if secure:
            scheme, defaultPort = 'https', 443
        else:
            scheme, defaultPort = 'http', 80

        # Rebuild the netloc with port if not default.
        netloc = self.netloc.split(':',1)[0]
        if port is not None and port != defaultPort:
            netloc = '%s:%d' % (netloc, port)

        return self.cloneURL(
            scheme, netloc, self._qpathlist, self._querylist, self.fragment)

    ## fragment/anchor manipulation

    def anchor(self, anchor=None):
        """
        Modify the fragment/anchor and return a new URL. An anchor of
        C{None} (the default) or C{''} (the empty string) will remove the
        current anchor.
        """
        return self.cloneURL(
            self.scheme, self.netloc, self._qpathlist, self._querylist, anchor)
    
    def __str__(self):
        return ''.join(serialise(self))
    
    def __repr__(self):
        return (
            '%s(scheme=%r, netloc=%r, pathsegs=%r, querysegs=%r, fragment=%r)'
            % (self.__class__,
               self.scheme,
               self.netloc,
               self._qpathlist,
               self._querylist,
               self.fragment))
    
def normURLPath(path):
    """
    Normalise the URL path by resolving segments of '.' and '..'.
    """
    segs = []

    pathSegs = path.split('/')

    for seg in pathSegs:
        if seg == '.':
            pass
        elif seg == '..':
            if segs:
                segs.pop()
        else:
            segs.append(seg)

    if pathSegs[-1:] in (['.'],['..']):
        segs.append('')

    return '/'.join(segs)


def serialise(u):
    """
    Serialise the given L{URL}.

    Unicode path, query and fragment components are handled according to the
    IRI standard (RFC 3987).
    """
    def _maybeEncode(s):
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        return s
    if u.scheme:
        # TODO: handle Unicode (see #2409)
        yield "%s://%s" % (u.scheme, u.netloc)
    for pathsegment in u._qpathlist:
        yield '/'
        yield urllib.quote(_maybeEncode(pathsegment), safe=SAFE)
    query = u._querylist
    if query:
        yield '?'
        first = True
        for key, value in query:
            if not first:
                yield '&'
            else:
                first = False
            yield urllib.quote(_maybeEncode(key), safe=SAFE)
            if value is not None:
                yield '='
                yield urllib.quote(_maybeEncode(value), safe=SAFE)
    if u.fragment:
        yield "#"
        yield urllib.quote(_maybeEncode(u.fragment), safe=SAFE)