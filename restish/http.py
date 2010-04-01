"""
HTTP Request and Response objects, simple Response factories and exceptions
types for common HTTP errors.
"""
import cgi
import webob

from restish import error, url


class Request(webob.Request):
    """
    HTTP request class.

    The request represents the request from the client and is created by
    passing a WSGI environ dictionary to the initialiser.

    Request is basically a webob.Request with one important difference:
    url-like properties are represented as url.URL instances to allow them
    to manipulated easily and safely.
    """

    def __init__(self, environ):
        webob.Request.__init__(self, environ)

    @property
    def host_url(self):
        """
        Return the host's URL, i.e. the URL of the HTTP server.
        """
        return url.URL(super(Request, self).host_url)

    @property
    def application_url(self):
        """
        Return the WSGI application's URL.
        """
        return url.URL(super(Request, self).application_url)

    @property
    def application_path(self):
        """
        Return the path part of the WSGI application's URL.
        """
        return self.application_url.path

    @property
    def path_url(self):
        """
        Return the path's URL, i.e. the current URL without the query string.
        """
        return url.URL(super(Request, self).path_url)

    @property
    def url(self):
        """
        Return the full current (i.e. requested), URL.
        """
        return url.URL(super(Request, self).url)

    @property
    def path(self):
        """
        Return the path part of the current URL, relative to the root of the
        web server.
        """
        return url.URL(super(Request, self).path)

    @property
    def path_qs(self):
        """
        Return the path of the current URL, relative to the root of the web
        server, and the query string.
        """
        return url.URL(super(Request, self).path_qs)


class Response(webob.Response):
    """
    HTTP response class.

    A Response instance represents the response that will be sent to the client
    and is created by passing a status code, a list of (name, value) headers
    and a body.

    Response is basically just a webob.Response with a modified initializer and
    less implicit behaviour.
    """

    default_content_type = None

    def __init__(self, status, headers, body):
        kwargs = {'status': status,
                  'headerlist': headers}
        # XXX webob workaround. I can't see a way to create an empty response
        # *with* a content-length, as is common for a HEAD response. So, a
        # workaround is that if there is no body, i.e. None, then we capture
        # the content-length and set the header once webob's initialiser has
        # finished.
        content_length = None
        if body is None:
            header_dict = dict([(key.lower(), val) for (key, val) in headers])
            content_length = header_dict.get('content-length')
        elif isinstance(body, str):
            kwargs['body'] = body
        else:
            kwargs['app_iter'] = body
        webob.Response.__init__(self, **kwargs)
        # XXX webob workaround. see above
        if content_length is not None:
            self.headers['Content-Length'] = content_length


# Successful 2xx

def ok(headers, body):
    """
    200 OK

    The request has succeeded. The information returned with the response
    is dependent on the method used in the request, for example:

    GET an entity corresponding to the requested resource is sent in the
    response;

    HEAD the entity-header fields corresponding to the requested resource are
    sent in the response without any message-body;

    POST an entity describing or containing the result of the action;

    TRACE an entity containing the request message as received by the end
    server.
    """
    return Response("200 OK", headers, body)


def created(location, headers, body):
    """
    201 Created

    The request has been fulfilled and resulted in a new resource being
    created. The newly created resource can be referenced by the URI(s)
    returned in the entity of the response, with the most specific URI for the
    resource given by a Location header field. The response SHOULD include an
    entity containing a list of resource characteristics and location(s) from
    which the user or user agent can choose the one most appropriate. The
    entity format is specified by the media type given in the Content-Type
    header field. The origin server MUST create the resource before returning
    the 201 status code. If the action cannot be carried out immediately, the
    server SHOULD respond with 202 (Accepted) response instead.

    A 201 response MAY contain an ETag response header field indicating the
    current value of the entity tag for the requested variant just created, see
    section 14.19. 
    """
    headers.append(('Location', location))
    return Response("201 Created", headers, body)


# Redirection 3xx

_REDIRECTION_PAGE = """<html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8" />
<title>%(status)s</title>
</head>
<body>
<h1>%(status)s</h1>
<p>This document has moved to <a href="%(location)s">%(location)s</a>.</p>
</body>
</html>"""

def _redirect(status, location, headers=None):
    """
    Creating a standard HTML content for the common redirects:
     * 301 Moved Permanently
     * 302 Found
     * 303 See Other
    """
    if not headers:
        headers = []
    headers.extend([('Location', location),
                    ('Content-Type', 'text/html')])
    body = _REDIRECTION_PAGE % {"status": cgi.escape(status),
                                "location": cgi.escape(location)}
    return Response(status, headers, body)


def moved_permanently(location, headers=None):
    """
    301 Moved Permanently

    The requested resource has been assigned a new permanent URI and any
    future references to this resource SHOULD use one of the returned URIs.
    Clients with link editing capabilities ought to automatically re-link
    references to the Request-URI to one or more of the new references returned
    by the server, where possible. This response is cacheable unless indicated
    otherwise.

    The new permanent URI SHOULD be given by the Location field in the
    response. Unless the request method was HEAD, the entity of the response
    SHOULD contain a short hypertext note with a hyperlink to the new URI(s).

    If the 301 status code is received in response to a request other than GET
    or HEAD, the user agent MUST NOT automatically redirect the request unless
    it can be confirmed by the user, since this might change the conditions
    under which the request was issued.

    Note: When automatically redirecting a POST request after receiving a
    301 status code, some existing HTTP/1.0 user agents will
    erroneously change it into a GET request.
    """
    return _redirect("301 Moved Permanently", location, headers)


def found(location, headers=None):
    """
    302 Found

    The requested resource resides temporarily under a different URI. Since the
    redirection might be altered on occasion, the client SHOULD continue to use
    the Request-URI for future requests. This response is only cacheable if
    indicated by a Cache-Control or Expires header field.

    The temporary URI SHOULD be given by the Location field in the response.
    Unless the request method was HEAD, the entity of the response SHOULD
    contain a short hypertext note with a hyperlink to the new URI(s).

    If the 302 status code is received in response to a request other than GET
    or HEAD, the user agent MUST NOT automatically redirect the request unless
    it can be confirmed by the user, since this might change the conditions
    under which the request was issued.

    Note: RFC 1945 and RFC 2068 specify that the client is not allowed to
    change the method on the redirected request.  However, most existing user
    agent implementations treat 302 as if it were a 303 response, performing a
    GET on the Location field-value regardless of the original request method.
    The status codes 303 and 307 have been added for servers that wish to make
    unambiguously clear which kind of reaction is expected of the client.
    """
    return _redirect("302 Found", location, headers)


def see_other(location, headers=None):
    """
    303 See Other

    The response to the request can be found under a different URI and SHOULD
    be retrieved using a GET method on that resource. This method exists
    primarily to allow the output of a POST-activated script to redirect the
    user agent to a selected resource. The new URI is not a substitute
    reference for the originally requested resource. The 303 response MUST NOT
    be cached, but the response to the second (redirected) request might be
    cacheable.

    The different URI SHOULD be given by the Location field in the response.
    Unless the request method was HEAD, the entity of the response SHOULD
    contain a short hypertext note with a hyperlink to the new URI(s).

    Note: Many pre-HTTP/1.1 user agents do not understand the 303 status. When
    interoperability with such clients is a concern, the 302 status code may be
    used instead, since most user agents react to a 302 response as described
    here for 303.
    """
    return _redirect("303 See Other", location, headers)


def not_modified(headers=None):
    """
    304 Not Modified

    If the client has performed a conditional GET request and access is
    allowed, but the document has not been modified, the server SHOULD respond
    with this status code. The 304 response MUST NOT contain a message-body,
    and thus is always terminated by the first empty line after the header
    fields.

    The response MUST include the following header fields:

          - Date, unless its omission is required by section 14.18.1

    If a clockless origin server obeys these rules, and proxies and clients add
    their own Date to any response received without one (as already specified
    by [RFC 2068], section 14.19), caches will operate correctly.

          - ETag and/or Content-Location, if the header would have been sent in
    a 200 response to the same request

          - Expires, Cache-Control, and/or Vary, if the field-value might
    differ from that sent in any previous response for the same variant

    If the conditional GET used a strong cache validator (see section 13.3.3),
    the response SHOULD NOT include other entity-headers. Otherwise (i.e., the
    conditional GET used a weak validator), the response MUST NOT include other
    entity-headers; this prevents inconsistencies between cached entity-bodies
    and updated headers.

    If a 304 response indicates an entity not currently cached, then the cache
    MUST disregard the response and repeat the request without the conditional.

    If a cache uses a received 304 response to update a cache entry, the cache
    MUST update the entry to reflect any new field values given in the
    response. 
    """
    if headers is None:
        headers = []
    return Response("304 Not Modified", headers, None)


# Client Error 4xx

def bad_request(headers=None, body=None):
    """
    400 Bad Request

    The request could not be understood by the server due to malformed syntax.
    The client SHOULD NOT repeat the request without modifications.
    """
    if headers is None and body is None:
        headers = [('Content-Type', 'text/plain')]
        body = '400 Bad Request'
    return Response("400 Bad Request", headers, body)


class BadRequestError(error.HTTPClientError):
    """ Exception for the 400 http code """
    response_factory = staticmethod(bad_request)


def unauthorized(headers, body):
    """
    401 Unauthorized

    The request requires user authentication. The response MUST include a
    WWW-Authenticate header field (section 14.47) containing a challenge
    applicable to the requested resource. The client MAY repeat the request
    with a suitable Authorization header field (section 14.8). If the request
    already included Authorization credentials, then the 401 response indicates
    that authorization has been refused for those credentials. If the 401
    response contains the same challenge as the prior response, and the user
    agent has already attempted authentication at least once, then the user
    SHOULD be presented the entity that was given in the response, since that
    entity might include relevant diagnostic information. HTTP access
    authentication is explained in "HTTP Authentication: Basic and Digest
    Access Authentication" [43]. 
    """
    return Response("401 Unauthorized", headers, body)


class UnauthorizedError(error.HTTPClientError):
    """ Exception for the 401 http code """
    response_factory = staticmethod(unauthorized)


def forbidden(headers=None, body=None):
    """
    403 Forbidden

    The server understood the request, but is refusing to fulfill it.
    Authorization will not help and the request SHOULD NOT be repeated. If the
    request method was not HEAD and the server wishes to make public why the
    request has not been fulfilled, it SHOULD describe the reason for the
    refusal in the entity. If the server does not wish to make this information
    available to the client, the status code 404 (Not Found) can be used
    instead. 
    """
    if headers is None and body is None:
        headers = [('Content-Type', 'text/plain')]
        body = '403 Forbidden'
    return Response("403 Forbidden", headers, body)


class ForbiddenError(error.HTTPClientError):
    """ Exception for the 403 http code """
    response_factory = staticmethod(forbidden)


def not_found(headers=None, body=None):
    """
    404 Not Found

    The server has not found anything matching the Request-URI. No indication
    is given of whether the condition is temporary or permanent. The 410 (Gone)
    status code SHOULD be used if the server knows, through some internally
    configurable mechanism, that an old resource is permanently unavailable and
    has no forwarding address. This status code is commonly used when the
    server does not wish to reveal exactly why the request has been refused, or
    when no other response is applicable. 
    """
    if headers is None and body is None:
        headers = [('Content-Type', 'text/plain')]
        body = '404 Not Found'
    return Response("404 Not Found", headers, body)


class NotFoundError(error.HTTPClientError):
    """ Exception for the 404 http code """
    response_factory = staticmethod(not_found)


def method_not_allowed(allow):
    """
    405 Not Allowed

    The method specified in the Request-Line is not allowed for the resource
    identified by the Request-URI. The response MUST include an Allow header
    containing a list of valid methods for the requested resource.
    """
    if isinstance(allow, list):
        allow = ', '.join(allow)
    return Response("405 Method Not Allowed",
          [('Content-Type', 'text/plain'), \
           ('Allow', allow)], "405 Method Not Allowed")


class MethodNotAllowedError(error.HTTPClientError):
    """ Exception for the 405 http code """
    response_factory = staticmethod(method_not_allowed)


def not_acceptable(headers, body):
    """
    406 Not Acceptable

    The resource identified by the request is only capable of generating
    response entities which have content characteristics not acceptable
    according to the accept headers sent in the request.

    Unless it was a HEAD request, the response SHOULD include an entity
    containing a list of available entity characteristics and location(s) from
    which the user or user agent can choose the one most appropriate. The
    entity format is specified by the media type given in the Content-Type
    header field. Depending upon the format and the capabilities of the user
    agent, selection of the most appropriate choice MAY be performed
    automatically. However, this specification does not define any standard for
    such automatic selection.

    Note: HTTP/1.1 servers are allowed to return responses which are not
    acceptable according to the accept headers sent in the request. In some
    cases, this may even be preferable to sending a 406 response.  User agents
    are encouraged to inspect the headers of an incoming response to determine
    if it is acceptable.

    If the response could be unacceptable, a user agent SHOULD temporarily stop
    receipt of more data and query the user for a decision on further actions. 
    """
    return Response('406 Not Acceptable', headers, body)


class NotAcceptableError(error.HTTPClientError):
    """ Exception for the 406 http code """
    response_factory = staticmethod(not_acceptable)


def conflict(headers, body):
    """
    409 Conflict

    The request could not be completed due to a conflict with the current state
    of the resource. This code is only allowed in situations where it is
    expected that the user might be able to resolve the conflict and resubmit
    the request. The response body SHOULD include enough information for the
    user to recognize the source of the conflict. Ideally, the response entity
    would include enough information for the user or user agent to fix the
    problem; however, that might not be possible and is not required.

    Conflicts are most likely to occur in response to a PUT request. For
    example, if versioning were being used and the entity being PUT included
    changes to a resource which conflict with those made by an earlier
    (third-party) request, the server might use the 409 response to indicate
    that it can't complete the request. In this case, the response entity would
    likely contain a list of the differences between the two versions in a
    format defined by the response Content-Type. 
    """
    return Response("409 Conflict", headers, body)


class ConflictError(error.HTTPClientError):
    """ Exception for the 409 http code """
    response_factory = staticmethod(conflict)


# Server Error 5xx

def internal_server_error(headers=None, body=None):
    """
    500 Internal Server Error.

    The server encountered an unexpected condition which prevented it from
    fulfilling the request. 
    """
    if headers is None and body is None:
        headers = [('Content-Type', 'text/plain')]
        body = '500 Internal Server Error'
    return Response('500 Internal Server Error', headers, body)


class InternalServerError(error.HTTPServerError):
    """
    500 Internal Server Error exception.
    """
    response_factory = staticmethod(internal_server_error)


def bad_gateway(headers=None, body=None):
    """
    502 Bad Gateway.

    The server, while acting as a gateway or proxy, received an invalid
    response from the upstream server it accessed in attempting to fulfill the
    request.
    """
    if headers is None and body is None:
        headers = [('Content-Type', 'text/plain')]
        body = '502 Bad Gateway'
    return Response('502 Bad Gateway', headers, body)


class BadGatewayError(error.HTTPServerError):
    """
    502 Bad Gateway exception.
    """
    response_factory = staticmethod(bad_gateway)


def service_unavailable(headers=None, body=None):
    """
    503 Service Unavailable.

    The server is currently unable to handle the request due to a temporary
    overloading or maintenance of the server. The implication is that this is a
    temporary condition which will be alleviated after some delay. If known,
    the length of the delay MAY be indicated in a Retry-After header. If no
    Retry-After is given, the client SHOULD handle the response as it would for
    a 500 response. 
    """
    if headers is None and body is None:
        headers = [('Content-Type', 'text/plain')]
        body = '503 Service Unavailable'
    return Response('503 Service Unavailable', headers, body)


class ServiceUnavailableError(error.HTTPServerError):
    """
    503 Service Unavailable exception.
    """
    response_factory = staticmethod(service_unavailable)


def gateway_timeout(headers=None, body=None):
    """
    504 Gateway Timeout.

    The server, while acting as a gateway or proxy, did not receive a timely
    response from the upstream server specified by the URI (e.g. HTTP, FTP,
    LDAP) or some other auxiliary server (e.g. DNS) it needed to access in
    attempting to complete the request. 
    """
    if headers is None and body is None:
        headers = [('Content-Type', 'text/plain')]
        body = '504 Gateway Timeout'
    return Response('504 Gateway Timeout', headers, body)


class GatewayTimeoutError(error.HTTPServerError):
    """
    504 Gateway Timeout exception.
    """
    response_factory = staticmethod(gateway_timeout)

