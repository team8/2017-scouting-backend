from firebase import firebase
from firebase import firebase_token_generator

class FirebaseAuthentication(object):
    """
    Class that wraps the Firebase SimpleLogin mechanism. Actually this
    class does not trigger a connection, simply fakes the auth action.

    In addition, the provided email and password information is totally
    useless and they never appear in the ``auth`` variable at the server.
    """
    def __init__(self, token, email, debug=False, admin=False, extra=None):
        self.authenticator = firebase_token_generator.FirebaseTokenGenerator("lol fake secret", debug, admin)
        self.token = token
        self.email = email
        self.provider = 'password'
        self.extra = (extra or {}).copy()
        self.extra.update({'debug': debug, 'admin': admin,
                           'email': self.email, 'provider': self.provider})

    def get_user(self):
        """
        Method that gets the authenticated user. The returning user has
        the token, email and the provider data.
        """
        user_id = self.extra.get('id')
        return firebase.FirebaseUser(self.email, self.token, self.provider, user_id)