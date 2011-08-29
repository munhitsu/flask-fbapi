from flask import _request_ctx_stack
from flaskext.fbapi.storage import redis
from flask import _request_ctx_stack

class FbApi(object):
    """
    Extension to Flask app to handle storage open/close
    
    All views that require access_token, initiate/terminate oauth shall be decorated using
    
    @app.route(your_url,methods=['GET','POST'])
    @fbapi_authentication_required
    """
    
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None


    def init_app(self, app):
        self.app = app
        self.app.config.setdefault('FBAPI_ACCESS_TOKEN_STORAGE', redis.AccessTokenStore)
        assert self.app.config.has_key('FBAPI_SCOPE')
        assert self.app.config.has_key('FBAPI_APP_URI')
        assert self.app.config.has_key('FBAPI_APP_ID')
        assert self.app.config.has_key('FBAPI_APP_SECRET')
        
        self.initialize_access_token_store()

        self.app.teardown_request(self.teardown_request)
        self.app.before_request(self.before_request)
        

    def initialize_access_token_store(self):
        self.token_storage = self.app.config['FBAPI_ACCESS_TOKEN_STORAGE'](self.app)


    def before_request(self):
        ctx = _request_ctx_stack.top
        ctx.token_storage = self.token_storage
        self.token_storage.open()

    
    def teardown_request(self, exception):
        self.token_storage.close()
        del ctx.token_storage
