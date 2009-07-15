def wsgi_out(app, environ):
    import warnings
    warnings.warn("[0.10] Please use WebTest or paste.wsgilib.intercept_output instead.",
                  DeprecationWarning)
    out = {}
    def start_response(status, headers):
        out['status'] = status
        out['headers'] = headers
    result = app(environ, start_response)
    out['body'] = ''.join(iter(result))
    if hasattr(result, 'close'):
        result.close()
    return out

