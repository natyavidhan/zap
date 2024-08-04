
from flask import render_template, session, redirect, url_for

from config import Config
from app.blueprints.auth import bp
from app.blueprints.auth import utils
from app import oauth
from app import db

@bp.route('/google/')
def google():
    GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
    
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route('/google/auth')
def google_auth():
    token = oauth.google.authorize_access_token()
    prof = token['userinfo']
    user = db.fetch_user("email", prof['email'])
    if user is None:
        user = db.create_user(prof['email'], prof['name'])
    tokens = utils.gen_tokens(user)
    session['user'] = tokens
    return redirect('/')

@bp.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("index"))