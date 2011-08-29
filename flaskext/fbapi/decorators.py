from fbapi.api import parse_signed_request, is_valid_signed_request, is_deauthorize_signed_request, fbapi_auth, oauth_login_url
from functools import wraps
from flask import current_app, request, session, g, render_template
from datetime import datetime



def _handle_signed_request():
    """
    parses signed_request
    """
    signed_request = request.form.get('signed_request', None)
    if signed_request: #attached to request
        current_app.logger.debug("signed_request data: '%s'" % signed_request)
        fb_signed_request = parse_signed_request(signed_request)        

        if is_valid_signed_request(fb_signed_request): #let's use only perfect signed_request
            g.fb_signed_request = fb_signed_request
            g.fb_user_id = fb_signed_request['user_id']
            session['fb_user_id'] = fb_signed_request['user_id']
            
            expires = fb_signed_request['expires'] #TODO: change date to delta seconds
            access_token = fb_signed_request['oauth_token']
            current_app.config.get("FBAPI_ACCESS_TOKEN_STORAGE", AccessTokenStore).save(g.fb_user_id, access_token, expires)
            g.fb_access_token = access_token

            session.modified = True

        elif is_deauthorize_signed_request(fb_signed_request):
            fb_user_id = fb_signed_request['user_id']
            current_app.logger.info("signed_request deauthorized user: %s" % fb_user_id)
            current_app.config.get("FBAPI_ACCESS_TOKEN_STORAGE", AccessTokenStore).deauthorize(fb_user_id)
            return oauth_redir_render() #output is ignored by facebook so sending oauth request is just a formality

        else:
            current_app.logger.error("signed_request invalid (can be HACKING attempt)")
            return oauth_redir_render()
        #TODO: deauthorized case

        
def _handle_session():
    """
    makes sure that g.fb_user_id is defined
    """
    if not hasattr(g, "fb_user_id") or not g.fb_user_id:
        g.fb_user_id = session.get("fb_user_id", None)
        if not g.fb_user_id:
            return oauth_redir_render()
    current_app.logger.debug("fb_user_id: %s" % g.fb_user_id)


def _handle_oauth_response():
    """
    requres g.fb_user_id
    we may already have access_token from signed_request but as we may get a new one during oauth than let's use the new one
    """
    error = request.args.get("error", None)
    code = request.args.get("code", None)
    if error: #potential error response from oauth flow
        error_reason = request.args.get("error_reason", None)
        error_description = request.args.get("error_description", None)
        current_app.logger.error("oauth response error\n error: '%s'\n error_reason: '%s'\nerror_desctiption: '%s'" % (error, error_reason, error_description))
        #TODO: add signal oauth_failed
        return oauth_redir_render()

    if code: #it's time to authenticate the app
        current_app.logger.debug("oauth response code: '%s'" % code)
        try:
            (access_token, expires) = fbapi_auth(code)
            current_app.logger.debug("fbapi_auth response (%s,%s)" % (access_token, expires))
            current_app.config.get("FBAPI_ACCESS_TOKEN_STORAGE", AccessTokenStore).save(g.fb_user_id, access_token, expires)
            g.fb_access_token = access_token
            
        except Exception as e:
            current_app.logger.debug("fbapi_auth exception on app authentication: %s" % e)
            return oauth_redir_render()


def _handle_storage_fallback():
    """
    makes sure that we have access_token (I.e. using session used_id get one from Storage)
    """
    if not hasattr(g, "fb_access_token") or not g.fb_access_token:
        current_app.config.get("FBAPI_ACCESS_TOKEN_STORAGE", AccessTokenStore).load(g.fb_user_id)
        return
    
    if not g.fb_access_token:
        current_app.logger.debug("redis fallback: no active access_token in storage")
        return oauth_redir_render()


def fbapi_authentication_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = _handle_signed_request()
        if result is not None:
            return result

        result = _handle_session()
        if result is not None:
            return result

        result = _handle_oauth_response()
        if result is not None:
            return result
        
        result = _handle_storage_fallback()
        if result is not None:
            return result
        
        return func(*args, **kwargs)
    return inner


def oauth_redir_render():
    """
    renders the page that requests facebook auth
    """
    return render_template(u'oauth_redir.html', fb_oauth_uri=oauth_login_url())



def retry_on_exception(func, retries):
    """
    decorator to retry existing function on any exception
    number of retries can be passed as an argument retries
    usage: api_retry(api_string,params={},retries=1)
    """
    @wraps(func)
    def retry(*args, **kwargs):
        done = False
        while retries >= 0 and not done:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                retries = retries - 1
                current_app.logger.info("Exception: %s" % e)
        raise e
    return retry


def duration_dump(func):
    """
    decorator to measure function duration
    """
    @wraps(func)
    def duration(*args, **kwargs):
        ts = datetime.now()
        result = func(*args, **kwargs)
        te = datetime.now()
        print 'timestamp end'
        print '%r (%r, %r) %s sec' % (func.__name__, args, kwargs, te - ts)
        return result

    return duration
