from flaskext.fbapi.api import oauth_login_url
from flaskext.fbapi.decorators import fbapi_authentication_required

#TODO: not crucial but nice to have landing view
#@app.route('/oauth/',methods=['GET','POST'])
def oauth_redirect_view():
    return render_template(u'oauth_redir.html',fb_oauth_uri=oauth_login_url())

