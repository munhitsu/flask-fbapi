from __future__ import absolute_import
from flask import _request_ctx_stack
import redis


class AccessTokenStore(object):
    """
    Decomposed layer to simplify access_token storage selection.
    Uses ctx.redis_fb as a storage
    
    object is one per Application
    context is keept in request context
    
    """

    def __init__(self, app):
        # let's use app only to get cofig and not store it
        self.config_redis_id = app.config["FBAPI_REDIS_DB"]

    def open(self):
        ctx = _request_ctx_stack.top
        ctx.redis_fb = redis.Redis(self.config_redis_id)
    
    def close(self):
        ctx = _request_ctx_stack.top
        ctx.redis_fb.close()
    
    def _get_db(self):
        ctx = _request_ctx_stack.top
        if ctx is not None:
            return ctx.sqlite3_db
    
    def save(self, user_id, access_token, expires):
        redis_fb = self._get_db()
        redis_fb.setex(user_id, access_token, expires) #set's key with expiry
        redis_fb.sadd('authorized_users', user_id) #extends users set, WARNING potential bottleneck

    def load(self, user_id):
        redis_fb = self._get_db()
        redis_fb.get(user_id)

    def deauthorize(self, user_id):
        redis_fb = self._get_db()
        redis_fb.sdel('authorized_users', user_id)
        redis_fb.delete(user_id)
        redis_fb.sadd('deauthorized_users', user_id)