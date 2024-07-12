from flask import Flask, render_template, session, url_for, redirect, request, jsonify
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
    posts = db.random_posts()
    for post_ in posts:
        post_["liked"] = session['user']['_id'] in post_['likes']
    return render_template("home.html", user=session['user'], posts = posts)


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
    user = db.fetch_user("email", session['user']['email'])
    error = request.args.get("error")

    posts = db.get_posts(*user['posts'])
    for post_ in posts:
        post_["liked"] = session['user']['_id'] in post_['likes']

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
    post = db.get_posts(post_id)
    if len(post) == 0:
        return redirect("/")
    is_json = request.args.get("json")
    user = db.fetch_user("_id", post['user'])
    liked = session['user']['_id'] in post['likes']
    if is_json:
        return jsonify({"post": post, "user": user, "liked": liked})
    return render_template("post.html", post=post, user=user, liked=liked)

@app.route("/comment", methods=["POST"])
def comment():
    if 'user' not in session:
        return "False"
    post = request.args.get("post")
    comment = request.args.get("comment")
    res = db.add_comment(session['user']['_id'], post, comment)
    if res:
        return "True"
    return "False"

@app.route("/like", methods=["POST"])
def like():
    if 'user' not in session:
        return "False"
    post = request.args.get("post")
    res = db.toggle_like(session['user']['_id'], post)
    if res:
        return "True"
    return "False"

@app.route("/profile/<user_id>")
def profile(user_id):
    user = db.fetch_user("_id", user_id)
    if user is None:
        return redirect("/")
    
    posts = db.get_posts(*user['posts'])
    for post_ in posts:
        post_["liked"] = session['user']['_id'] in post_['likes']
    
    if 'user' not in session:
        return render_template("profile.html", me=False, user=user, posts=posts)
    if session['user']['_id'] == user_id:
        return redirect("/me")
    return render_template("profile.html", me=False, user=user, posts=posts, current=db.fetch_user("_id", session['user']['_id']))

@app.route("/follow", methods=["POST"])
def follow():
    if 'user' not in session:
        return "False"
    user_id = request.args.get("user_id")
    user = db.fetch_user("_id", user_id)
    if user is None:
        return "False"
    db.toggle_follow(session['user']['_id'], user_id)
    return "True"


if __name__ == "__main__":
    app.run("localhost", debug=True)