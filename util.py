import redis
import MySQLdb
from igor import const
import webapp2
from webapp2_extras import sessions, auth

# util function
def list2Filter(filter_list):
    filter = {}
    for elem in filter_list:
        filter.update({elem: True})
    return filter

# redis wrapper
r = redis.StrictRedis(**const.redis)

def redis_get(key):
    return r.get(key)

def redis_set(key, value):
    r.set(key, value)
    #r.bgsave()

# mysql wrapper
def mysql_query_list(query):
    c= MySQLdb.connect(**const.mysqldb)
    cursor = c.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        c.close()
        return results
    except:
        c.close()
        return False

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


