import webapp2
from webapp2_extras import sessions, auth

# session for webapp2
class BaseHandler(webapp2.RequestHandler):              # taken from the webapp2 extrta session example
    def dispatch(self):                                 # override dispatch
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)       # dispatch the main handler
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def check_login(self):
        if self.session.get('name') is None:
            self.redirect('/login', abort = True)

    def check_login2(self):
        if self.session.get('name') is not None:
            self.redirect('/', abort = True)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session(max_age = 600)

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'youlingman',
    }


