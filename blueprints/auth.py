
from flask import Blueprint, session, redirect, url_for

from config import Config
from blueprints import utils
from main import oauth
from main import db

bp = Blueprint('auth', __name__, url_prefix="/auth")

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
    redirect_uri = url_for('auth.google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route('/google/callback')
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