from flask import Blueprint, session, render_template, redirect, url_for, request

from main import db
from config import Config
from blueprints import utils

bp = Blueprint('user', __name__, url_prefix="/user")

@bp.route("/me")
def self():
    if 'user'not in session:
        return redirect(url_for("index"))

    session_obj = utils.get_current_user()
    if session_obj is False:
        return redirect(url_for("index"))

    user = db.fetch_user("email", session_obj['email'])
    error = request.args.get("error")

    posts = db.get_posts(*user['posts'])
    for post_ in posts:
        post_["liked"] = session_obj['_id'] in post_['likes']
    
    posts = posts[::-1]

    return render_template("profile.html", user=user, me=True, error= error, posts=posts)

@bp.route("/edit", methods=["POST"])
def edit():
    if 'user'not in session:
        return redirect(url_for("index"))

    session_obj = utils.get_current_user()
    if session_obj is False:
        return redirect(url_for("index"))
    
    username = request.form.get("username")
    name = request.form.get("name")
    bio = request.form.get("bio")

    res = db.fetch_user("username", username)

    if username.strip() == "" or name.strip() == "":
        return redirect(url_for("user.self") + "?error=Username/name cannot be blank")

    if " " in username:
        return redirect(url_for("user.self") + "?error=username cannot contain spaces")

    if  res is not None and res['email'] != session_obj['email']:
        return redirect(url_for("user.self") + "?error=Username already in use")
    
    db.edit_profile(session_obj['email'], username, name, bio)
    new_tokens = utils.regen_tokens(session['user']['refresh_token'])
    session['user'] = new_tokens
    return redirect(url_for("user.self"))

@bp.route("/profile/<username>")
def profile(username):
    mode = request.args.get('mode')
    if mode == 'id':
        user = db.fetch_user('_id', username)
        if user is None:
            return redirect('/')
        return redirect(f'/user/profile/{user['username']}')
    user = db.fetch_user("username", username)
    if user is None:
        return redirect("/")

    session_obj = utils.get_current_user()
    
    posts = db.get_posts(*user['posts'])
    for post_ in posts:
        if session_obj is not False:
            post_["liked"] = session_obj['_id'] in post_['likes']
        else:
            post_["liked"] = False

    posts = posts[::-1]
    
    if 'user' not in session:
        return render_template("profile.html", me=False, user=user, posts=posts)
    if session_obj is not False and session_obj['username'] == username:
        return redirect("/user/me")
    

    return render_template("profile.html", me=False, user=user, posts=posts, current=db.fetch_user("_id", session_obj['_id']))

@bp.route("/follow", methods=["POST"])
def follow():
    if 'user' not in session:
        return "False"
    session_obj = utils.get_current_user()
    if session_obj is False:
        return 'False'
    user_id = request.args.get("user_id")
    user = db.fetch_user("_id", user_id)
    if user is None:
        return "False"
    db.toggle_follow(session_obj['_id'], user_id)
    return "True"