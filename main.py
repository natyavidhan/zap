from flask import Flask, render_template, session, url_for, redirect, request
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
    prof = token['userinfo']
    print(prof)
    user = db.fetch_user("email", prof['email'])
    if user is None:
        user = db.create_user(prof['email'], prof['name'])
    session['user'] = user
    return redirect('/')

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("index"))

@app.route("/me")
def self():
    if 'user'not in session:
        return redirect(url_for("index"))
    print(session['user'])
    user = db.fetch_user("email", session['user']['email'])
    error = request.args.get("error")

    posts = [db.get_post(post_id) for post_id in user['posts']]

    return render_template("profile.html", user=user, me=True, error= error, posts=posts)

@app.route("/edit", methods=["POST"])
def edit():
    if 'user'not in session:
        return redirect(url_for("index"))
    
    username = request.form.get("username")
    name = request.form.get("name")
    bio = request.form.get("bio")

    res = db.fetch_user("username", username)

    if username.strip() == "" or name.strip() == "":
        return redirect(url_for("self") + "?error=Username/name cannot be blank")

    if  res is not None and res['email'] != session['user']['email']:
        return redirect(url_for("self") + "?error=Username already in use")
    
    db.edit_profile(session['user']['email'], username, name, bio)
    return redirect(url_for("self"))

@app.route("/new", methods=["GET", "POST"])
def new():
    if 'user' not in session:
        return redirect(url_for(index))
    
    error = request.args.get("error")

    if request.method == "GET":
        return render_template("new.html", error=error)
    
    image   = request.files.get("image")
    caption = request.form.get("caption")
    tags    = [i.strip() for i in request.form.get("tags").split(",") if i.strip() != ""]

    print(dict(request.form))

    if image is None or caption.strip() == "":
        return redirect("/new?error=No image/caption provided")
    
    post = db.create_post(session['user']['_id'], caption, image, tags)

    return redirect(f"/post/{post['_id']}")

@app.route("/post/<post_id>")
def post(post_id):
    post = db.get_post(post_id)
    if not post:
        return redirect("/")
    user = db.fetch_user("_id", post['user'])
    return render_template("post.html", post=post, user=user)

@app.route("/comment", methods=["POST"])
def comment():
    if 'user' not in session:
        return redirect("/")
    post = request.form.get("post")
    comment = request.form.get("comment")
    res = db.add_comment(session['user']['_id'], post, comment)
    if res:
        return redirect(f"/post/{post}")
    return redirect("/")

if __name__ == "__main__":
    app.run("localhost", debug=True)