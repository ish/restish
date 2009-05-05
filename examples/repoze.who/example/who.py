"""
repoze.who integration module.
"""


def identity(request):
    """
    Return the identity or None of the authenticated user from the request.
    """
    return request.environ.get('repoze.who.identity')


def make_userdb_auth_plugin():
    return UserDBAuthenticator()


def make_userdb_md_plugin():
    return UserDBMDProvider()


class UserDBAuthenticator(object):
    """
    repoze.who "IAuthenticator" plugin. Authenticates username/password
    credentials in the application's user database.
    """

    def authenticate(self, environ, identity):
        # Extract the authentication args from the identity.
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            return None
        # We're using a dummy module to simulate authentication against a
        # database of users but authentication could just as easily be
        # performed against some object in the WSGI environ.
        from example import userdb
        user = userdb.get(login)
        # Did we find the user at all?
        if not user:
            return None
        # Does the password match?
        if user['password'] != password:
            return None
        # All clear, return the user's identifier, i.e. the login username.
        return login


class UserDBMDProvider(object):
    """
    repoze.who "IMetadataProvider" plugin. Loads additional information about
    the authenticated user per-request.
    """

    def add_metadata(self, environ, identity):
        # Get the id of the authenticated user.
        userid = identity.get('repoze.who.userid')
        # Lookup in the (dummy) database.
        from example import userdb
        user = userdb.get(userid)
        # Add application-specific data to the identity.
        identity['title'] = user['title']
        identity['name'] = user['name']
        return identity

