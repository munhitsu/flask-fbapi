Flask Facebook API
==================

Provides

- Server side authentication & permissions request for Facebook canvas apps
- Helper methods for FQL and graph api `flaskext.fbapi.api` `fbapi_get_*`
- Simple query profiling decorator `duration_dump`
- Function retry decorator (useful for FB API calls) `retry_on_exception`
- Application access token retrieval `fbapi_get_application_access_token`

Configuration
----
Configuration is taken from current_app.config.

	FBAPI_SCOPE - list/tuple of access privileges
	FBAPI_APP_URI - URI for our canvas app through Facebook
	FBAPI_APP_ID
	FBAPI_APP_SECRET
	FBAPI_ACCESS_TOKEN_STORAGE - defaults to redis store
	FBAPI_REDIS_DB - defaults to 1
	FBAPI_REDIS_HOST - defaults to localhost
	FBAPI_REDIS_PORT - defaults to 6379

Usage
-----
Initialization

	from flaskext.fbapi import FbApi
	
	def main():
	    app.config.from_object(config.DevelopmentConfig)
	    FbApi(app)
	    app.run(host='0.0.0.0', port=8000)

Usage. All view methods that use access_token, initiate/terminate oauth shall be wrapped with `fbapi_authentication_required` decorator.

	@app.route('/',methods=['GET','POST'])
	@fbapi_authentication_required
	def select_match():
    	return 'Select Match'

Access_token storage
------
Some backend is required to store access_tokens. At this point one is implemented: `flaskext.fbapi.storage.redis`. In case of different redis schema or a different backend please define a new class and configure FbApi.

