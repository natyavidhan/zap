from flask import session, render_template, redirect, url_for, request

from app import db
from app.blueprints.user import bp

@bp.route("/me")
def self():
    if 'user'not in session:
        return redirect(url_for("index"))
    user = db.fetch_user("email", session['user']['email'])
    error = request.args.get("error")

    posts = db.get_posts(*user['posts'])
    for post_ in posts:
        post_["liked"] = session['user']['_id'] in post_['likes']

    return render_template("profile.html", user=user, me=True, error= error, posts=posts)

@bp.route("/edit", methods=["POST"])
def edit():
    if 'user'not in session:
        return redirect(url_for("index"))
    
    username = request.form.get("username")
    name = request.form.get("name")
    bio = request.form.get("bio")

    res = db.fetch_user("username", username)

    if username.strip() == "" or name.strip() == "":
        return redirect(url_for("self") + "?error=Username/name cannot be blank")

    if " " in username:
        return redirect(url_for("self") + "?error=username cannot contain spaces")

    if  res is not None and res['email'] != session['user']['email']:
        return redirect(url_for("self") + "?error=Username already in use")
    
    db.edit_profile(session['user']['email'], username, name, bio)
    _id = session['user']['_id']
    session['user'] = db.fetch_user("_id", _id)
    return redirect(url_for("self"))


@bp.route("/profile/<username>")
def profile(username):
    user = db.fetch_user("username", username)
    print(user)
    if user is None:
        return redirect("/")
    
    posts = db.get_posts(*user['posts'])
    for post_ in posts:
        if 'user' in session:
            post_["liked"] = session['user']['_id'] in post_['likes']
        else:
            post_["liked"] = False
    
    if 'user' not in session:
        return render_template("profile.html", me=False, user=user, posts=posts)
    if session['user']['username'] == username:
        return redirect("/me")
    return render_template("profile.html", me=False, user=user, posts=posts, current=db.fetch_user("_id", session['user']['_id']))

@bp.route("/follow", methods=["POST"])
def follow():
    if 'user' not in session:
        return "False"
    user_id = request.args.get("user_id")
    user = db.fetch_user("_id", user_id)
    if user is None:
        return "False"
    db.toggle_follow(session['user']['_id'], user_id)
    return "True"