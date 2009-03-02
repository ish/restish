import urlparse
import urllib


# Lists of characters considered "safe", i.e. should not be escape encoded.
SAFE = '-_.!*\'()~'
SAFE_SEGMENT = SAFE
SAFE_QUERY_NAME = SAFE
SAFE_QUERY_VALUE = SAFE + '='


# Marker object for unset attributes when None is a meaningful value.
_UNSET = object()


def _decode(S):
    """ Simple decode from utf-8 """
    return S.decode('utf-8')


def _encode(S):
    """ Simple encode to utf8 if it's a unicode instance """
    if isinstance(S, unicode):
        return S.encode('utf-8')
    return S


def _quote(S, safe):
    """ urllib quote - see top of module for range of safe definitions """
    return urllib.quote(S, safe)


def _unquote(S):
    """ urllib unquote """
    return urllib.unquote_plus(S)


def split_path(path):
    """
    Split a path of type str into a sequence of unicode segments.
    """
    segments = [urllib.unquote(segment) for segment in path.split('/')]
    if segments[:1] == ['']:
        segments = segments[1:]
    return [_decode(S) for S in segments]


def join_path(path_segments):
    """
    Combine a sequence of path segments into a single str.
    """
    if not path_segments:
        return ''
    return '/' + '/'.join([_quote((_encode(seg)), SAFE_SEGMENT)
        for seg in path_segments])


def _split_query(query):
    """
    Break the query into tuples of it's unquotes elements
    """
    for x in query.split('&'):
        if '=' in x:
            yield tuple(_decode(_unquote(s)) for s in x.split('=', 1))
        elif x:
            yield (_decode(_unquote(x)), None)


def split_query(query):
    """
    Split a query string (str) into a sequence of (name, value) tuples where
    name and value are unicode instances.
    """
    return list(_split_query(query))


def join_query(query_list):
    """
    Join a sequence of (name, value) tuples into a single str.
    """
    def one(KV):
        (K, V) = KV
        if V is None:
            return _quote(_encode(K), SAFE_QUERY_NAME)
        else:
            return '%s=%s' % (_quote(_encode(K), SAFE_QUERY_NAME), \
                              _quote(_encode(V), SAFE_QUERY_VALUE))
    return '&'.join(one(KV) for KV in query_list)


class URL(str):
    """
    URL class.

    A URL instance is a smart string (Python str). URL instances mostly behave
    the same as a str instance (with the possible exception of the equality
    operation) but include attributes to access specific parts of the URL.

    URL instances also include methods to manipulate a URL. Each time a URL is
    modified a new URL instance is resturned.

    The URL class tries to be unicode-aware. Unicode path segments and query
    components are UTF-8 encoded on the way in and always returned as unicode
    instances. Note however that the URL itself is a byte string.
    """

    def __init__(self, url):
        """
        Create a new URL instance from a str URL.
        """
        str.__init__(url)
        self.parsed_url = urlparse.urlsplit(url)

    def __eq__(self, other):
        if isinstance(other, URL):
            return self.parsed_url == other.parsed_url
        elif isinstance(other, str):
            return self.parsed_url == urlparse.urlsplit(other)
        return False

    @property
    def scheme(self):
        """ The url scheme (http, https, etc) """
        return self.parsed_url[0]

    @property
    def netloc(self):
        """ The domain or network location """
        return self.parsed_url[1]

    @property
    def path(self):
        """ The path of the url without query string or fragment """
        return self.__class__(self.parsed_url[2])

    @property
    def path_qs(self):
        """ The path, query string and fragment """
        return self.clone(scheme=None, netloc=None)

    @property
    def path_segments(self):
        """ A list of url segments """
        return split_path(self.path)

    @property
    def query(self):
        """ The query parameters as a string """
        return self.parsed_url[3]

    @property
    def query_list(self):
        """ The query parameters as a list of tuples """
        return split_query(self.query)

    @property
    def fragment(self):
        """ The url fragment (e.g. #anchor) """
        return self.parsed_url[4]

    def clone(self, scheme=_UNSET, netloc=_UNSET, \
              path=_UNSET, query=_UNSET, fragment=_UNSET):
        """
        Make a new instance of self, passing along the given
        arguments to its constructor.

        :arg scheme:
        :arg netloc:
        :arg path:
        :arg query:
        :arg fragment:
        """
        scheme_, netloc_, path_, query_, fragment_ = self.parsed_url
        if scheme is not _UNSET:
            scheme_ = scheme
        if netloc is not _UNSET:
            netloc_ = netloc
        if path is not _UNSET:
            path_ = path
        if query is not _UNSET:
            query_ = query
        if fragment is not _UNSET:
            fragment_ = fragment
        return self.__class__(urlparse.urlunsplit((scheme_, netloc_, path_, query_, fragment_)))
    
    ## path manipulations ##

    def root(self):
        """
        Contruct a URL to the root of the web server.
        """
        return self.clone(path='/', query=None, fragment=None)

    def sibling(self, segment):
        """
        Construct a url where the given path segment is a sibling of this url
        """
        l = list(self.path_segments)
        l[-1] = segment
        return self.clone(path=join_path(l), query=None, fragment=None)

    def child(self, *path):
        """
        Construct a url where the given path segment is a child of this url
        """
        l = list(self.path_segments)
        if l[-1:] == ['']:
            l[-1:] = path
        else:
            l.extend(path)
        return self.clone(path=join_path(l), query=None, fragment=None)

    def parent(self):
        """
        Pop a URL segment from this url.
        """
        l = list(self.path_segments)
        l.pop()
        return self.clone(path=join_path(l), query=None, fragment=None)
    
    def click(self, href):
        """
        Modify the path as if ``href`` were clicked

        Create a url as if the current url was given by ``self`` and ``href`` was clicked on
        """
        scheme, netloc, path, query, fragment = urlparse.urlsplit(href)

        # Return self if the click URL is empty.
        if (scheme, netloc, path, query, fragment) == ('', '', '', '', ''):
            return self

        if scheme:
            return self.clone(scheme=scheme, netloc=netloc, \
                              path=path, query=query, fragment=fragment)
        else:
            scheme = self.scheme

        # Copy less specific missing parts of the URL from the current URL. We
        # don't need to worry about copying the fragment because an empty click
        # URL is handled above.
        if not netloc:
            netloc = self.netloc
            if not path:
                path = self.path
                if not query:
                    query = self.query
            else:
                if path[0] != '/':
                    path = join_path(self.path_segments[:-1] + split_path(path))

        path = normalise_path(path)
        return self.clone(scheme=scheme, netloc=netloc, \
                          path=path, query=query, fragment=fragment) 
    
    def add_query(self, name, value=None):
        """
        Add a query argument with the given value

        :arg key: the query key
        :arg value: The query value. None means do not use a value. e.g. ``?key=``
        """
        if value is not None:
            value = unicode(value)
        q = list(self.query_list)
        q.append((name, value))
        return self.clone(query=join_query(q))
    
    def add_queries(self, query_list):
        """
        Add multiple query args from a list of tuples

        :arg query_list: list of tuple (key, value) pairs
        """
        q = list(self.query_list)
        q.extend(query_list)
        return self.clone(query=join_query(q))

    def replace_query(self, name, value=None):
        """
        Remove all existing occurrences of the query argument 'name', *if it
        exists*, then add the argument with the given value.

        :arg key: the query key
        :arg value: The query value. None means do not use a value. e.g. ``?key=``
        """
        if value is not None:
            value = unicode(value)
        ql = self.query_list
        ## Preserve the original position of the query key in the list
        i = 0
        for (k, v) in ql:
            if k == name:
                break
            i += 1
        q = filter(lambda x: x[0] != name, ql)
        q.insert(i, (name, value))
        return self.clone(query=join_query(q))

    def remove_query(self, name):
        """
        Remove all query arguments with the given name

        :arg name: the name of the query arguments to remove
        """
        q = filter(lambda x: x[0] != name, self.query_list)
        return self.clone(query=join_query(q))

    def clear_queries(self, name=None):
        """
        Remove all existing query arguments

        :arg name: the name of the query arguments to remove, defaults to removing all
        """
        if name is None:
            q = []
        else:
            q = filter(lambda x: x[0] != name, self.query_list)
        return self.clone(query=join_query(q))
    
    ## scheme manipulation ##

    def secure(self, secure=True, port=None):
        """Modify the scheme to https/http and return the new URL.

        :arg secure: choose between https and http, default to True (https)
        :arg port: port, override the scheme's normal port
        """

        # Choose the scheme and default port.
        if secure:
            scheme, defaultPort = 'https', 443
        else:
            scheme, defaultPort = 'http', 80

        # Rebuild the netloc with port if not default.
        netloc = self.netloc.split(':', 1)[0]
        if port is not None and port != defaultPort:
            netloc = '%s:%d' % (netloc, port)

        return self.clone(scheme=scheme, netloc=netloc)

    ## fragment/anchor manipulation

    def anchor(self, anchor=None):
        """
        Modify the fragment/anchor and return a new URL. 

        :arg anchor: An anchor of None (the default) or '' will remove the
                     current anchor.
        """
        return self.clone(fragment=anchor)


class URLAccessor(object):
    """
    URL accessor, provides access to useful URLs, often constructed from the
    accessor's request.
    """

    def __init__(self, request):
        self.request = request

    @property
    def url(self):
        """
        Return the full current (i.e. requested), URL.
        """
        return self.request.url

    @property
    def path(self):
        """
        Return the path part of the current URL, relative to the root of the
        web server.
        """
        return self.request.path

    @property
    def path_qs(self):
        """
        Return the path of the current URL, relative to the root of the web
        server, and the query string.
        """
        return self.request.path_qs

    @property
    def host_url(self):
        """
        Return the host's URL, i.e. the URL of the HTTP server.
        """
        return self.request.host_url

    @property
    def path_url(self):
        """
        Return the path's URL, i.e. the current URL without the query string.
        """
        return self.request.path_url

    @property
    def application_url(self):
        """
        Return the WSGI application's URL.
        """
        return self.request.application_url

    @property
    def application_path(self):
        """
        Return the path part of the application's URL.
        """
        return self.request.application_path

    def new(self, url):
        """
        Create a new URL instance.
        """
        return URL(url)

    
def normalise_path(path):
    """
    Normalise the URL path by resolving segments of '.' and '..'.
    """
    segs = []

    path_segs = split_path(path)

    for seg in path_segs:
        if seg == '.':
            pass
        elif seg == '..':
            if segs:
                segs.pop()
        else:
            segs.append(seg)

    if path_segs[-1:] in (['.'], ['..']):
        segs.append('')

    return join_path(segs)

