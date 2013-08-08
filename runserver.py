import os
import logging
import server.boog_slayer
from flask import Flask
from flask.ext.login import LoginManager
from flaskext.markdown import Markdown
log = logging.getLogger('boog_slayer')
handler = logging.StreamHandler()
log.setLevel(logging.DEBUG)
log.addHandler(handler)

class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app = Flask(__name__)
Markdown(app)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.register_blueprint(server.boog_slayer.boog_slayer)
app.secret_key = 'This should be something different'.encode()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return server.boog_slayer.models.get_user(userid)

if __name__ == "__main__":

    port = int(os.environ.get('TASK_PORT') or 5000)
    app.run('0.0.0.0', port=port, debug=True)
