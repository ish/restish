"""
Guard support library.

Re-exports the primary restish.guard names and adds application-specific guard
checkers.
"""

# Import names from restish.guard so everything guard-related an application
# needs is available from a single module.
from restish.guard import guard, GuardError, GuardResource


def authenticated(request, obj):
    """
    Example guard checker that checks if there is a REMOTE_USER in the WSGI
    environ.
    """
    if not request.environ.get('REMOTE_USER'):
        raise GuardError("Not authenticated.")

