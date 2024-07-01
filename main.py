from flask import Flask, render_template, session, url_for, redirect
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

import os

from database import Database

load_dotenv()

app = Flask(__name__)
app.config.from_mapping(dict(os.environ))

oauth = OAuth(app)

db = Database()

@app.route("/")
def index():
    if 'user'not in session:
        return render_template("index.html")
    return render_template("home.html", user=session['user'])


@app.route('/google/')
def google():
    GOOGLE_CLIENT_ID = os.environ.get('G_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('G_CLIENT_SECRET')
    
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

@app.route('/google/auth')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    user = db.create_user(user['email'], user['name'])
    session['user'] = user
    return redirect('/')

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run("localhost", debug=True)