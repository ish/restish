"""
Dummy user database module.
"""

USERS = {
    'ming': {'title': 'Emperor', 'name': 'Ming the Merciless', 'password': 'flash'},
}

def get(username):
    return USERS.get(username)

