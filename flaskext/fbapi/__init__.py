"""
required configuration in app.config

# FBAPI_SCOPE - list/tuple of access privelages
# FBAPI_APP_URI - URI for our canvas app through facebook
# FBAPI_APP_ID
# FBAPI_APP_SECRET
# FBAPI_ACCESS_TOKEN_STORAGE - defaults to redis store
# FBAPI_REDIS_DB - defaults to 1
# FBAPI_REDIS_HOST - defaults to localhost
# FBAPI_REDIS_PORT - defaults to 6379
"""

from flaskext.fbapi.omnivore import FbApi
from flaskext.fbapi.decorators import fbapi_authentication_required, retry_on_exception, duration_dump
