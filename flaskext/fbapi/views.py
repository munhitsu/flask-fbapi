from fbapi.api import oauth_login_url
from fbapi.decorators import fbapi_authentication_required

from icanmatch import app

@app.route('/oauth/',methods=['GET','POST'])
@fbapi_authentication_required
def oauth_redirect_view():
    return render_template(u'oauth_redir.html',fb_oauth_uri=oauth_login_url())

