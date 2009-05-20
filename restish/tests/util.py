def wsgi_out(app, environ):
    out = {}
    def start_response(status, headers):
        out['status'] = status
        out['headers'] = headers
    result = app(environ, start_response)
    out['body'] = ''.join(iter(result))
    if hasattr(result, 'close'):
        result.close()
    return out

