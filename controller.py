# -*- coding: utf-8 -*-

import jinja2
import os
import webapp2
from webapp2_extras import sessions, auth
import json
import util
from openid.consumer import consumer
from openid.extensions import pape, sreg


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
data = [{'id': '1', 'name': '测试1'}, {'id': '2', 'name': '测试2'}]

# controller
# index
class MainPage(util.BaseHandler):
    def get(self):
        #self.check_login()
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(datas = data, session = self.session))

# login
provider_url = 'https://youropenidserver.com/openid/'
class Login(util.BaseHandler):
    def get(self):
        self.check_login2()
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_environment.get_template('login.html')
        self.response.out.write(template.render())

# logout
class Logout(util.BaseHandler):
    def get(self):
        self.session['name'] = None
        self.session.clear()
        self.redirect('/login')

# openid
class Auth(util.BaseHandler):
    def get(self):
        # openid auth
        self.check_login2()
        oid = consumer.Consumer({}, None)
        try:
            request = oid.begin(provider_url)
        except Exception, e:
            template = jinja_environment.get_template('error.html')
            self.response.out.write(template.render(mag = 'OpenID begin error'))
            return
            
        sreg_request = sreg.SRegRequest(required=['email', 'fullname', 'nickname'], optional=[])
        request.addExtension(sreg_request)

        redirect_url = request.redirectURL(self.request.host_url, self.request.host_url + '/login/verify')

        self.redirect(redirect_url)

class Verify(util.BaseHandler):
    def get(self):
        # openid verify
        self.check_login2()
        oid = consumer.Consumer({}, None)
        query_dict = {}
        for k, v in self.request.GET.items():
            query_dict[k] = v

        try:
            info = oid.complete(query_dict, self.request.host_url + '/login/verify')

        except Exception, e:
            template = jinja_environment.get_template('error.html')
            self.response.out.write(template.render(msg = 'OpenID verification failed'))
            return
        
        if info.status != consumer.SUCCESS or not info.identity_url.startswith(provider_url):
            template = jinja_environment.get_template('error.html')
            self.response.out.write(template.render(msg = 'OpenID verification failed'))
            return
        else:
            # gain user info
            sreg_resp = sreg.SRegResponse.fromSuccessResponse(info)
            if sreg_resp:
                self.session['name'] = sreg_resp.get('fullname')
                self.session['email'] = sreg_resp.get('email')

            self.redirect('/')

application = webapp2.WSGIApplication([('/', MainPage),
        (r'/login', Login),
        (r'/logout', Logout),
        (r'/login/auth', Auth),
        (r'/login/verify', Verify)
], config = util.config, debug = True)


# for local debug
from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
static_app = StaticURLParser("/root/webapp2-demo/")
app = Cascade([static_app, application])

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()

