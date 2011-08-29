import base64, hashlib, hmac
import simplejson as json
import urllib, urllib2
from pprint import pformat
from flask import current_app, request
from datetime import datetime


class FacebookApiException(Exception):
    def __init__(self, api_response):
        self.api_response = api_response

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, json.dumps(self.api_response))

def oauth_login_url(preserve_path=True, next_url=None):
    """
    returns oauth dialog url
    if next_url is defined than it overrides preserve_path
    if preserve_path is set to True (default) than FBAPI_APP_URI/request.path is used
    """
    FBAPI_SCOPE = current_app.config['FBAPI_SCOPE']
    FBAPI_APP_URI = current_app.config['FBAPI_APP_URI']
    FBAPI_APP_ID = current_app.config['FBAPI_APP_ID']
    
    if next_url:
        redirect_uri = next_url
    else:
        if preserve_path:
            #as the user is redirected through _top we need an url within facebook domain
            redirect_uri = FBAPI_APP_URI + request.path[1:] 
        else:
            redirect_uri = FBAPI_APP_URI
    
    fb_login_uri = "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s" % (FBAPI_APP_ID, redirect_uri)
    if FBAPI_SCOPE:
        fb_login_uri += "&scope=%s" % ",".join(FBAPI_SCOPE)
    return fb_login_uri


def base64_url_decode(data):
    data = data.encode(u'ascii')
    data += '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data)


def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip('=')


def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))


def parse_signed_request(signed_request):
    FBAPI_APP_SECRET = current_app.config['FBAPI_APP_SECRET']
    encoded_sig, payload = signed_request.split('.', 1)

    sig = base64_url_decode(encoded_sig)
    data = json.loads(base64_url_decode(payload))

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        current_app.logger.error('Unknown algorithm for signed request')
        return None
    else:
        expected_sig = hmac.new(FBAPI_APP_SECRET, msg=payload, digestmod=hashlib.sha256).digest()

    if sig == expected_sig:
        current_app.logger.debug("signed_request: %s" % pformat(data))
        return data
    else:
        current_app.logger.error('Invalid signed request received!')
        return None


def is_valid_signed_request(signed_request):
    try:
        return signed_request['user_id'] and signed_request['expires'] and signed_request['oauth_token']
    except:
        return False

def is_deauthorize_signed_request(signed_request):
    try:
        return signed_request['user_id'] and not signed_request.has_key('oauth_token')
    except:
        return False


def fbapi_get_string(path, domain=u'graph', params=None, access_token=None, encode_func=urllib.urlencode):
    """Make an API call"""
    if not params:
        params = {}
    params[u'method'] = u'GET'
    if access_token:
        params[u'access_token'] = access_token

    for k, v in params.iteritems():
        if hasattr(v, 'encode'):
            params[k] = v.encode('utf-8')

    url = u'https://' + domain + u'.facebook.com' + path
    params_encoded = encode_func(params)
    url = url + params_encoded
    current_app.logger.debug("FBAPI request: %s" % url)
    result = urllib2.urlopen(url).read()
    current_app.logger.debug("FBAPI response: %s" % result)
    
    return result


def fbapi_get_json(path, domain=u'graph', params=None, access_token=None, encode_func=urllib.urlencode):
    """Make an API call (json)"""
    if not params:
        params = {}
    if format:
        params[u'format'] = u'json'

    unparsed_result = fbapi_get_string(path, domain=domain, params=params, access_token=access_token, encode_func=encode_func)
    try:
        result = json.loads(unparsed_result)
        current_app.logger.debug("FBAPI parsed response: \n%s" % pformat(result))
    except JSONDecodeError:
        #add log request
        current_app.logger.error("FBAPI not a json response")
        raise FacebookApiException(result)
    finally:
        if u'error' in result or u'error_code' in result:
            raise FacebookApiException(result)

    return result


def fbapi_get_fql(path, params=None, access_token=None, encode_func=urllib.urlencode, format=u"json"):
    """Make an FQL API call"""
    result = fbapi_get_json(path=u"/method/fql.query?", domain=u"api", params=params, access_token=access_token, encode_func=encode_func)

    return result


def fbapi_get_fql_multiquery(params=None, access_token=None, encode_func=urllib.urlencode, format="json"):
    """Make a multiquery FQL API call"""
    result = fbapi_get_json(path=u"/method/fql.multiquery?", domain=u"api", params=params, access_token=access_token, encode_func=encode_func)

    return result


def fbapi_auth(code):
    """
    returns (access_token, expires)
    """
    FBAPI_APP_URI = current_app.config['FBAPI_APP_URI']
    FBAPI_APP_ID = current_app.config['FBAPI_APP_ID']
    FBAPI_APP_SECRET = current_app.config['FBAPI_APP_SECRET']
    
    params = {'client_id':FBAPI_APP_ID,
              'redirect_uri':FBAPI_APP_URI,
              'client_secret':FBAPI_APP_SECRET,
              'code':code}
    
    result = fbapi_get_string(path=u"/oauth/access_token?", params=params, encode_func=simple_dict_serialisation)
    pairs = result.split("&", 1)
    result_dict = {}
    for pair in pairs:
        (key, value) = pair.split("=")
        result_dict[key] = value
    
    return (result_dict["access_token"], result_dict["expires"])


def fbapi_get_application_access_token(id):
    FB_APP_SECRET = current_app.config['FB_APP_SECRET']
    token = fbapi_get_string(path=u"/oauth/access_token", params=dict(grant_type=u'client_credentials', client_id=id, client_secret=FB_APP_SECRET), domain=u'graph')
    token = token.split('=')[-1]
    if not str(id) in token:
        current_app.logger.error('Token mismatch: %s not in %s', id, token)
    return token
